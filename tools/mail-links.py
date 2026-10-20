#!/usr/bin/env python3
"""모든 페이지의 support 메일 링크에 제목 · 「보낸 페이지」 줄을 붙인다 (2026-10-20).

받은 메일만 보고도 사이트의 어느 페이지에서 왔는지 알 수 있게 — 제목이 없으면 언어별 「[ShouArchive] 문의」,
이미 있는 제목(환불 요청 · 키 미수신 등)은 「[ShouArchive] …」 모양으로 맞추고, 본문 맨 아래에 「보낸 페이지: 주소」 를 붙인다.
여러 번 돌려도 같다(이미 붙은 줄은 다시 붙이지 않는다). 페이지를 고치거나 더하면 다시 실행:

    python3 tools/mail-links.py
"""
import html
import pathlib
import re
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://shouarchive.beakbig.com"
ADDRESS = "support@beakbig.com"
LANGS = ["en", "es", "ja", "zh-Hans", "zh-Hant"]  # 한국어는 루트
SUBJECT = {
    "ko": "[ShouArchive] 문의",
    "en": "[ShouArchive] Support request",
    "es": "[ShouArchive] Consulta",
    "ja": "[ShouArchive] お問い合わせ",
    "zh-Hans": "[ShouArchive] 咨询",
    "zh-Hant": "[ShouArchive] 諮詢",
}
FROM = {
    "ko": "보낸 페이지:",
    "en": "Sent from:",
    "es": "Enviado desde:",
    "ja": "送信元ページ:",
    "zh-Hans": "来自页面：",
    "zh-Hant": "來自頁面：",
}
LINK = re.compile(r'href="mailto:' + re.escape(ADDRESS) + r'([^"]*)"')


def page_url(rel: pathlib.PurePosixPath) -> str:
    parts = list(rel.parts)
    name = parts[-1][: -len(".html")]
    prefix = "/" + "/".join(parts[:-1]) + "/" if len(parts) > 1 else "/"
    return SITE + prefix + ("" if name == "index" else name)


def rewrite(query: str, lang: str, url: str) -> str:
    params = urllib.parse.parse_qs(html.unescape(query).lstrip("?"), keep_blank_values=True)
    subject = params.get("subject", [""])[0].strip()
    body = params.get("body", [""])[0]
    if not subject:
        subject = SUBJECT[lang]
    elif not subject.startswith("[ShouArchive]"):
        subject = "[ShouArchive] " + (subject[len("ShouArchive "):] if subject.startswith("ShouArchive ") else subject)
    line = f"{FROM[lang]} {url}"
    if line not in body:
        body = (body.rstrip("\n") + "\n\n\n" if body.strip() else "\n\n\n") + "---\n" + line
    q = lambda s: urllib.parse.quote(s, safe="")
    return f"?subject={q(subject)}&amp;body={q(body)}"


def main() -> int:
    changed = 0
    pages = sorted(ROOT.glob("*.html")) + [p for lang in LANGS for p in sorted((ROOT / lang).glob("*.html"))]
    for path in pages:
        rel = pathlib.PurePosixPath(path.relative_to(ROOT).as_posix())
        lang = rel.parts[0] if len(rel.parts) > 1 else "ko"
        url = page_url(rel)
        text = path.read_text(encoding="utf-8")
        new = LINK.sub(lambda m: f'href="mailto:{ADDRESS}{rewrite(m.group(1), lang, url)}"', text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"메일 링크를 고친 페이지 {changed}개 / {len(pages)}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
