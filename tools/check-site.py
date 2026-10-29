#!/usr/bin/env python3
"""사이트를 훑어보는 점검 스크립트. 페이지를 고친 뒤 실행하세요.

```bash
python3 tools/check-site.py
```

확인하는 것
  1. 6개 언어 × 12개 페이지가 모두 있는가 (+ 루트 404.html)
  2. 한국어 원본과 구조가 같은가 — 태그 순서, 속성 이름, 값이 그대로여야 하는 속성
     (href · src · id · class · data-* · hidden 등. canonical 의 href 는 언어마다 다르므로 비교하지 않음)
  3. 번역이 밀리지 않았는가 — 남은 한글, 그리고 언어마다 함께 있으면 안 되는 문자 체계
     (언어 전환 메뉴 · 언어 이름은 제외)
  4. data-price 키가 pricing.json 에 있는가, 값이 없는(null) 자리에 숫자가 그대로 남아 있지 않은가
     (예상해 둔 금액이 페이지에 노출되지 않게 하는 검사 — commercial.* 는 「미정」 문장이어야 하고,
     seller.* 같은 다른 키는 [대표자] 처럼 숫자 없는 자리 표시면 됩니다)
     그리고 checkout.html 의 Paddle 설정(#paddle-config)이 pricing.json 과 같은가
  5. 내부 링크가 실제 파일을 가리키는가 — 링크는 확장자 없이 쓴다(`pricing` → pricing.html, `./` · `en/` → index.html).
     `.html` 로 끝나는 사이트 안 링크는 문제로 잡습니다. 현재 페이지 링크(aria-current)가 자기 자신을 가리키는가
  6. CSS 에 [hidden] 을 강제하는 규칙이 있는가 — .btn 처럼 display 를 정하는 요소에 달린
     hidden 이 동작하려면 !important 가 필요합니다
  7. 25 MiB 를 넘는 파일이 없는가 (Workers 정적 파일 한도 · README 「주의」 절)
  8. 인라인 <script> 가 없는가 — 루트 _headers 의 CSP(script-src 'self')가 막습니다. 스크립트는 assets/ 파일로만
  9. 루트 _headers · 404.html 이 있고 .assetsignore 가 _headers 를 빼지 않는가

경고(종료 코드를 바꾸지 않음)
  - pricing.json 의 paddle.environment 가 sandbox 이거나 client_token 이 test_ 로 시작하면 — 공개 결제 페이지가
    샌드박스라는 뜻. 출시 전에 production 토큰으로 바꾸고 서버의 샌드박스 라이선스 · 결제 · Mac 기록을 정리할 것
    (README 「출시 체크리스트」).

문제는 모두 모아서 마지막에 한 번에 보고합니다. 코드 1 이 나오면 문제가 있다는 뜻입니다.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = ['ko', 'en', 'ja', 'zh-Hans', 'zh-Hant', 'es']
PAGES = ['index.html', 'pricing.html', 'download.html', 'support.html', 'privacy.html', 'terms.html', 'refund.html', 'changelog.html', 'checkout.html',
         'activate.html', 'license.html', 'rotate.html', 'erase.html', 'billing.html']
ROOT_ONLY = ['404.html']  # 언어판이 없는 루트 페이지 — 링크 · 인라인 스크립트만 본다
MAX_BYTES = 25 * 1024 * 1024  # Workers 정적 파일 한도
KEEP_VALUE = {'href', 'src', 'id', 'class', 'data-price', 'data-src', 'data-live-hide', 'data-live-show', 'data-if', 'data-page'}
TAG_RE = re.compile(r'<([a-z0-9]+)((?:\s+[a-z0-9-]+(?:="[^"]*")?)*)\s*/?>')
ATTR_RE = re.compile(r'([a-z0-9-]+)(?:="([^"]*)")?')
HANGUL_RE = re.compile(r'[가-힣ㄱ-ㆎ]')
KANA_RE = re.compile(r'[぀-ヿ]')
HAN_RE = re.compile(r'[一-鿿㐀-䶿]')
MIXED_OK = {  # 언어마다 허용하지 않는 문자 체계 — 한자를 쓰는 언어가 두 개라 언어별로 지정
  'ko': (KANA_RE, HAN_RE),
  'en': (HANGUL_RE, KANA_RE, HAN_RE),
  'es': (HANGUL_RE, KANA_RE, HAN_RE),
  'ja': (HANGUL_RE,),
  'zh-Hans': (HANGUL_RE, KANA_RE),
  'zh-Hant': (HANGUL_RE, KANA_RE),
}
LANG_NAMES = ['한국어', 'English', '日本語', '简体中文', '繁體中文', 'Español', 'Korean', 'Chinese', 'Japonese', 'Spanish', '한국어']

problems = []
warnings = []

def report(kind, path, detail):
    problems.append(f'[{kind}] {os.path.relpath(path, ROOT) if os.path.isabs(path) else path} — {detail}')

def warn(kind, path, detail):
    warnings.append(f'[{kind}] {path} — {detail}')

def path_for(lang, page):
    return os.path.join(ROOT, page if lang == 'ko' else f'{lang}/{page}')

def skeleton(html):
    """(태그 이름, 값이 그대로여야 하는 속성들의 쌍) 목록 — 번역과 무관한 구조만 뽑는다.

    언어 폴더의 `../` · `./` 접두사는 지웁니다(한국어 원본과 같은 값으로 맞추기 위함).
    canonical 의 href 는 언어마다 다른 절대 주소라 값을 비교하지 않습니다."""
    html = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    out = []
    for tag, attrs in TAG_RE.findall(html):
        pairs = []
        canonical = 'rel="canonical"' in attrs
        for name, value in ATTR_RE.findall(attrs):
            if name == 'hidden':
                pairs.append(('hidden', ''))
            elif name in KEEP_VALUE:
                if name == 'href' and canonical:
                    pairs.append((name, 'CANONICAL'))
                    continue
                value = re.sub(r'^(\.\./|\./)', '', value or '')
                value = re.sub(r'^(assets/screenshots)/[^/]+/', r'\1LANG/', value)  # 스크린샷 폴더는 언어마다 다름
                if value.startswith('mailto:'):  # 제목(subject)은 언어마다 다를 수 있음
                    value = value.split('?')[0]
                pairs.append((name, value))
        out.append((tag, tuple(pairs)))
    return out

def resolve_local(p, href):
    """사이트 안 상대 링크가 가리키는 실제 파일. 확장자 없는 주소를 Cloudflare 와 같은 규칙으로 푼다 —
    `pricing` → pricing.html, `./` · `en/` · `` → 그 폴더의 index.html. 없으면 None."""
    path = href.split('#')[0]
    base = os.path.dirname(p)
    if path in ('', '.', './') or path.endswith('/'):
        target = os.path.normpath(os.path.join(base, path, 'index.html'))
        return target if os.path.exists(target) else None
    target = os.path.normpath(os.path.join(base, path))
    if os.path.isdir(target):
        target = os.path.join(target, 'index.html')
    for candidate in (target, target + '.html'):
        if os.path.isfile(candidate):
            return candidate
    return None

def visible_text(html):
    """번역이 필요 없는 부분(언어 선택 목록 · 「한국어」 라는 언어 이름)을 뺀 눈에 보이는 글자."""
    html = re.sub(r'<span class="footer-langs">.*?</span>', '', html, flags=re.S)
    html = re.sub(r'<select[^>]*>.*?</select>', '', html, flags=re.S)
    return re.sub(r'<[^>]+>', ' ', html).replace('한국어', '')  # 언어 목록에는 원래 한국어가 들어 있음

def check_structure(lang, page):
    p = path_for(lang, page)
    ko = skeleton(open(path_for('ko', page), encoding='utf-8').read())
    other = skeleton(open(p, encoding='utf-8').read())
    shown = 0
    if len(ko) != len(other):
        report('구조', p, f'태그 수가 다릅니다 (한국어 {len(ko)} vs 여기 {len(other)})')
    for i, (a, b) in enumerate(zip(ko, other)):
        if a != b and shown < 5:
            report('구조', p, f'{i+1}번째 태그 — 한국어 {a} vs 여기 {b}')
            shown += 1

def check_hangul(lang, page):
    found = sorted(set(HANGUL_RE.findall(visible_text(open(path_for(lang, page), encoding='utf-8').read()))))
    if found:
        report('번역', path_for(lang, page), f'번역되지 않은 한글이 남았습니다: {"".join(found)[:40]}')

def check_links(p):
    """사이트 안 링크가 실제 파일을 가리키는가. 사이트 안 .html 링크는 확장자 없는 주소로 바꿔야 한다
    (Cloudflare 가 .html 주소를 307 로 돌리고, canonical · hreflang 도 확장자가 없다)."""
    html = open(p, encoding='utf-8').read()
    for href in sorted(set(re.findall(r'(?<![\w-])(?:href|src)="([^"]+)"', html))):
        if href.startswith(('http://', 'https://', 'mailto:', 'tel:', '#', 'data:')):
            continue
        if href.split('#')[0].endswith('.html'):
            report('링크', p, f'사이트 안 링크는 확장자 없이 씁니다 (.html 을 떼세요): {href}')
            continue
        if resolve_local(p, href) is None:
            report('링크', p, f'대상이 없습니다: {href}')
    for href in sorted(set(re.findall(r'<option value="([^"]+)"', html))):
        if resolve_local(p, href) is None:
            report('링크', p, f'언어 선택 대상이 없습니다: {href}')

def check_current_page(lang, page):
    """aria-current="page" 링크는 자기 자신을 가리켜야 한다 (../ 로 잘못 가면 한국어판으로 튄다)."""
    p = path_for(lang, page)
    for href in re.findall(r'<a href="([^"]+)" aria-current="page"', open(p, encoding='utf-8').read()):
        if href.startswith(('http', 'mailto:', '#')):
            continue
        target = resolve_local(p, href)
        if target is None or os.path.normpath(target) != os.path.normpath(p):
            report('현재 페이지', p, f'aria-current 링크가 다른 파일을 가리킵니다: {href}')

def check_inline_script(p):
    """인라인 <script>…</script> 는 _headers 의 CSP(script-src 'self')가 막는다 — src 가 있는 것만 허용."""
    html = re.sub(r'<!--.*?-->', '', open(p, encoding='utf-8').read(), flags=re.S)
    for m in re.finditer(r'<script\b([^>]*)>', html):
        if not re.search(r'\bsrc="', m.group(1)):
            report('CSP', p, '인라인 <script> 가 있습니다 — assets/ 의 파일로 빼세요 (_headers 의 script-src 가 막습니다)')
            break

def check_canonical(lang, page):
    """canonical 이 확장자 없는 절대 주소인가 — localize-nav.py 가 만든다."""
    p = path_for(lang, page)
    m = re.search(r'<link rel="canonical" href="([^"]+)">', open(p, encoding='utf-8').read())
    if not m:
        report('canonical', p, 'canonical 링크가 없습니다 — python3 tools/localize-nav.py 를 실행하세요')
    elif m.group(1).endswith('.html') or not m.group(1).startswith('https://'):
        report('canonical', p, f'canonical 은 확장자 없는 절대 주소여야 합니다: {m.group(1)}')

def check_mixed_script(lang, page):
    """번역이 밀려 다른 언어 문자가 남았는지 — 언어 전환 메뉴와 지원 언어 목록은 제외."""
    p = path_for(lang, page)
    text = visible_text(open(p, encoding='utf-8').read())
    for name in LANG_NAMES:
        text = text.replace(name, ' ')
    for rx in MIXED_OK[lang]:
        found = sorted(set(rx.findall(text)))
        if found:
            report('문자 섞임', p, f'함께 있으면 안 되는 문자가 있습니다: {"".join(found)[:30]}')

def check_undecided_price(lang, page):
    """data-price 키가 pricing.json 에 있는지, 값이 null 인 자리에 숫자(금액)가 그대로 남아 있지 않은지."""
    cfg = json.load(open(os.path.join(ROOT, 'tools', 'pricing.json'), encoding='utf-8'))
    want = (cfg.get('undecided') or {}).get(lang)
    p = path_for(lang, page)
    for key, text in re.findall(r'<span\b[^>]*\bdata-price="([^"]+)"[^>]*>(.*?)</span>', open(p, encoding='utf-8').read(), flags=re.S):
        cur, found = cfg, True
        for part in key.split('.'):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                found = False
                break
        if not found:
            report('가격', p, f'{key} 는 pricing.json 에 없는 키입니다')
            continue
        if cur is None and re.search(r'\d|US\$|€|£|¥|￥|\$', text):
            report('가격', p, f'{key} 는 pricing.json 에 값이 없는데 페이지에 숫자가 있습니다: {text.strip()[:30]}')
        if cur is None and want and key.startswith('commercial.') and text.strip() != want:
            report('가격', p, f'{key} 자리 문장이 「{want}」 이어야 합니다: {text.strip()[:30]}')

def check_paddle_config(lang, page):
    """#paddle-config 의 속성이 pricing.json 의 paddle 값과 같은지 (fill-pricing.py 를 잊지 않았는지)."""
    p = path_for(lang, page)
    m = re.search(r'<[a-z0-9]+\b[^>]*\bid="paddle-config"[^>]*>', open(p, encoding='utf-8').read())
    if not m:
        if page == 'checkout.html':
            report('결제', p, 'id="paddle-config" 요소가 없습니다')
        return
    paddle = json.load(open(os.path.join(ROOT, 'tools', 'pricing.json'), encoding='utf-8')).get('paddle') or {}
    for attr, key in (('data-env', 'environment'), ('data-token', 'client_token'),
                      ('data-price-license', 'price_license'), ('data-price-updates', 'price_updates'),
                      ('data-license-api', 'license_api')):
        got = re.search(r'\s' + attr + r'="([^"]*)"', m.group(0))
        if not got or got.group(1) != str(paddle.get(key) or ''):
            report('결제', p, f'{attr} 가 pricing.json 의 paddle.{key} 와 다릅니다 — python3 tools/fill-pricing.py 를 실행하세요')

def check_hidden_rule():
    """.btn 처럼 display 를 정하는 요소에 달린 hidden 이 동작하려면 CSS 강제 규칙이 있어야 합니다."""
    css = open(os.path.join(ROOT, 'assets', 'style.css'), encoding='utf-8').read()
    if not re.search(r'\[hidden\][^}]*display:\s*none\s*!important', css):
        report('CSS', 'assets/style.css', '[hidden] 을 display:none !important 로 강제하는 규칙이 없습니다 (.btn 의 display 가 기본 숨김이를 덮어씁니다)')

def check_sizes():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in ('.git', 'node_modules')]
        for name in filenames:
            f = os.path.join(dirpath, name)
            size = os.path.getsize(f)
            if size > MAX_BYTES:
                report('용량', f, f'{size / 1024 / 1024:.1f} MiB — 25 MiB 한도를 넘습니다')

def check_deploy_files():
    """루트 _headers(보안 헤더 · CSP) · 404.html 이 있고, .assetsignore 가 _headers 를 빼지 않는가."""
    headers = os.path.join(ROOT, '_headers')
    if not os.path.exists(headers):
        report('배포', '_headers', '없습니다 — 보안 헤더 · CSP 규칙 파일 (README 「구성」)')
    elif 'Content-Security-Policy:' not in open(headers, encoding='utf-8').read():
        report('배포', '_headers', 'Content-Security-Policy 줄이 없습니다')
    ignore = os.path.join(ROOT, '.assetsignore')
    if os.path.exists(ignore):
        lines = [l.strip() for l in open(ignore, encoding='utf-8') if l.strip() and not l.startswith('#')]
        if '_headers' in lines or '404.html' in lines:
            report('배포', '.assetsignore', '_headers · 404.html 은 빼면 안 됩니다 (Worker 가 읽어야 합니다)')
    for name in ROOT_ONLY:
        p = os.path.join(ROOT, name)
        if not os.path.exists(p):
            report('파일', p, '없습니다 (Cloudflare 가 없는 주소에 돌려주는 페이지)')
            continue
        check_links(p)
        check_inline_script(p)

def check_sandbox_warning():
    """공개 결제 페이지가 Paddle 샌드박스를 가리키면 경고 — 출시 전에 꼭 바꿔야 하지만 개발 중에는 정상이므로 종료 코드는 그대로."""
    paddle = json.load(open(os.path.join(ROOT, 'tools', 'pricing.json'), encoding='utf-8')).get('paddle') or {}
    if paddle.get('environment') == 'sandbox' or str(paddle.get('client_token') or '').startswith('test_'):
        warn('결제', 'tools/pricing.json', '공개 결제 페이지가 샌드박스입니다(paddle.environment=sandbox 또는 client_token 이 test_). '
             '출시 전에 production 토큰으로 바꾸고 서버의 샌드박스 라이선스 · 결제 · Mac 기록을 정리할 것 — README 「출시 체크리스트」')

def check_release_notes(feed):
    """news.json 의 ShouArchive 업데이트 내역이 변경 사항 페이지(6개 언어)와 같은지 — 원본은 changelog.html, 맞추기는 tools/sync-releases.py"""
    import importlib.util
    sys.dont_write_bytecode = True  # tools/__pycache__ 를 남기지 않는다
    spec = importlib.util.spec_from_file_location('sync_releases', os.path.join(ROOT, 'tools', 'sync-releases.py'))
    sync = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sync)
    try:
        want = sync.synced(feed)
    except SystemExit as error:
        report('소식', 'changelog.html', str(error))
        return
    if want != feed:
        report('소식', 'news.json', 'ShouArchive 업데이트 내역이 변경 사항 페이지와 다릅니다 — python3 tools/sync-releases.py')

def check_news():
    """앱 「소식」 탭의 news.json — 앱(NewsFeed.decode)이 빼 버릴 항목이 없게: id · 날짜 · https 링크 · 6개 언어 제목 · 요약, 같은 id 없음."""
    path = os.path.join(ROOT, 'news.json')
    if not os.path.exists(path):
        report('소식', 'news.json', '없습니다 — 앱의 소식 탭이 이 주소를 받습니다 (README 「소식 목록」)')
        return
    try:
        feed = json.load(open(path, encoding='utf-8'))
    except ValueError as error:
        report('소식', 'news.json', f'JSON 이 아닙니다: {error}')
        return
    if feed.get('version', 1) != 1:
        report('소식', 'news.json', f'version 은 1 이어야 합니다 (앱이 읽는 형식): {feed.get("version")}')
    seen = set()
    date = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    for i, item in enumerate(feed.get('items') or []):
        where = f'items[{i}] {item.get("id", "")}'
        if not item.get('id') or item['id'] in seen:
            report('소식', 'news.json', f'{where} — id 가 비었거나 겹칩니다')
        seen.add(item.get('id'))
        if not date.match(str(item.get('published') or '')):
            report('소식', 'news.json', f'{where} — published 는 YYYY-MM-DD')
        if item.get('deadline') is not None and not date.match(str(item['deadline'])):
            report('소식', 'news.json', f'{where} — deadline 은 YYYY-MM-DD 또는 null')
        if not str(item.get('url') or '').startswith('https://'):
            report('소식', 'news.json', f'{where} — url 은 https:// 로 시작해야 합니다 (앱이 다른 링크는 뺍니다)')
        for lang, link in (item.get('urls') or {}).items():
            if lang not in LANGS or lang == 'en':
                report('소식', 'news.json', f'{where} — urls 의 언어 {lang} 는 ko · ja · zh-Hans · zh-Hant · es 중 하나 (영어는 url)')
            if not str(link or '').startswith('https://'):
                report('소식', 'news.json', f'{where} — urls.{lang} 은 https:// 로 시작해야 합니다')
        platforms = set(item.get('platforms') or [])
        if not platforms <= {'ios', 'android', 'shouarchive'}:
            report('소식', 'news.json', f'{where} — platforms 는 ios · android · shouarchive 만 (비우면 양쪽)')
        if 'shouarchive' in platforms and not re.match(r'^\d+(\.\d+)*$', str(item.get('version') or '')):
            report('소식', 'news.json', f'{where} — ShouArchive 업데이트 내역은 version(「1.0.3」) 이 있어야 합니다')
        for field in ('title', 'summary'):
            texts = item.get(field) or {}
            missing = [lang for lang in LANGS if not str(texts.get(lang) or '').strip()]
            if missing:
                report('소식', 'news.json', f'{where} — {field} 에 빠진 언어: {", ".join(missing)}')
    check_release_notes(feed)

for page in PAGES:
    if not os.path.exists(path_for('ko', page)):
        report('파일', path_for('ko', page), '없습니다')
        continue
    for lang in LANGS:
        if not os.path.exists(path_for(lang, page)):
            report('파일', path_for(lang, page), '없습니다 (6개 언어 모두 있어야 합니다)')
            continue
        if lang != 'ko':
            check_structure(lang, page)
            check_hangul(lang, page)
            check_mixed_script(lang, page)
        check_undecided_price(lang, page)
        check_paddle_config(lang, page)
        check_links(path_for(lang, page))
        check_current_page(lang, page)
        check_inline_script(path_for(lang, page))
        check_canonical(lang, page)
check_hidden_rule()
check_sizes()
check_deploy_files()
check_sandbox_warning()
check_news()

for line in warnings:
    print('경고', line)
if problems:
    print(f'문제 {len(problems)}건')
    for line in problems:
        print(' ', line)
    sys.exit(1)
print(f'이상 없음 — {len(LANGS)}개 언어 × {len(PAGES)}개 페이지 + {" · ".join(ROOT_ONLY)}, 링크 · 번역 · 구조 · CSP · 용량 모두 통과'
      + (f' (경고 {len(warnings)}건)' if warnings else ''))