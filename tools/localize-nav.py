#!/usr/bin/env python3
"""모든 언어 페이지에 6개 언어 전환 메뉴(헤더 select · 푸터 링크)와 hreflang 링크를 넣는다. 여러 번 실행해도 결과가 같다."""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = [('ko', '한국어'), ('en', 'English'), ('ja', '日本語'), ('zh-Hans', '简体中文'), ('zh-Hant', '繁體中文'), ('es', 'Español')]
PAGES = ['index.html', 'support.html', 'privacy.html']
LABEL = {'ko': '언어', 'en': 'Language', 'ja': '言語', 'zh-Hans': '语言', 'zh-Hant': '語言', 'es': 'Idioma'}

def page_path(lang, page):  # 저장소 루트 기준 경로
    return page if lang == 'ko' else f'{lang}/{page}'

def rel(from_lang, to_lang, page):  # from 페이지에서 to 페이지로 가는 상대 경로
    up = '' if from_lang == 'ko' else '../'
    return up + page_path(to_lang, page)

def process(lang, page):
    p = os.path.join(ROOT, page_path(lang, page))
    if not os.path.exists(p): return False
    s = open(p).read()
    # 1) hreflang 링크 묶음 교체
    s = re.sub(r'(?:[ \t]*<link rel="alternate" hreflang="[^"]+" href="[^"]+">\n)+', '', s)
    links = ''.join(f'  <link rel="alternate" hreflang="{l}" href="{rel(lang, l, page)}">\n' for l, _ in LANGS)
    links += f'  <link rel="alternate" hreflang="x-default" href="{rel(lang, "en", page)}">\n'
    s = re.sub(r'([ \t]*<link rel="stylesheet")', links + r'\1', s, count=1)
    # 2) 헤더: 기존 <a class="lang"> 또는 이미 넣은 select 를 select 로
    opts = ''.join(f'<option value="{rel(lang, l, page)}"{" selected" if l == lang else ""}>{name}</option>' for l, name in LANGS)
    select = f'<label class="lang-switch"><span class="visually-hidden">{LABEL[lang]}</span><select class="lang-select" aria-label="{LABEL[lang]}">{opts}</select></label>'
    s = re.sub(r'<label class="lang-switch">.*?</label>', select, s, count=1, flags=re.S)
    s = re.sub(r'<a class="lang" href="[^"]+"[^>]*>[^<]*</a>', select, s, count=1)
    # 3) 푸터: 언어 링크들 교체 (푸터 nav 안의 lang= 링크 또는 이미 넣은 .footer-langs)
    foot = '<span class="footer-langs">' + ' '.join(f'<a href="{rel(lang, l, page)}" lang="{l}" hreflang="{l}"{" aria-current=\"page\"" if l == lang else ""}>{name}</a>' for l, name in LANGS) + '</span>'
    if '<span class="footer-langs">' in s:
        s = re.sub(r'<span class="footer-langs">.*?</span>', foot, s, count=1, flags=re.S)
    else:
        m = re.search(r'(<footer.*?<nav[^>]*>)(.*?)(</nav>)', s, flags=re.S)
        if m:
            inner = re.sub(r'\s*<a href="[^"]+" lang="[^"]+" hreflang="[^"]+">[^<]*</a>', '', m.group(2))
            s = s[:m.start(2)] + inner.rstrip() + '\n      ' + foot + '\n    ' + s[m.end(2):]
    # 4) select 동작 스크립트
    script = '<script>document.querySelectorAll(".lang-select").forEach(function(e){e.addEventListener("change",function(){location.href=e.value})})</script>'
    if 'lang-select").forEach' not in s:
        s = s.replace('</body>', script + '\n</body>', 1)
    open(p, 'w').write(s)
    return True

done = [page_path(l, p) for l, _ in LANGS for p in PAGES if process(l, p)]
print('updated', len(done), 'pages:', ' '.join(done))
