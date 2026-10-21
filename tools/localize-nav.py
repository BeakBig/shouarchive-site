#!/usr/bin/env python3
"""모든 언어 페이지에 6개 언어 전환 메뉴(헤더 select · 푸터 링크)와 canonical · hreflang 링크를 넣고,
헤더 · 푸터 메뉴 링크를 표(TXT)에서 고쳐 쓴다. 여러 번 실행해도 결과가 같다.

주소는 모두 확장자 없이 쓴다 (2026-10-20) — Cloudflare 가 /support 를 support.html 로 서빙하고 .html 주소는 307 로
확장자 없는 주소로 보내므로, 사이트 안 링크 · canonical · hreflang 도 그 모양으로 통일한다.
  - 사이트 안 상대 링크: `pricing`, `./`(홈), `./#features`, 다른 언어는 `../en/pricing` · `../en/`
  - canonical · hreflang: 절대 주소 https://shouarchive.beakbig.com/en/pricing (한국어는 /pricing, 홈은 /en/ · /)
  - 언어 전환 스크립트는 인라인 대신 assets/nav.js (루트 _headers 의 CSP 가 인라인 스크립트를 막는다)
  - 방문 통계(Cloudflare Web Analytics) 비컨은 pricing.json 의 analytics.cf_beacon_token 이 있을 때만 넣는다 (2026-10-21)

페이지를 고치거나 언어를 더하면 다시 실행한다. 새 페이지를 만들면 아래 PAGES 에 추가한다.
"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Cloudflare Web Analytics 사이트 토큰 (tools/pricing.json 의 analytics.cf_beacon_token — 비면 비컨을 넣지 않는다)
import json
BEACON_TOKEN = json.load(open(os.path.join(ROOT, 'tools', 'pricing.json'), encoding='utf-8')).get('analytics', {}).get('cf_beacon_token', '').strip()
SITE = 'https://shouarchive.beakbig.com'
LANGS = [('ko', '한국어'), ('en', 'English'), ('ja', '日本語'), ('zh-Hans', '简体中文'), ('zh-Hant', '繁體中文'), ('es', 'Español')]
PAGES = ['index.html', 'pricing.html', 'download.html', 'support.html', 'privacy.html', 'terms.html', 'refund.html', 'checkout.html',
         'activate.html', 'license.html', 'rotate.html', 'erase.html']
HEADER_LINKS = [('features', 'index.html', '#features'), ('pricing', 'pricing.html', ''), ('download', 'download.html', ''), ('support', 'support.html', ''), ('privacy', 'privacy.html', '')]
FOOTER_LINKS = [('home', 'index.html', ''), ('pricing', 'pricing.html', ''), ('download', 'download.html', ''), ('support', 'support.html', ''), ('privacy_doc', 'privacy.html', ''), ('terms', 'terms.html', ''), ('refund', 'refund.html', '')]

# 페이지마다 쓰는 문구. lang: 셀렉트 옆 보조 문구, main/footer: 내비게이션 aria-label, 나머지: 링크 글자
TXT = {
  'ko': {'lang': '언어', 'main': '주 메뉴', 'footer': '바닥 메뉴', 'features': '기능', 'pricing': '가격', 'download': '다운로드', 'support': '지원', 'privacy': '개인정보', 'home': '홈', 'privacy_doc': '개인정보 처리방침', 'terms': '이용약관', 'refund': '환불 정책'},
  'en': {'lang': 'Language', 'main': 'Main', 'footer': 'Footer', 'features': 'Features', 'pricing': 'Pricing', 'download': 'Download', 'support': 'Support', 'privacy': 'Privacy', 'home': 'Home', 'privacy_doc': 'Privacy Policy', 'terms': 'Terms of Service', 'refund': 'Refund Policy'},
  'ja': {'lang': '言語', 'main': 'メイン', 'footer': 'フッター', 'features': '機能', 'pricing': '価格', 'download': 'ダウンロード', 'support': 'サポート', 'privacy': 'プライバシー', 'home': 'ホーム', 'privacy_doc': 'プライバシーポリシー', 'terms': '利用規約', 'refund': '返金ポリシー'},
  'zh-Hans': {'lang': '语言', 'main': '主导航', 'footer': '页脚', 'features': '功能', 'pricing': '价格', 'download': '下载', 'support': '支持', 'privacy': '隐私', 'home': '首页', 'privacy_doc': '隐私政策', 'terms': '服务条款', 'refund': '退款政策'},
  'zh-Hant': {'lang': '語言', 'main': '主要導覽', 'footer': '頁尾', 'features': '功能', 'pricing': '價格', 'download': '下載', 'support': '支援', 'privacy': '隱私權', 'home': '首頁', 'privacy_doc': '隱私權政策', 'terms': '服務條款', 'refund': '退款政策'},
  'es': {'lang': 'Idioma', 'main': 'Principal', 'footer': 'Pie de página', 'features': 'Funciones', 'pricing': 'Precios', 'download': 'Descargas', 'support': 'Soporte', 'privacy': 'Privacidad', 'home': 'Inicio', 'privacy_doc': 'Política de privacidad', 'terms': 'Términos del servicio', 'refund': 'Política de reembolso'},
}

def page_path(lang, page):  # 저장소 루트 기준 파일 경로
    return page if lang == 'ko' else f'{lang}/{page}'

def clean_name(page):  # 'pricing.html' → 'pricing', 'index.html' → '' (폴더 주소)
    name = page[:-len('.html')] if page.endswith('.html') else page
    return '' if name == 'index' else name

def url_of(lang, page):  # 사이트 루트 기준 확장자 없는 주소: '' · 'pricing' · 'en/' · 'en/pricing'
    return clean_name(page) if lang == 'ko' else f'{lang}/{clean_name(page)}'

def absolute(lang, page):  # canonical · hreflang 에 쓰는 절대 주소
    return f'{SITE}/{url_of(lang, page)}'

def rel(from_lang, to_lang, page):  # from 페이지에서 to 페이지로 가는 상대 주소 (확장자 없음)
    up = '' if from_lang == 'ko' else '../'
    return (up + url_of(to_lang, page)) or './'

def lang_switch(lang, page):
    t = TXT[lang]
    opts = ''.join(f'<option value="{rel(lang, l, page)}"{" selected" if l == lang else ""}>{name}</option>' for l, name in LANGS)
    return f'<label class="lang-switch"><span class="visually-hidden">{t["lang"]}</span><select class="lang-select" aria-label="{t["lang"]}">{opts}</select></label>'

def cur(l, lang):  # f-string 안의 식에 따옴표를 넣지 않도록 따로 뺀다 (파이썬 버전마다 허용 여부가 다르다)
    return ' aria-current="page"' if l == lang else ''

def footer_langs(lang, page):
    links = ' '.join(f'<a href="{rel(lang, l, page)}" lang="{l}" hreflang="{l}"{cur(l, lang)}>{name}</a>' for l, name in LANGS)
    return f'<span class="footer-langs">{links}</span>'

def menu_links(lang, page, links):
    out = []
    for key, target, frag in links:
        if target == page:  # 자기 페이지 앵커는 파일 이름 없이, 자기 파일은 같은 폴더의 확장자 없는 주소로
            href = frag or (clean_name(target) or './')
        else:  # 메뉴는 늘 같은 언어 폴더 안의 페이지로 간다 (언어를 바꾸는 건 언어 선택만)
            href = (clean_name(target) or './') + frag
        cur = ' aria-current="page"' if target == page else ''
        out.append(f'<a href="{href}"{cur}>{TXT[lang][key]}</a>')
    return out

def process(lang, page):
    p = os.path.join(ROOT, page_path(lang, page))
    if not os.path.exists(p): return False
    s = open(p, encoding='utf-8').read()
    up = '' if lang == 'ko' else '../'
    # 1) canonical + hreflang 링크 묶음 교체 (절대 주소 · 확장자 없음)
    s = re.sub(r'(?:[ \t]*<link rel="(?:alternate" hreflang="[^"]+|canonical)" href="[^"]+">\n)+', '', s)
    links = f'  <link rel="canonical" href="{absolute(lang, page)}">\n'
    links += ''.join(f'  <link rel="alternate" hreflang="{l}" href="{absolute(l, page)}">\n' for l, _ in LANGS)
    links += f'  <link rel="alternate" hreflang="x-default" href="{absolute("en", page)}">\n'
    if '<link rel="stylesheet"' not in s: sys.exit(f'{page_path(lang, page)} 에 stylesheet 링크가 없습니다')
    s = re.sub(r'([ \t]*<link rel="stylesheet")', links + r'\1', s, count=1)
    # 2) 헤더 메뉴: 링크들 + 언어 선택
    head = menu_links(lang, page, HEADER_LINKS) + [lang_switch(lang, page)]
    s = re.sub(r'(<nav class="nav" aria-label=")[^"]*(">)(.*?)(</nav>)',
               lambda m: m.group(1) + TXT[lang]['main'] + m.group(2) + '\n      ' + '\n      '.join(head) + '\n    ' + m.group(4),
               s, count=1, flags=re.S)
    # 3) 푸터 메뉴: 링크들 + 언어 목록
    foot = menu_links(lang, page, FOOTER_LINKS) + [footer_langs(lang, page)]
    s = re.sub(r'(<footer class="site-footer">.*?<nav aria-label=")[^"]*(">)(.*?)(</nav>)',
               lambda m: m.group(1) + TXT[lang]['footer'] + m.group(2) + '\n      ' + '\n      '.join(foot) + '\n    ' + m.group(4),
               s, count=1, flags=re.S)
    # 4) 언어 선택 동작 — 예전 인라인 스크립트는 지우고 assets/nav.js 를 넣는다 (CSP: 인라인 스크립트 금지)
    s = re.sub(r'<script>document\.querySelectorAll\("\.lang-select"\)[^\n]*</script>\n?', '', s)
    script = f'<script src="{up}assets/nav.js"></script>'
    if script not in s:
        s = s.replace('</body>', script + '\n</body>', 1)
    # 5) 방문 통계 — pricing.json 의 analytics.cf_beacon_token 이 있으면 Cloudflare Web Analytics 비컨을 넣고, 비면 뺀다
    s = re.sub(r'<script defer src="https://static\.cloudflareinsights\.com/beacon\.min\.js"[^>]*></script>\n?', '', s)
    if BEACON_TOKEN:
        s = s.replace('</body>', f'<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{{"token": "{BEACON_TOKEN}"}}\'></script>\n</body>', 1)
    open(p, 'w', encoding='utf-8').write(s)
    return True

done = [page_path(l, p) for l, _ in LANGS for p in PAGES if process(l, p)]
missing = [(l, p) for l, _ in LANGS for p in PAGES if not os.path.exists(os.path.join(ROOT, page_path(l, p)))]
print('updated', len(done), 'pages:', ' '.join(done))
if missing:
    print('없어서 건너뛴 페이지:', ' '.join(f'{l}/{p}' for l, p in missing))
