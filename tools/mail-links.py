#!/usr/bin/env python3
"""모든 페이지의 support 메일 링크에 제목 · 「보낸 페이지」 줄을 붙인다 (2026-10-20).

받은 메일만 보고도 사이트의 어느 페이지에서 왔는지 알 수 있게 — 제목은 앱의 문의 메일(`[ShouArchive][이슈] …`)과 같은 모양
「[ShouArchive][<페이지 코드>] <제목>」(제목이 없으면 언어별 「문의」), 본문 맨 아래에 「보낸 페이지: 주소 (코드)」.
페이지 코드는 언어와 상관없이 같다(W = 웹사이트) — 메일함에서 코드로 걸러 모을 수 있다. 바꾸면 메일 필터도 같이 고친다.
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
# 페이지 코드 — 정해진 값이다(메일 필터가 쓴다)
PAGE_CODE = {
    "index": "W-HOME",
    "pricing": "W-PRICE",
    "download": "W-DL",
    "support": "W-SUP",
    "privacy": "W-PRIV",
    "terms": "W-TERMS",
    "refund": "W-REFUND",
    "checkout": "W-BUY",
    "activate": "W-ACT",
    "license": "W-KEY",
    "rotate": "W-ROTATE",
}
SUBJECT = {
    "ko": "문의",
    "en": "Support request",
    "es": "Consulta",
    "ja": "お問い合わせ",
    "zh-Hans": "咨询",
    "zh-Hant": "諮詢",
}
TAGS = re.compile(r"^(?:\s*\[(?:ShouArchive|W-[A-Z]+)\])+\s*")
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


def rewrite(query: str, lang: str, url: str, code: str) -> str:
    params = urllib.parse.parse_qs(html.unescape(query).lstrip("?"), keep_blank_values=True)
    # 이미 붙은 태그 · 「ShouArchive 」 접두어를 떼고 다시 붙인다 (여러 번 돌려도 같게)
    subject = TAGS.sub("", params.get("subject", [""])[0].strip())
    if subject.startswith("ShouArchive "):
        subject = subject[len("ShouArchive "):]
    subject = f"[ShouArchive][{code}] {subject or SUBJECT[lang]}"
    body = params.get("body", [""])[0]
    cut = body.find("\n---\n" + FROM[lang])
    if cut >= 0:
        body = body[:cut]
    body = body.rstrip("\n")
    body = (body + "\n\n\n" if body.strip() else "\n\n\n") + "---\n" + f"{FROM[lang]} {url} ({code})"
    q = lambda s: urllib.parse.quote(s, safe="")
    return f"?subject={q(subject)}&amp;body={q(body)}"


def main() -> int:
    changed = 0
    pages = sorted(ROOT.glob("*.html")) + [p for lang in LANGS for p in sorted((ROOT / lang).glob("*.html"))]
    for path in pages:
        rel = pathlib.PurePosixPath(path.relative_to(ROOT).as_posix())
        lang = rel.parts[0] if len(rel.parts) > 1 else "ko"
        url = page_url(rel)
        code = PAGE_CODE[rel.parts[-1][: -len(".html")]]
        text = path.read_text(encoding="utf-8")
        new = LINK.sub(lambda m: f'href="mailto:{ADDRESS}{rewrite(m.group(1), lang, url, code)}"', text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"메일 링크를 고친 페이지 {changed}개 / {len(pages)}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
