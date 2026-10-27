#!/usr/bin/env python3
"""tools/pricing.json 의 값을 모든 HTML 페이지에 넣는다. 여러 번 실행해도 결과가 같다.

값은 한 곳(tools/pricing.json)에만 적는다. 페이지에는 자리 표시만 둔다.

  가격 텍스트   <span data-price="commercial.price">US$29</span>
  링크          <a data-src="commercial.checkout" href="#">구매하기</a>
  출시 여부     <p data-live-hide>출시 예정입니다</p> / <p data-live-show>지금 살 수 있습니다</p>
  Paddle 설정   <div id="paddle-config" data-env="sandbox" data-token="" data-price-license="" data-price-updates="" hidden></div>

- data-price: JSON 값이 있으면 그 값으로 바꾸고, 자리 표시였다면 class="placeholder"(주황색)를 뗀다.
             값이 null 일 때
               · commercial.* 키 — pricing.json 의 undecided 에 있는 그 언어 문장(「가격 미정」 등)을
                 넣는다. 정하지 않은 가격이 숫자로 남는 것을 막기 위해서다.
               · 그 밖의 키(seller.* 등) — 페이지에 이미 적힌 자리 표시([대표자] 등)를 그대로 둔다.
             pricing.json 에 없는 키는 그 자리를 건드리지 않고 마지막에 모아서 알린다(종료 코드 1).
- data-src:   JSON 값이 비어 있으면 href 자리 표시와 hidden 을 그대로 둔다.
              값이 채워지면 href 를 바꾸고 hidden 을 지운다(버튼이 저절로 보인다).
- data-live-hide: commercial.checkout 가 채워지면(출시) hidden 을 건다.
- data-live-show: commercial.checkout 가 채워지기 전에는 hidden 을 건다.
- data-if="키":  그 키의 값이 비어 있으면(null · "") hidden 을 걸고, 채워지면 뗀다 — 다운로드 페이지의 SHA-256 줄처럼
              값이 있을 때만 뜻이 있는 줄에 쓴다. 안의 data-price 자리는 평소 규칙대로(null 이면 「미정」 문장) 채우지만
              줄이 숨겨져 있으므로 보이지 않는다.
              키 앞에 ! 를 붙이면 반대(비어 있을 때만 보임), 공백으로 여러 개를 적으면 모두 맞을 때만 보인다 —
              data-if="commercial.download !commercial.checkout" 은 「내려받기는 열렸고 판매는 아직」 일 때만 보인다.
              data-live-hide / data-live-show 와 한 요소에 같이 쓰지 않는다(둘 다 hidden 을 정한다).
- id="paddle-config": data-env · data-token · data-price-license · data-price-updates · data-license-api 를 pricing.json 의
              paddle.environment · client_token · price_license · price_updates · license_api 로 매번 다시 쓴다
              (값을 바꿔 다시 실행해도 그대로 반영된다). 모두 공개 값이다 — API 키 · 웹훅 비밀값은
              pricing.json 에도 페이지에도 넣지 않는다.
- 루트 _redirects: 「최신 앱 받기」 고정 주소 /download/latest 를 commercial.download(지금 DMG)로 302 로 넘긴다.
              SNS 등에 한 번 올린 링크가 릴리스마다 새 이름의 DMG 를 따라간다. 이 스크립트가 매번 다시 쓴다(손으로 고치지 않는다).
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, 'tools', 'pricing.json')
MISSING = object()
missing = set()  # pricing.json 에 없는 키 (파일, 키) — 오타를 조용히 넘기지 않도록 마지막에 한 번에 알린다
PADDLE_ATTRS = (('data-env', 'environment'), ('data-token', 'client_token'),
                ('data-price-license', 'price_license'), ('data-price-updates', 'price_updates'),
                ('data-license-api', 'license_api'))


def load():
    with open(CONFIG, encoding='utf-8') as f:
        return json.load(f)


def resolve(cfg, path, where=''):
    """'commercial.price' → 값. 없는 키면 MISSING 을 돌려주고 기록해 둔다."""
    cur = cfg
    for part in path.split('.'):
        if not isinstance(cur, dict) or part not in cur:
            missing.add((where, path))
            return MISSING
        cur = cur[part]
    return cur


def set_hidden(tag, hidden):
    if hidden:
        return tag if re.search(r'<[a-z0-9]+[^>]*\shidden[\s/>]', tag) else tag[:-1].rstrip() + ' hidden>'
    return re.sub(r'\shidden(?=[\s/>])', '', tag)


def lang_of(path):
    """저장소 루트면 ko, 아니면 첫 번째 폴더 이름(en · ja · zh-Hans · zh-Hant · es)."""
    rel_path = os.path.relpath(path, ROOT)
    return rel_path.split(os.sep)[0] if os.sep in rel_path else 'ko'


def undecided(cfg, lang):
    """값이 없을 때 보여줄 각 언어 문장. 없으면 None(=페이지에 적힌 문장을 그대로 둠)."""
    return (cfg.get('undecided') or {}).get(lang)


def drop_placeholder(open_tag):
    """값이 채워진 자리에서 주황색 자리 표시 class 를 뗀다."""
    def fix(m):
        names = [c for c in m.group(1).split() if c != 'placeholder']
        return f' class="{" ".join(names)}"' if names else ''
    return re.sub(r'\sclass="([^"]*)"', fix, open_tag, count=1)


def apply_prices(html, cfg, lang, where):
    """<span data-price="키">기존 글자</span> → JSON 값으로 교체.
    null 이면 commercial.* 는 언어별 「미정」 문구, 그 밖의 키는 페이지 글자를 그대로 둔다.
    속성 안(meta description 등)에서는 {{키}} 꼴로 쓴다 — 태그를 넣을 수 없으므로."""
    todo = undecided(cfg, lang)

    def value(path):
        """(넣을 글자 또는 None, 실제 값이 있는가)"""
        val = resolve(cfg, path, where)
        if val is MISSING:
            return None, False
        if val is None:
            return (todo if path.startswith('commercial.') else None), False
        if isinstance(val, dict):  # 언어별 값 — 없는 언어는 영어, 그것도 없으면 자리 표시 유지
            val = val.get(lang, val.get('en'))
            if val is None:
                return None, False
        return str(val), True

    def sub(m):
        open_tag, path = m.group(1), m.group(2)
        text, real = value(path)
        if text is None:
            return m.group(0)
        if real:
            open_tag = drop_placeholder(open_tag)
        return open_tag + text + m.group(4)
    html = re.sub(r'(<[a-z0-9]+[^>]*\bdata-price="([^"]+)"[^>]*>)(.*?)(</[a-z0-9]+>)', sub, html, flags=re.S)
    return re.sub(r'\{\{([^}]+)\}\}', lambda m: value(m.group(1))[0] or m.group(0), html)


def apply_sources(html, cfg, where):
    """data-src="키" 를 가진 <a> 의 href 를 JSON 값으로. 값이 비면 자리 표시(#)로 되돌리고 숨긴다."""
    def sub(m):
        open_tag, path = m.group(1), m.group(2)
        val = resolve(cfg, path, where)
        if val is MISSING:
            return m.group(0)
        val = val or '#'
        open_tag = set_hidden(open_tag, val == '#')
        if re.search(r'\shref="[^"]*"', open_tag):
            return re.sub(r'\shref="[^"]*"', lambda _: f' href="{val}"', open_tag, count=1)
        return open_tag[:-1].rstrip() + f' href="{val}">'
    return re.sub(r'(<a\b[^>]*\bdata-src="([^"]+)"[^>]*>)', sub, html, flags=re.S)


def apply_launch(html, cfg, live):
    """출시 여부(commercial.checkout)에 맞춰 data-live-hide / data-live-show 요소의 hidden 을 맞춘다."""
    for attr, hide in (('data-live-hide', live), ('data-live-show', not live)):
        pat = r'<[a-z0-9]+\b[^>]*\b' + attr + r'\b[^>]*>'
        html = re.sub(pat, lambda m: set_hidden(m.group(0), hide), html)
    return html


def apply_conditions(html, cfg, where):
    """data-if="키 !키 …" 요소 — 조건이 모두 맞으면 보이고, 하나라도 어긋나면 hidden.
    키 = 그 값이 채워져 있음, !키 = 비어 있음(null · "")."""
    def sub(m):
        tag, show = m.group(0), True
        for cond in m.group(1).split():
            want = not cond.startswith('!')
            val = resolve(cfg, cond.lstrip('!'), where)
            if val is MISSING:
                return tag
            show = show and bool(val) == want
        return set_hidden(tag, not show)
    return re.sub(r'<[a-z0-9]+\b[^>]*\bdata-if="([^"]+)"[^>]*>', sub, html)


def apply_paddle(html, cfg, where):
    """id="paddle-config" 요소의 Paddle.js 설정 속성을 pricing.json 의 paddle 값으로 다시 쓴다.
    속성 값을 통째로 바꾸므로 값을 고쳐 다시 실행해도 새 값이 들어가고, 같은 값이면 바뀌지 않는다."""
    def sub(m):
        tag = m.group(0)
        for attr, key in PADDLE_ATTRS:
            val = resolve(cfg, 'paddle.' + key, where)
            val = '' if val is None or val is MISSING else str(val)
            val = val.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')
            if re.search(r'\s' + attr + r'="[^"]*"', tag):
                tag = re.sub(r'(\s' + attr + r'=)"[^"]*"', lambda a: a.group(1) + '"' + val + '"', tag, count=1)
            else:
                tag = re.sub(r'\s*(/?>)$', lambda a: f' {attr}="{val}"' + a.group(1), tag, count=1)
        return tag
    return re.sub(r'<[a-z0-9]+\b[^>]*\bid="paddle-config"[^>]*>', sub, html)


def html_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in ('.git', 'node_modules', '.wrangler')]
        for name in sorted(filenames):
            if name.endswith('.html'):
                yield os.path.join(dirpath, name)


REDIRECTS = os.path.join(ROOT, '_redirects')
LATEST_PATHS = ('/download/latest', '/download/latest/')


def write_redirects(cfg):
    """/download/latest → 지금 DMG (302 — 다음 릴리스에 바뀌므로 영구 이동이 아니다). 다운로드가 없으면 규칙을 두지 않는다."""
    target = (cfg.get('commercial', {}) or {}).get('download') or ''
    lines = ['# fill-pricing.py 가 tools/pricing.json 의 commercial.download 로 만든다 — 손으로 고치지 않는다.',
             '# 「최신 앱 받기」 고정 주소: SNS · 메일에 올린 링크가 릴리스마다 새 이름의 DMG 를 따라간다.']
    lines += [f'{path} {target} 302' for path in LATEST_PATHS] if target else []
    out = '\n'.join(lines) + '\n'
    old = open(REDIRECTS, encoding='utf-8').read() if os.path.exists(REDIRECTS) else None
    if out != old:
        open(REDIRECTS, 'w', encoding='utf-8').write(out)
        return True
    return False


def main():
    cfg = load()
    live = bool(cfg.get('commercial', {}).get('checkout'))
    changed = []
    for path in html_files():
        where = os.path.relpath(path, ROOT)
        src = open(path, encoding='utf-8').read()
        out = apply_prices(src, cfg, lang_of(path), where)
        out = apply_sources(out, cfg, where)
        out = apply_launch(out, cfg, live)
        out = apply_conditions(out, cfg, where)
        out = apply_paddle(out, cfg, where)
        if out != src:
            open(path, 'w', encoding='utf-8').write(out)
            changed.append(where)
    if write_redirects(cfg):
        changed.append('_redirects')
    print(f'pricing.json 적용 — 출시(구매 열림): {"예" if live else "아니오"} · 바뀐 파일 {len(changed)}개')
    for p in changed:
        print('  ' + p)
    if missing:
        print(f'pricing.json 에 없는 키 {len(missing)}곳 — 그 자리는 건드리지 않았습니다 (키 오타이거나, 아직 새 키로 고치지 않은 페이지):')
        for where, key in sorted(missing):
            print(f'  {where}: {key}')
        sys.exit(1)


if __name__ == '__main__':
    main()
