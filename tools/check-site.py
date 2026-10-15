#!/usr/bin/env python3
"""사이트를 훑어보는 점검 스크립트. 페이지를 고친 뒤 실행하세요.

```bash
python3 tools/check-site.py
```

확인하는 것
  1. 6개 언어 × 8개 페이지가 모두 있는가
  2. 한국어 원본과 구조가 같은가 — 태그 순서, 속성 이름, 값이 그대로여야 하는 속성
     (href · src · id · class · data-* · hidden 등)
  3. 번역이 밀리지 않았는가 — 남은 한글, 그리고 언어마다 함께 있으면 안 되는 문자 체계
     (언어 전환 메뉴 · 언어 이름은 제외)
  4. data-price 키가 pricing.json 에 있는가, 값이 없는(null) 자리에 숫자가 그대로 남아 있지 않은가
     (예상해 둔 금액이 페이지에 노출되지 않게 하는 검사 — commercial.* 는 「미정」 문장이어야 하고,
     seller.* 같은 다른 키는 [대표자] 처럼 숫자 없는 자리 표시면 됩니다)
     그리고 checkout.html 의 Paddle 설정(#paddle-config)이 pricing.json 과 같은가
  5. 내부 링크가 실제 파일을 가리키는가, 현재 페이지 링크가 자기 자신을 가리키는가
  6. CSS 에 [hidden] 을 강제하는 규칙이 있는가 — .btn 처럼 display 를 정하는 요소에 달린
     hidden 이 동작하려면 !important 가 필요합니다
  7. 25 MiB 를 넘는 파일이 없는가 (Workers 정적 파일 한도 · README 「주의」 절)

문제는 모두 모아서 마지막에 한 번에 보고합니다. 코드 1 이 나오면 문제가 있다는 뜻입니다.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = ['ko', 'en', 'ja', 'zh-Hans', 'zh-Hant', 'es']
PAGES = ['index.html', 'pricing.html', 'download.html', 'support.html', 'privacy.html', 'terms.html', 'refund.html', 'checkout.html']
MAX_BYTES = 25 * 1024 * 1024  # Workers 정적 파일 한도
KEEP_VALUE = {'href', 'src', 'id', 'class', 'data-price', 'data-src', 'data-live-hide', 'data-live-show'}
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

def report(kind, path, detail):
    problems.append(f'[{kind}] {os.path.relpath(path, ROOT) if os.path.isabs(path) else path} — {detail}')

def path_for(lang, page):
    return os.path.join(ROOT, page if lang == 'ko' else f'{lang}/{page}')

def skeleton(html):
    """(태그 이름, 값이 그대로여야 하는 속성들의 쌍) 목록 — 번역과 무관한 구조만 뽑는다.

    언어 폴더의 `../` 접두사는 지웁니다(한국어 원본과 같은 값으로 맞추기 위함)."""
    html = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    out = []
    for tag, attrs in TAG_RE.findall(html):
        pairs = []
        for name, value in ATTR_RE.findall(attrs):
            if name == 'hidden':
                pairs.append(('hidden', ''))
            elif name in KEEP_VALUE:
                value = re.sub(r'^\.\./', '', value or '')
                value = re.sub(r'^(assets/screenshots)/[^/]+/', r'\1LANG/', value)  # 스크린샷 폴더는 언어마다 다름
                if value.startswith('mailto:'):  # 제목(subject)은 언어마다 다를 수 있음
                    value = value.split('?')[0]
                pairs.append((name, value))
        out.append((tag, tuple(pairs)))
    return out

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

def check_links(lang, page):
    p = path_for(lang, page)
    missing = []
    for href in sorted(set(re.findall(r'href="([^"]+)"', open(p, encoding='utf-8').read()))):
        if href.startswith(('http://', 'https://', 'mailto:', 'tel:', '#', 'data:')):
            continue
        target = os.path.normpath(os.path.join(os.path.dirname(p), href.split('#')[0]))
        if not os.path.exists(target):
            missing.append(href)
    for href in missing:
        report('링크', p, f'대상이 없습니다: {href}')

def check_current_page(lang, page):
    """aria-current="page" 링크는 자기 자신을 가리켜야 한다 (../ 로 잘못 가면 한국어판으로 튄다)."""
    p = path_for(lang, page)
    for href in re.findall(r'<a href="([^"]+)" aria-current="page"', open(p, encoding='utf-8').read()):
        if href.startswith(('http', 'mailto:', '#')):
            continue
        target = os.path.normpath(os.path.join(os.path.dirname(p), href.split('#')[0]))
        if target != os.path.normpath(p):
            report('현재 페이지', p, f'aria-current 링크가 다른 파일을 가리킵니다: {href}')

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
                      ('data-price-license', 'price_license'), ('data-price-updates', 'price_updates')):
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
        check_links(lang, page)
        check_current_page(lang, page)
check_hidden_rule()
check_sizes()

if problems:
    print(f'문제 {len(problems)}건')
    for line in problems:
        print(' ', line)
    sys.exit(1)
print(f'이상 없음 — {len(LANGS)}개 언어 × {len(PAGES)}개 페이지, 링크 · 번역 · 구조 · 용량 모두 통과')