#!/usr/bin/env python3
"""변경 사항 페이지(6개 언어 changelog.html) → news.json 의 ShouArchive 업데이트 내역 항목.

앱(1.0.3~)의 「소식 › ShouArchive」 는 news.json 에서 `"platforms": ["shouarchive"]` 항목을 읽는다.
버전마다 글을 두 곳에 따로 쓰지 않도록, 업데이트 내역의 원본은 변경 사항 페이지이고 이 스크립트가 news.json 을 맞춘다.
  - 버전 = 한국어 changelog.html 의 <h2 id="v1-0-3">1.0.3 — 2026년 10월 29일</h2> (날짜가 없으면 FIRST_RELEASE_DATES)
  - 제목 = 「ShouArchive 1.0.3」 (제목 줄의 — 뒤가 날짜가 아니면 「ShouArchive 1.0.0 — 첫 출시」 처럼 붙인다)
  - 요약 = 그 h2 아래 <li> 들을 한 줄씩 (「- 」 로 시작, 태그는 뺀다)
  - 원문 = 그 언어의 변경 사항 페이지 #v1-0-3 (영어가 기본 url)
다른 소식(Apple · Google)은 건드리지 않는다. 1.0.1 · 1.0.2 앱은 shouarchive 항목을 모르는 플랫폼이라 뺀다.

  python3 tools/sync-releases.py           # news.json 을 고친다
  python3 tools/sync-releases.py --check   # 맞지 않으면 알리고 종료 코드 1 (check-site.py 도 같은 검사를 한다)
"""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://shouarchive.beakbig.com'
LANGS = ['ko', 'en', 'ja', 'zh-Hans', 'zh-Hant', 'es']
# 제목 줄에 날짜를 적지 않은 버전의 공개일 (1.0.0 — 처음 DMG 를 연 날, 사이트 d1341a9)
FIRST_RELEASE_DATES = {'1.0.0': '2026-10-22'}

H2 = re.compile(r'<h2 id="v(\d+(?:-\d+)+)">(.*?)</h2>(.*?)(?=<h2 id="v|</section>)', re.S)
LI = re.compile(r'<li>(.*?)</li>', re.S)
KO_DATE = re.compile(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일')


def page(lang):
    return os.path.join(ROOT, 'changelog.html' if lang == 'ko' else os.path.join(lang, 'changelog.html'))


def link(lang, anchor):
    prefix = '' if lang == 'ko' else f'{lang}/'
    return f'{SITE}/{prefix}changelog#{anchor}'


def text(fragment):
    return html.unescape(re.sub(r'<[^>]+>', '', fragment)).strip()


def sections(lang):
    """{버전: (제목 줄 — 뒤, [항목 …])}"""
    source = open(page(lang), encoding='utf-8').read()
    found = {}
    for anchor, heading, body in H2.findall(source):
        version = anchor.replace('-', '.')
        label = text(heading).split('—', 1)[-1].strip() if '—' in heading else ''
        found[version] = (label, [text(li) for li in LI.findall(body)])
    return found


def release_items():
    by_lang = {lang: sections(lang) for lang in LANGS}
    items = []
    for version, (ko_label, _) in by_lang['ko'].items():
        match = KO_DATE.search(ko_label)
        published = (f'{int(match[1]):04d}-{int(match[2]):02d}-{int(match[3]):02d}' if match
                     else FIRST_RELEASE_DATES.get(version))
        if not published:
            raise SystemExit(f'{version}: 한국어 제목 줄에 날짜가 없습니다 — 날짜를 적거나 FIRST_RELEASE_DATES 에 넣으세요')
        anchor = 'v' + version.replace('.', '-')
        title, summary = {}, {}
        for lang in LANGS:
            if version not in by_lang[lang]:
                raise SystemExit(f'{lang}/changelog.html 에 {version} 이 없습니다')
            label, lines = by_lang[lang][version]
            # 날짜가 아닌 꼬리(「첫 출시」)만 제목에 붙인다
            title[lang] = f'ShouArchive {version}' + ('' if not label or re.search(r'\d{4}', label) else f' — {label}')
            summary[lang] = '\n'.join(f'- {line}' for line in lines)
        items.append({
            'id': f'shouarchive-{version}',
            'platforms': ['shouarchive'],
            'version': version,
            'published': published,
            'deadline': None,
            'source': 'ShouArchive',
            'url': link('en', anchor),
            'urls': {lang: link(lang, anchor) for lang in LANGS if lang != 'en'},
            'title': title,
            'summary': summary,
        })
    return items


def synced(feed):
    others = [item for item in feed.get('items', []) if 'shouarchive' not in (item.get('platforms') or [])]
    return {**feed, 'items': others + release_items()}


def main():
    path = os.path.join(ROOT, 'news.json')
    feed = json.load(open(path, encoding='utf-8'))
    want = synced(feed)
    if '--check' in sys.argv:
        if want != feed:
            print('news.json 의 ShouArchive 업데이트 내역이 변경 사항 페이지와 다릅니다 — python3 tools/sync-releases.py')
            sys.exit(1)
        print('업데이트 내역 일치')
        return
    open(path, 'w', encoding='utf-8').write(json.dumps(want, ensure_ascii=False, indent=2) + '\n')
    print(f'news.json — 업데이트 내역 {len(release_items())}개')


if __name__ == '__main__':
    main()
