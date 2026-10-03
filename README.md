# ShouArchive 홈페이지

ShouArchive(macOS) 의 소개 · 지원 · 개인정보 처리방침 페이지입니다. 순수 정적 HTML/CSS 이고 빌드 단계가 없습니다.

- 공개 주소: https://shouarchive.beakbig.com/ — Cloudflare 에서 이 저장소를 서브도메인에 연결해 서비스 중 (`.html` 주소는 확장자 없는 주소로 307 리다이렉트되므로 외부에 알릴 때는 `/support`, `/privacy` 처럼 확장자 없이)
- 원본(GitHub Pages): https://beakbig.github.io/shouarchive-site/ (`main` 브랜치 루트, Worker 배포 전에도 이 주소는 열립니다)
- 저장소: `BeakBig/shouarchive-site` (공개)

## 구성

| 경로 | 내용 |
| --- | --- |
| `index.html` · `pricing.html` · `download.html` | 한국어 랜딩 · 가격(두 판 비교) · 다운로드 |
| `support.html` · `privacy.html` · `terms.html` · `refund.html` | 한국어 지원(FAQ) · 개인정보 처리방침 · 이용약관 · 환불 정책 |
| `en/` · `ja/` · `zh-Hans/` · `zh-Hant/` · `es/` | 영어 · 일본어 · 중국어 간체 · 번체 · 스페인어판 (같은 일곱 페이지) |
| `assets/style.css` | 공용 스타일 (라이트 · 다크) |
| `assets/icon.png` · `icon-64.png` | 앱 아이콘 |
| `assets/screenshots/<언어>/` | 갤러리 스크린샷 `01.png` ~ `06.png` (2880×1800), 6개 언어 |
| `assets/samples/` | 심사 · 테스트용 합성 APK · AAB |
| `.nojekyll` | GitHub Pages 가 Jekyll 처리 없이 그대로 서빙하게 함 |
| `worker/` | `shouarchive.beakbig.com` 을 이 사이트로 잇는 Cloudflare Worker 와 배포 설명 |
| `tools/localize-nav.py` | 모든 페이지의 6개 언어 전환 메뉴 · 헤더 · 푸터 링크 · `hreflang` 을 다시 맞추는 스크립트 (페이지를 고치거나 언어를 더하면 다시 실행) |
| `tools/pricing.json` · `tools/fill-pricing.py` | 가격 · 링크의 유일한 출처와, 그 값을 페이지에 넣는 스크립트 |

App Store Connect 에 넣는 URL:

- 지원: `https://shouarchive.beakbig.com/support` (다른 언어는 `<언어>/support`)
- 마케팅: `https://shouarchive.beakbig.com/` (다른 언어는 `<언어>/`)
- 개인정보 처리방침: `https://shouarchive.beakbig.com/privacy` (다른 언어는 `<언어>/privacy`)

## 가격 · 링크는 한 곳에서 바꾸기

가격 숫자 · 체험 기간 · 결제 링크 · 다운로드 링크는 **`tools/pricing.json` 한 곳에만** 적습니다. 페이지에는 자리 표시만 두고, `tools/fill-pricing.py` 가 그 값을 넣어 줍니다.

```bash
python3 tools/fill-pricing.py   # pricing.json → 모든 언어 페이지
python3 tools/localize-nav.py    # 언어 전환 · 헤더 · 푸터 · hreflang 다시 맞추기
```

페이지에 쓰는 표시 세 가지:

| 표시 | 쓰임 |
| --- | --- |
| `<span data-price="appstore.price_now">US$2</span>` | 글자 사이에 넣기 (JSON 값이 `null` 이면 페이지에 적힌 문장을 그대로 둡니다 — 각 언어 표현) |
| `<a data-src="commercial.checkout" href="#">` | 링크. JSON 이 비어 있으면 `hidden` 으로 숨겨 두었다가, 값을 채우면 `href` 가 바뀌면서 스스로 나타납니다 |
| `data-live-hide` / `data-live-show` | 상용 판 공개 전에만 보이는 문장 / 공개된 뒤에 보이는 문장. 공개 여부는 `commercial.checkout` 이 채워져 있는지로 판단합니다 |

값이 `null` 이거나 빈 문자열인 항목은 **상용 판이 아직 없다는 뜻**입니다 — 가격이 정해지면 `commercial.price_monthly` 같은 값을 채우고 `commercial.checkout`(Paddle 결제 링크)을 넣습니다. 그러면 「출시 예정」 안내가 자동으로 사라지고 구매 · 다운로드 버튼이 나타납니다.

새 페이지를 만들면 `tools/localize-nav.py` 의 `PAGES` 에 파일 이름을 추가하고 그 페이지를 만들고, 두 스크립트를 한 번씩 실행하세요.

## 올리기

```bash
git add -A && git commit -m "..." && git push
```

푸시하면 Cloudflare 빌드가 `npx wrangler deploy` 로 1분 안팎에 shouarchive.beakbig.com 에 올립니다 (GitHub Pages 원본에도 1분 안팎).

### 주의 — 배포 구조와 빌드가 실패했던 일

- `shouarchive.beakbig.com` 을 서비스하는 것은 Cloudflare 계정의 **`shouarchive` Worker**(정적 파일만)입니다. 이 저장소에 푸시하면 Cloudflare 빌드가 저장소 루트를 그대로 정적 파일로 올립니다 — 설정은 `wrangler.jsonc`, 올리지 않을 파일은 `.assetsignore`. 이 저장소의 `worker/`(`shouarchive-path`) 는 예전 프록시 안이고 계정에 배포돼 있지 않습니다.
- **2026-10-03 빌드 실패**: `.assetsignore` 가 없어 `.git` 까지 올리다가 `.git` 압축 파일(29.1 MiB)이 Workers 파일 한도 **25 MiB** 를 넘어 실패했고, 공개 주소는 예전 내용 · 새 파일 404 로 남았습니다. `.assetsignore` 에 `.git` 등을 넣어 해결.
- `.assetsignore` · `wrangler.jsonc` 를 지우지 마세요. 정적 파일 하나도 25 MiB 를 넘으면 안 됩니다 (스크린샷은 장당 1 MB 안팎).
- 푸시한 뒤에는 공개 주소에서 새로 넣은 파일이 열리는지 확인하세요. 예: `curl -sI https://shouarchive.beakbig.com/assets/screenshots/ko/10.png` 가 200 인지. 반영되지 않으면 Cloudflare 대시보드 › Workers & Pages › `shouarchive` › Deployments · Builds 의 빌드 로그를 봅니다 (빌드 로그는 대시보드에서만 보입니다).

## 남은 일

- App Store 링크는 `https://apps.apple.com/app/id6814686766` 로 넣어 두었습니다 (여섯 언어 랜딩 페이지). 앱이 승인돼 게시되기 전에는 이 링크가 「앱을 사용할 수 없음」으로 보입니다.
- Cloudflare Worker 배포 (`worker/README.md`) — 이것이 끝나야 `https://shouarchive.beakbig.com/` 가 열립니다.
- 저장소 이름을 바꾸면 GitHub Pages 원본 주소가 바뀌므로 `worker/wrangler.toml` 의 `UPSTREAM` 도 함께 고쳐야 합니다.
