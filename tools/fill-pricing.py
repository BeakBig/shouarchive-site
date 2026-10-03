#!/usr/bin/env python3
"""tools/pricing.json 의 값을 모든 HTML 페이지에 넣는다. 여러 번 실행해도 결과가 같다.

값은 한 곳(tools/pricing.json)에만 적는다. 페이지에는 자리 표시만 둔다.

  가격 텍스트   <span data-price="appstore.price_now">US$2</span>
  링크          <a data-src="commercial.checkout" href="#">구독 시작</a>
  상용 판 공개  <p data-live-hide>출시 예정입니다</p> / <p data-live-show>구독 중입니다</p>

- data-price: JSON 값이 null 이면 페이지에 이미 적힌 문장(각 언어 표현)을 그대로 둔다.
             단 pricing.json 의 undecided 에 그 언어 문장이 있으면 그것을 쓴다 — 정하지 않은
             가격이 숫자로 남는 것을 막기 위해서다.
- data-src:   JSON 값이 비어 있으면 href 자리 표시와 hidden 을 그대로 둔다.
              값이 채워지면 href 를 바꾸고 hidden 을 지운다(버튼이 저절로 보인다).
- data-live-hide: commercial.checkout 가 채워지면(상용 판 공개) hidden 을 건다.
- data-live-show: commercial.checkout 가 채워지기 전에는 hidden 을 건다.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, 'tools', 'pricing.json')


def load():
    with open(CONFIG, encoding='utf-8') as f:
        return json.load(f)


def resolve(cfg, path):
    """'appstore.price_now' → 값. 없는 키면 즉시 중단(오타를 조용히 넘기지 않는다)."""
    cur = cfg
    for part in path.split('.'):
        if not isinstance(cur, dict) or part not in cur:
            sys.exit(f'pricing.json 에 없는 키입니다: {path}')
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

def apply_prices(html, cfg, lang):
    """<span data-price="키">기존 글자</span> → JSON 값으로 교체. null 이면 언어별 「미정」 문구.
    속성 안(meta description 등)에서는 {{키}} 꼴로 쓴다 — 태그를 넣을 수 없으므로."""
    todo = undecided(cfg, lang)

    def sub(m):
        open_tag, path, old = m.group(1), m.group(2), m.group(3)
        val = resolve(cfg, path)
        if val is None:
            val = todo
            if val is None:
                return m.group(0)
        return open_tag + str(val) + m.group(4)
    html = re.sub(r'(<[a-z0-9]+[^>]*\bdata-price="([^"]+)"[^>]*>)(.*?)(</[a-z0-9]+>)', sub, html, flags=re.S)
    return re.sub(r'\{\{([^}]+)\}\}', lambda m: m.group(0) if (resolve(cfg, m.group(1)) or todo) is None else str(resolve(cfg, m.group(1)) or todo), html)


def apply_sources(html, cfg):
    """data-src="키" 를 가진 <a> 의 href 를 JSON 값으로. 값이 비면 자리 표시(#)로 되돌리고 숨긴다."""
    def sub(m):
        open_tag, path = m.group(1), m.group(2)
        val = resolve(cfg, path) or '#'
        open_tag = set_hidden(open_tag, not val or val == '#')
        if re.search(r'\shref="[^"]*"', open_tag):
            return re.sub(r'\shref="[^"]*"', f' href="{val}"', open_tag, count=1)
        return open_tag[:-1].rstrip() + f' href="{val}">'
    return re.sub(r'(<a\b[^>]*\bdata-src="([^"]+)"[^>]*>)', sub, html, flags=re.S)


def apply_launch(html, cfg, live):
    """상용 판 공개 여부에 맞춰 data-live-hide / data-live-show 요소의 hidden 을 맞춘다."""
    for attr, hide in (('data-live-hide', live), ('data-live-show', not live)):
        pat = r'<[a-z0-9]+\b[^>]*\b' + attr + r'\b[^>]*>'
        html = re.sub(pat, lambda m: set_hidden(m.group(0), hide), html)
    return html


def html_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in ('.git', 'worker', 'node_modules', '.wrangler')]
        for name in sorted(filenames):
            if name.endswith('.html'):
                yield os.path.join(dirpath, name)


def main():
    cfg = load()
    live = bool(cfg.get('commercial', {}).get('checkout'))
    changed = []
    for path in html_files():
        src = open(path, encoding='utf-8').read()
        out = apply_launch(apply_sources(apply_prices(src, cfg, lang_of(path)), cfg), cfg, live)
        if out != src:
            open(path, 'w', encoding='utf-8').write(out)
            changed.append(os.path.relpath(path, ROOT))
    print(f'pricing.json 적용 — 상용 판 공개: {"예" if live else "아니오"} · 바뀐 파일 {len(changed)}개')
    for p in changed:
        print('  ' + p)


if __name__ == '__main__':
    main()