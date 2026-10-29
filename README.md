# ShouArchive 홈페이지

ShouArchive(macOS) 의 소개 · 지원 · 개인정보 처리방침 페이지입니다. 순수 정적 HTML/CSS 이고 빌드 단계가 없습니다.

- 공개 주소: https://shouarchive.beakbig.com/ — Cloudflare 에서 이 저장소를 서브도메인에 연결해 서비스 중 (`.html` 주소는 확장자 없는 주소로 307 리다이렉트되므로 외부에 알릴 때는 `/support`, `/privacy` 처럼 확장자 없이. **사이트 안 링크 · `canonical` · `hreflang` 도 전부 확장자 없는 주소**다 — 2026-10-20 통일, `check-site.py` 가 `.html` 링크를 잡는다)
- 원본(GitHub Pages): https://beakbig.github.io/shouarchive-site/ (`deploy` 브랜치 루트, Worker 배포 전에도 이 주소는 열립니다)
- 저장소: `BeakBig/shouarchive-site` (공개)

## 구성

| 경로 | 내용 |
| --- | --- |
| `index.html` · `pricing.html` · `download.html` | 한국어 랜딩 · 가격(체험 · 구매 후 기능표) · 다운로드 |
| `support.html` · `privacy.html` · `terms.html` · `refund.html` | 한국어 지원(FAQ) · 개인정보 처리방침 · 이용약관 · 환불 정책 |
| `changelog.html` | 한국어 변경 사항(2026-10-26) — 버전마다 바뀐 점만 적는다(가격 · 라이선스 · 출시 예정 같은 안내는 넣지 않는다). 새 버전을 낼 때마다 맨 위에 `<h2 id="v<버전>">` 항목을 6개 언어로 더한다(그 버전의 Sparkle 릴리스 노트와 같은 내용 · 출시 날짜는 제목 줄에 직접). 바닥 메뉴 · 다운로드 페이지에서 링크 |
| `checkout.html` | 한국어 구매 페이지 — Paddle 의 「기본 결제 링크(default payment link)」. 「구매하기」 는 라이선스 서버에 결제를 만들고(`/v1/web/checkout`, 실패하면 예전처럼 가격 id 로) Paddle.js 오버레이를 엽니다. `?_ptxn=` 거래(라이선스 서버가 만든 갱신 · 앱 안 구매)는 Paddle.js 가 스스로 엽니다. 결제가 끝나면(`checkout.completed`) 「결제를 확인하고 있습니다」 카드(앱과 같은 Lottie 퍼즐 로딩 — 못 불러오면 도는 원)를 띄우고 `#claim` 확인 값으로 키를 받아 와 「ShouArchive 에서 열기」 · 「키 복사」 를 보여 주고, 앱에서 시작한 결제(`from=app`)면 앱을 바로 엽니다. 1분(2초 간격)이 지나도 키가 없으면 「결제는 완료되었습니다 — 메일함 · 스팸함을 확인하고, 안 오면 support@shouarchive.beakbig.com 으로」 안내(`checkout-slow`)로 바꾸고, 페이지를 열어 둔 동안 5초 간격으로 5분 더 확인해 준비되면 키를 보여 줍니다. 갱신(`#kind=renewal`)은 기간 연장 안내. 서버가 키를 보관하지 않거나 확인 값이 맞지 않으면 메일 안내. `?done=1`(예전 successUrl)도 메일 안내. 메뉴에는 넣지 않습니다 |
| `activate.html` | 메일의 「앱에서 바로 등록하기」 링크가 여는 중계 페이지 — `#key=` 의 키를 보여 주고 `shouarchive://activate?key=…` 로 앱을 엽니다(Mac 데스크톱에서만 저절로, 휴대폰에서는 버튼만). 키는 `#` 뒤라 서버로 가지 않고, 읽은 뒤 주소에서 지웁니다. 메뉴에 넣지 않고 검색에서 뺍니다(`noindex`) |
| `license.html` | 키 다시 받기 — 구매 이메일을 받아 라이선스 서버(`/v1/licenses/resend`)에 보냅니다. 서버는 늘 같은 답을 주고 구매 이메일로만 같은 키를 보냅니다. 메뉴에 넣지 않습니다(`noindex`, 메일 · 지원 FAQ · 앱에서 링크) |
| `rotate.html` | 키 바꾸기(2026-10-17) — 키가 남에게 알려진 것 같을 때. 그냥 열면 구매 이메일을 받아 확인 메일을 요청하고(`/v1/licenses/rotate`), 메일의 링크(`#token=`)로 열면 「키 바꾸기」 단추를 보여 줍니다 — **단추를 눌러야** 바뀝니다(`/v1/licenses/rotate/confirm`, 메일 보안 검사기가 링크를 미리 열어도 그대로). 새 키는 페이지에 보여 주지 않고 구매 이메일로만 갑니다. 확인 값은 읽은 뒤 주소에서 지웁니다. 쓴 · 만료된 링크면 안내와 함께 요청 양식을 보여 줍니다. 새 Mac 등록 알림 메일의 「내가 아니라면」 링크도 여기로 옵니다. `noindex` |
| `erase.html` | 개인정보 삭제(2026-10-20) — `rotate.html` 과 같은 두 모드. 그냥 열면 구매 이메일을 받아 확인 메일을 요청하고(`/v1/privacy/erase`, 구매 여부와 상관없이 같은 답), 메일의 링크(`#token=`, 24시간)로 열면 삭제되는 내용 목록과 「삭제」 단추를 보여 줍니다 — **단추를 눌러야** 지워집니다(`/v1/privacy/erase/confirm` → `{ status: erased, licenses }`). 그 이메일의 모든 라이선스 해지 · 등록된 Mac 해제 · 구매 이메일 · 보관한 키 · 발송 기록 · 확인 링크 삭제 · 업데이트 구독 해지. 결제 기록(거래 id · 종류 · 시각)은 전자상거래법상 5년 보관, Paddle 이 가진 정보는 Paddle(privacy@paddle.com · paddle.net)에 따로. 쓴 · 만료된 링크(`erase_not_found` · `erase_expired`)면 안내와 함께 요청 양식. 확인 값은 읽은 뒤 주소에서 지웁니다. `noindex`, 메뉴에 넣지 않고 개인정보 처리방침 6 · 11항과 지원 FAQ 에서 링크 |
| `billing.html` | 결제 수단 바꾸기(2026-10-23) — Paddle **Retain 결제 복구**용. 업데이트 자동 갱신 결제가 실패하면 Retain 이 고객에게 결제 수단을 바꾸라는 메일을 보내는데, Retain 설정(Step 4 「Configure Paddle.js」)은 결제 · 가격 페이지가 **아닌** 공개 페이지에 Paddle.js 가 있는지 주소로 확인한다(리다이렉트 · 쿼리 · 로그인 없이). 그 페이지가 이것 — Paddle.js 를 불러와 `#paddle-config` 값으로 초기화만 하고(`license.js` 의 `billing`), 복구 링크로 열리면 Paddle.js 가 변경 창을 스스로 띄운다. `pwCustomer` 는 넘기지 않는다(로그인한 고객이 없다 · 결정 41). 홈에 넣지 않은 것은 홈 방문자 모두에게 Paddle 스크립트를 싣지 않으려고 — 개인정보 처리방침 7항은 「구매 페이지와 결제 수단 바꾸기 페이지」 에서만 불러온다고 적는다. Retain 확인에 넣는 주소는 `https://shouarchive.beakbig.com/en/billing`(Retain 메일이 영어). 메뉴에 넣지 않고 `noindex` |
| `404.html` | 없는 주소에 Cloudflare 가 404 로 돌려주는 페이지(`wrangler.jsonc` 의 `not_found_handling: "404-page"`, GitHub Pages 도 루트 `404.html` 을 씀). 어느 경로에서든 열리므로 주소는 절대 주소이고, 6개 언어 안내가 한 페이지에 있습니다. 언어판이 없고 `localize-nav.py` 가 건드리지 않습니다 |
| `en/` · `ja/` · `zh-Hans/` · `zh-Hant/` · `es/` | 영어 · 일본어 · 중국어 간체 · 번체 · 스페인어판 (같은 열세 페이지) |
| `_headers` | Cloudflare Workers 정적 자산의 응답 헤더 규칙 — 모든 경로에 `X-Content-Type-Options: nosniff` · `Referrer-Policy: strict-origin-when-cross-origin` · `X-Frame-Options: DENY` · `Permissions-Policy` · `Content-Security-Policy`(`default-src 'self'`, 스크립트는 자기 사이트 · Paddle CDN · Cloudflare Web Analytics 비컨(`static.cloudflareinsights.com`, 보고는 `connect-src` 의 `cloudflareinsights.com`), 결제 창 `frame-src` 는 `*.paddle.com`, `connect-src` 는 라이선스 서버와 `*.paddle.com`, 스타일만 `'unsafe-inline'`, `frame-ancestors 'none'`). **인라인 `<script>` 는 막히므로 두지 않습니다** — 언어 전환은 `assets/nav.js`, 라이선스 페이지는 `assets/license.js` 의 `data-page` 로 실행하고 `check-site.py` 가 인라인 스크립트를 잡습니다. 파일 자체는 서빙되지 않고 `.assetsignore` 에 넣으면 안 됩니다. 라이선스 서버 주소를 바꾸면 `connect-src` 도 고칩니다 |
| `news.json` | 앱 「소식」 탭(1.0.1~)이 받는 소식 목록 — 앱에 박힌 주소 `https://shouarchive.beakbig.com/news.json` 이라 옮기거나 이름을 바꾸면 안 된다. `_headers` 가 `no-cache` 로 내보낸다. 형식 · 쓰는 법은 아래 「소식 목록」, `check-site.py` 가 형식을 검사한다 |
| `assets/style.css` | 공용 스타일 (라이트 · 다크). Mac 앱 내려받기 단추에는 `mac-only` 를 붙이고 바로 뒤에 `<p class="mac-note" data-if="commercial.download">` 안내(「Mac 에서 이 페이지를 열어 내려받으세요」)를 둔다 — 터치가 주 입력인 기기(휴대폰 · 태블릿, `(hover: none) and (pointer: coarse)`)에서는 단추가 숨고 안내가 보인다. 창 너비가 아니라 입력 장치로 가르므로 좁게 줄인 Mac 창에서는 단추가 그대로다(2026-10-29). 다운로드 단추를 새로 넣으면 둘 다 붙인다 |
| `assets/nav.js` | 언어 전환 `<select>` 동작 하나 — 모든 페이지가 `</body>` 앞에서 불러옵니다(`localize-nav.py` 가 넣음). 예전 인라인 스크립트를 CSP 때문에 파일로 뺀 것 |
| `assets/license.js` | 결제 완료 화면 · `billing.html` · `activate.html` · `license.html` · `rotate.html` · `erase.html` 이 함께 쓰는 스크립트 (언어 중립 — 문구는 각 페이지 HTML 에 있고 보이기 · 숨기기 · 값 채우기만 합니다). 페이지는 `<script src="assets/license.js" data-page="checkout|billing|activate|resend|rotate|erase">` 로 불러오고 그 이름의 함수가 바로 실행됩니다. 라이선스 서버 주소는 `#paddle-config` 의 `data-license-api`, 없으면 기본값 `https://license.beakbig.com`. 결제 페이지는 `#claim` 등 확인 값을 읽은 직후 주소에서 지우고, Paddle.js 를 불러오지 못하면(광고 차단기) 「결제 모듈을 불러오지 못했습니다」(`#checkout-blocked`), 결제 만들기 상한(409 `checkout_limit`)이면 「지금은 결제 요청이 많습니다」(`#checkout-limit`)를 보여 줍니다. 서버 계약은 라이선스 서버 저장소 `docs/app-contract.md` §2.10 – §2.13 과 2026-10-20 계약(개인정보 삭제 §8) |
| `assets/vendor/lottie_light.min.js` | [lottie-web](https://github.com/airbnb/lottie-web) 5.12.2 의 light(SVG) 빌드 — 결제 확인 중 그림. npm 에서 받아 무결성(sha512)을 확인했고 라이선스는 `assets/vendor/lottie-web-LICENSE.md`(MIT). 외부 CDN 을 쓰지 않으려고 사이트에 둔다. 결제 확인 카드를 띄울 때만 불러온다 |
| `assets/loading/puzzle_loading.json` | 앱의 로딩 표시와 같은 Lottie 퍼즐 — 앱 저장소 `ShouArchive/Resources/Loading/puzzle_loading.json` 의 사본(앱 쪽을 바꾸면 같이 바꾼다) |
| `assets/icon.png` · `icon-64.png` | 앱 아이콘 |
| `assets/mail-icon.png` | 라이선스 서버 메일 머리 띠의 아이콘 (96×96 · 40pt 를 2배로) — 메일이 이 주소로 불러오므로 지우거나 옮기지 않는다 |
| `assets/screenshots/<언어>/` | 갤러리 스크린샷 `01.png` ~ `06.png` (2880×1800), 6개 언어 |
| `assets/samples/` | 심사 · 테스트용 합성 APK · AAB |
| `.nojekyll` | GitHub Pages 가 Jekyll 처리 없이 그대로 서빙하게 함 |
| `wrangler.jsonc` · `.assetsignore` | 루트 `wrangler.jsonc` 가 저장소 루트를 정적 자산으로 배포합니다(Cloudflare 빌드가 푸시마다 `npx wrangler deploy`). `html_handling: auto-trailing-slash`(확장자 없는 주소) · `not_found_handling: 404-page`. 올리지 않을 파일은 `.assetsignore`. 예전 프록시 Worker(`worker/`)는 2026-10-20 에 지웠습니다 — 계정에 배포된 적이 없는 죽은 코드였습니다 |
| `tools/localize-nav.py` | 모든 페이지의 6개 언어 전환 메뉴 · 헤더 · 푸터 링크 · `canonical` · `hreflang`(절대 주소, 확장자 없음) 을 다시 맞추고 `assets/nav.js` 를 넣는 스크립트 (페이지를 고치거나 언어를 더하면 다시 실행) |
| `tools/pricing.json` · `tools/fill-pricing.py` | 가격 · 링크 · Paddle 공개 설정 · 판매자 정보 · 방문 통계 토큰(`analytics.cf_beacon_token` — Cloudflare Web Analytics, 쿠키 없음. 비컨은 `localize-nav.py` 가 토큰이 있을 때만 넣는다 · 2026-10-21)의 유일한 출처와, 그 값을 페이지에 넣는 스크립트 |
| `tools/mail-links.py` | 모든 페이지의 support 메일 링크에 제목 「[ShouArchive][<페이지 코드>] <제목>」(제목이 없으면 언어별 「문의」 — 앱의 문의 메일 `[ShouArchive][이슈] …` 과 같은 모양)과 본문 맨 아래 「보낸 페이지: 주소 (코드)」 를 붙이는 스크립트. 페이지 코드(언어 무관, 메일 필터가 쓴다): `W-HOME` 홈 · `W-PRICE` 가격 · `W-DL` 다운로드 · `W-SUP` 지원 · `W-PRIV` 개인정보 · `W-TERMS` 약관 · `W-REFUND` 환불 · `W-BUY` 구매 · `W-ACT` 앱에서 등록 · `W-KEY` 키 다시 받기 · `W-ROTATE` 키 바꾸기 · `W-ERASE` 개인정보 삭제 · `W-BILL` 결제 수단 바꾸기 · `W-LOG` 변경 사항 · `W-404` 없는 페이지. 메일 링크를 더하거나 페이지를 고치면 다시 실행(여러 번 돌려도 같다) |
| `tools/check-site.py` | 사이트 전체 점검 — 6개 언어 × 14개 페이지 구조 · 링크(확장자 없는 주소) · 번역 누락 · 가격 키 · Paddle 설정 · 인라인 스크립트(CSP) · `_headers` · `404.html` · 25 MiB 한도. `paddle.*` 가 샌드박스면 **경고**(종료 코드는 그대로) |

ShouArchive 는 이 사이트에서만 판매합니다 (2026-10-15 결정 — Mac App Store 판은 출시하지 않고 제출을 거둬들임). 그래서 `pricing.json` 에는 `appstore.*` 키가 없고, 6개 언어 페이지 모두 `commercial.*` · `seller.*` 키만 씁니다(`fill-pricing.py` 가 없는 키를 만나면 코드 1 로 알립니다).

외부에 알리는 주소:

- 지원: `https://shouarchive.beakbig.com/support` (다른 언어는 `<언어>/support`)
- 홈: `https://shouarchive.beakbig.com/` (다른 언어는 `<언어>/`)
- 개인정보 처리방침: `https://shouarchive.beakbig.com/privacy` (다른 언어는 `<언어>/privacy`)

## 소식 목록 (`news.json`)

앱의 「소식」 탭(1.0.1~)은 앱을 열 때 · 탭을 열 때(6시간에 한 번까지) · 「새로고침」 을 누를 때 이 파일을 받는다. 푸시하면 1분쯤 뒤 모든 앱에 보인다(앱 업데이트 필요 없음).

```json
{ "version": 1,
  "items": [ { "id": "2026-10-16-app-review-2-5-19", "platforms": ["ios"], "published": "2026-10-16", "deadline": null,
               "source": "Apple", "url": "https://developer.apple.com/news/?id=…",
               "urls": { "ko": "https://developer.apple.com/kr/news/?id=…" },
               "title": { "ko": "…", "en": "…", "ja": "…", "zh-Hans": "…", "zh-Hant": "…", "es": "…" },
               "summary": { "ko": "…", "en": "…", "ja": "…", "zh-Hans": "…", "zh-Hant": "…", "es": "…" } } ] }
```

- `id` — 바꾸지 않는다(앱이 읽음 표시를 id 로 기억한다). `<날짜>-<짧은 이름>` 꼴. 목록에서 빼면 앱의 읽음 기록도 지워진다.
- `platforms` — `ios` · `android` 중 해당하는 것(비우면 양쪽). 앱은 iOS 화면에서 iOS · 양쪽 소식만 보인다.
- `published` — 원문의 날짜(`YYYY-MM-DD`). 앱은 최근 것을 위에 두고, 60일보다 오래된 소식은 새로 쓰는 사람의 배지에 세지 않는다.
- `deadline` — 개발자가 맞춰야 하는 날이 있을 때만(`YYYY-MM-DD`, 없으면 `null`). 앱이 「D-N」 으로 보인다(30일 안이면 경고색).
- `source` — 출처 이름(번역하지 않는다). `url` — 원문(영어), **https 만**(아니면 앱이 그 항목을 뺀다).
- `urls` — 번역된 원문이 있는 언어만(`ko` · `ja` · `zh-Hans` · `zh-Hant` · `es`, 1.0.2~). 앱은 앱 언어의 주소를 열고, 없으면 `url`(영어)을 연다 — 다른 언어로 물러나지 않는다(번체에 간체를 열지 않음). **번역판이 영어판과 같은 내용인지 열어 보고** 넣는다 — Apple 「새로 추가될 요구사항」 번역판은 10/29 에 아직 Xcode 16 기준이라 넣지 않았다. Apple 은 `/kr/` · `/jp/` · `/cn/`(간체)만 있고, Android 는 `?hl=ko` · `ja` · `zh-cn` · `zh-tw` · `es-419`. 1.0.1 앱은 `urls` 를 모르고 `url` 을 연다.
- `title` · `summary` — 6개 언어 모두. 원문을 옮겨 적지 않고 짧게 다시 쓴다(저작권). 사실은 원문에서 확인한 것만 — 기술 문장은 개발 세션 검수(마케팅 TC 와 같은 기준).
- **ShouArchive 업데이트 내역**(앱 1.0.3~ 「소식 › ShouArchive」) — `"platforms": ["shouarchive"]` + `"version": "1.0.3"` 항목. 손으로 쓰지 않는다: 변경 사항 페이지(6개 언어)에 버전을 더한 뒤 `python3 tools/sync-releases.py` 가 만든다(제목 「ShouArchive 1.0.3」 · 요약 = 그 버전의 항목들 · 원문 = 그 언어의 변경 사항 #v1-0-3). `check-site.py` 가 둘이 같은지 본다. 1.0.1 · 1.0.2 앱은 이 항목을 뺀다(모르는 플랫폼).
- 형식을 바꿔야 하면 `version` 을 올리고 앱을 먼저 고친다 — 지금 앱은 `version` 1 만 읽고 더 높은 번호는 통째로 무시한다.

## 가격 · 링크는 한 곳에서 바꾸기

가격 숫자 · 체험 기간 · 결제 링크 · 다운로드 링크 · Paddle 공개 설정 · 판매자(사업자) 정보는 **`tools/pricing.json` 한 곳에만** 적습니다. 페이지에는 자리 표시만 두고, `tools/fill-pricing.py` 가 그 값을 넣어 줍니다.

```bash
python3 tools/fill-pricing.py   # pricing.json → 모든 언어 페이지
python3 tools/localize-nav.py    # 언어 전환 · 헤더 · 푸터 · canonical · hreflang 다시 맞추기
python3 tools/mail-links.py      # support 메일 링크에 페이지 코드 · 「보낸 페이지」 줄
python3 tools/sync-releases.py   # 변경 사항 페이지 → news.json 의 ShouArchive 업데이트 내역
python3 tools/check-site.py      # 6개 언어 × 14개 페이지 구조 · 링크 · 번역 · CSP · 용량 점검
```

페이지에 쓰는 표시 다섯 가지:

| 표시 | 쓰임 |
| --- | --- |
| `<span data-price="commercial.price">US$29</span>` | 글자 사이에 넣기. 값이 `null` 일 때 — `commercial.*` 키는 `undecided` 에 있는 그 언어 문장(「가격 미정」)을 넣고(정하지 않은 금액이 숫자로 남지 않게), `seller.*` 같은 다른 키는 페이지의 주황색 자리 표시(`<span class="placeholder" data-price="seller.owner">[대표자]</span>`)를 그대로 둡니다. 값이 채워지면 `placeholder` class 도 떼어 냅니다. pricing.json 에 없는 키는 건드리지 않고 마지막에 목록으로 알립니다(종료 코드 1) |
| `<a data-src="commercial.checkout" href="#">` | 링크. JSON 이 비어 있으면 `hidden` 으로 숨겨 두었다가, 값을 채우면 `href` 가 바뀌면서 스스로 나타납니다 |
| `data-live-hide` / `data-live-show` | 출시 전에만 보이는 문장 / 공개된 뒤에 보이는 문장. 공개 여부는 `commercial.checkout` 이 채워져 있는지로 판단합니다 |
| `<p data-if="commercial.download_sha256" hidden>SHA-256: …</p>` | 그 키의 값이 비어 있으면(`null` · `""`) 숨기고, 채워지면 보이는 줄. 다운로드 페이지의 SHA-256 줄에 씁니다 — 안의 `data-price` 자리는 평소 규칙대로 채워지지만 줄이 숨겨져 보이지 않습니다. 키 앞에 `!` 를 붙이면 반대(비어 있을 때만 보임), 공백으로 여러 개를 적으면 모두 맞을 때만 보입니다 — `data-if="commercial.download !commercial.checkout"` 은 내려받기는 열렸고 판매는 아직일 때만 보이는 문장입니다. `data-live-hide` · `data-live-show` 와 한 요소에 같이 쓰지 않습니다 |
| `<div id="paddle-config" data-env data-token data-price-license data-price-updates data-license-api hidden>` | `checkout.html` · `billing.html` 의 Paddle.js 설정과 라이선스 서버 주소. 실행할 때마다 `paddle.*` 값으로 속성을 다시 씁니다(값을 바꿔 다시 실행하면 그대로 반영) |

`pricing.json` 의 키:

| 키 | 뜻 |
| --- | --- |
| `commercial.price` · `price_renewal` | 처음 구매(라이선스 + 업데이트 1년, US$29) · 업데이트 1년 갱신(US$15, 자동 갱신). 세금 별도 |
| `commercial.devices` · `refund_days` | 라이선스 하나로 쓰는 Mac 수(2) · 결제 후 전액 환불 기간(14일) |
| `commercial.release_date` | 출시일 — 아직 `null` |
| `commercial.checkout` · `download` · `download_sha256` | 구매 페이지 주소(보통 `/checkout`) · `.dmg` 주소 · 그 파일의 SHA-256(64자 hex, `null` 이면 다운로드 페이지의 SHA-256 줄이 숨겨짐 — DMG 를 올릴 때마다 `download` 와 함께 바꾼다). `checkout` 이 채워지면 출시(판매 시작)로 봅니다 — 「출시 예정」 안내가 사라지고 구매 · 다운로드 버튼이 나타납니다 |
| `paddle.environment` | `sandbox` 또는 `production` |
| `paddle.client_token` | Paddle 의 **client-side token**(`test_…` / `live_…`). 비어 있으면 `checkout.html` 은 「결제를 아직 열지 않았습니다」만 보여 줍니다 |
| `paddle.price_license` · `price_updates` | 가격 id(`pri_…`) — 라이선스(US$14, 1회) · 업데이트 1년(US$15, 매년 자동 갱신). 처음 구매 화면에 두 항목을 함께 넣어 합계 US$29 (라이선스 서버에 닿지 못할 때만 이 값으로 직접 엽니다) |
| `paddle.license_api` | 라이선스 서버 주소(`https://license.beakbig.com`) — 결제 완료 화면이 키를 받아 오고 사이트 결제를 만듭니다. 라이선스 서버의 `SITE_ORIGINS` 에 이 사이트 주소가 있어야 브라우저가 부를 수 있습니다(CORS). `activate.html` · `license.html` · `rotate.html` 은 `assets/license.js` 의 기본값을 쓰므로 주소를 바꾸면 거기도 고칩니다 |
| `seller.reg_no` · `owner` · `address` · `phone` · `mail_order` | 페이지 바닥 사업자 정보와 이용약관 2항. 사업자등록번호(613-40-01820)만 정해졌고 나머지는 `null`(주황색 자리 표시) |
| `contact.email` | 문의 주소 `support@shouarchive.beakbig.com` |

> **Paddle 값 중 사이트에 넣어도 되는 것은 client-side token 과 가격 id 뿐입니다** — 둘 다 브라우저에 그대로 보이는 공개 값입니다. **API 키(`pdl_…`)와 웹훅 비밀값(notification secret)은 절대 `pricing.json` 이나 페이지에 넣지 마세요.** 라이선스 서버의 비밀값(Cloudflare Workers secret)으로만 둡니다.

> 숨길 때 쓰는 `hidden` 속성이 CSS 의 `display` 규칙에 밀리지 않게 `assets/style.css` 에 `[hidden] { display: none !important; }` 규칙이 있습니다. 이 규칙을 지우면 출시 전 구매 · 다운로드 버튼이 그대로 보입니다(`check-site.py` 가 확인합니다).

새 페이지를 만들면 `tools/localize-nav.py` 와 `tools/check-site.py` 의 `PAGES`, `tools/mail-links.py` 의 `PAGE_CODE` 에 파일 이름을 추가하고 그 페이지를 6개 언어로 만들고, 스크립트를 한 번씩 실행하세요. `check-site.py` 가 번역이 밀렸거나 링크가 끊긴 페이지를 찾아냅니다 — 6개 언어 × 14개 페이지 = 84개 파일이 모두 같은 구조여야 통과합니다. 사이트 안 링크는 확장자 없이(`href="pricing"`, 홈은 `href="./"`, 다른 언어는 `href="../en/pricing"`) 쓰고, 스크립트는 인라인 대신 `assets/` 파일로 둡니다(`_headers` 의 CSP).

모든 페이지 바닥(`<footer>` 안 `<p class="biz">`)에 사업자 정보(상호 · 대표 · 사업자등록번호 · 통신판매업 신고 · 주소 · 전화 · 이메일 · 결제 대행 Paddle)가 있습니다. `localize-nav.py` 는 바닥의 `<nav>` 만 다시 쓰므로 이 줄은 건드리지 않습니다.

## ⚠️ 법률 문서는 초안입니다 — 검토 후, 발행 전에 고치세요

`terms.html`(이용약관) · `refund.html`(환불 정책) · `privacy.html`(개인정보 처리방침 — 앱 하나 기준으로 합침)는 **법률 검토를 거치지 않은 초안**입니다. **이 문서를 검토하기 전에는 Paddle 판매를 시작하지 마세요.** 주황색(`<span class="placeholder">`)으로 표시한 자리는 아직 판매자가 정하지 못한 값입니다.

이미 정해 둔 것 (초안에 반영되어 자리 표시가 지워짐):

| 정한 내용 | 들어간 곳 |
| --- | --- |
| 판매자 — 상호 비그빅(Beakbig) · 사업자등록번호 613-40-01820(간이과세자) · support@shouarchive.beakbig.com | 이용약관 2항 · 모든 페이지 바닥 |
| 요금 — 처음 구매 US$29(라이선스 + 업데이트 1년, Mac 2대), 업데이트 갱신 1년 US$15(자동 갱신 · 언제든 끄기), 기간 안에 나온 버전은 영구 사용, 기간 뒤 버전은 갱신해야 설치, 끊긴 뒤 갱신하면 결제일부터 1년 | 가격 페이지 · 이용약관 1 · 3.2 · 4항 |
| 체험 — 14일, 결제 수단 없이 앱 안에서 시작, 자동 결제 없음. 키 없이 끝나면 **계속 쓰는 것** = 프로파일 관리(다운로드 · 만들기 · 기기 포함) · 산출물 검사 · API 키 관리 · 히스토리(기록 보기만), **잠기는 것** = 앱 빌드 · 작업 대기열 · 앱 업로드 · 기기 설치 · 다시 서명 · 라이브러리 · IPA 정리 · OTA 배포 · 스토어 배포 (2026-10-20 검토 D4 · W4) | 가격 페이지 · 다운로드 FAQ · 지원 FAQ · 이용약관 1 · 4.3항 · 환불 정책 3항 · 개인정보 12항 |
| 약관 동의 — 앱의 설정 › 라이선스에 약관 · 처리방침 · 환불 정책 링크가 있고, 결제 · 체험 시작 · 계속 사용으로 동의한 것으로 봄 | 이용약관 1항 |
| 만 14세 이상(14세 미만은 법정대리인 동의), 지역 제한 없음(Paddle 판매 불가 지역 제외) | 이용약관 3.1항 |
| 라이선스당 Mac 2대 | 이용약관 3.2항 |
| 가격은 세금 별도 표시, 결제 시 Paddle 이 지역에 맞춰 자동 계산 | 이용약관 4.1항 · 가격 페이지 |
| 환불 — 처음 구매 · 갱신 모두 결제 후 14일 안 전액(한국 전자상거래법 청약철회 7일보다 넓게). 처음 구매 환불 = 라이선스 해지 · 등록된 Mac 모두 해제 · 자동 갱신(구독) 해지. 갱신 환불 = 업데이트 기간을 **갱신 전 날짜로** 되돌림(라이선스 · Mac 그대로). 부분 환불(세금만 등)은 영향 없음. chargeback — 처음 구매면 해지(Mac 은 남아 번복 시 자동 복구), 갱신 결제면 기간만 되돌리고 자동 갱신 끔(D6 (나)). 14일 뒤는 법이 정한 경우 외 환불 없음. **요청은 support@shouarchive.beakbig.com 으로 결제 이메일 + 주문 번호가 1순위**(판매자가 Paddle 에 바로 요청), paddle.net 은 2순위 — 앱의 「해지 방법…」 창도 같은 순서 | 환불 정책 2 · 4 – 9항 · 이용약관 5 · 13항 · 지원 FAQ · 구매 페이지 |
| 책임 상한 — 최근 12개월 동안 고객이 낸 금액까지. 고의 · 중대한 과실은 제한하지 않음 | 이용약관 10.2항 |
| 자동 갱신 — 갱신 7일 전에 결제 이메일과 앱에서 알림. 끄기는 언제든 Paddle 결제 안내 메일의 관리 링크 **또는 앱의 설정 › 라이선스 › 「결제 관리…」**(서버 `/v1/licenses/manage`), 꺼도 앱은 계속 씀. 요금 변경은 최소 30일 전에 결제 이메일과 앱 안내로 알리고 다음 갱신부터(W13). 위반은 이메일로 알린 뒤 정지 — 정지된 라이선스로는 앱이 잠기고 시정되면 되살림 | 이용약관 4.4 · 11항 · 환불 정책 6항 · 가격 · 구매 페이지 |
| 준거법 — 대한민국 법, 1심 관할은 판매자 주소지 관할 법원, 중재 조항 없음, 소비자가 사는 나라의 강행 소비자 보호 규정 그대로 적용 | 이용약관 12항 |
| 개인정보 권리 처리 기한 — 요청을 받은 날부터 10일 이내 · 적용 관할은 대한민국 개인정보 보호법, EU · EEA · 영국 이용자에게는 GDPR · UK GDPR 의 권리도 보장 | 개인정보 처리방침 11항 |
| 개인정보 5항 「사용자 이름 · 기기에 직접 붙인 이름은 쓰지 않습니다」 — 확정했습니다. 기기 식별값이 이미 해시된 값이라 사실과 맞습니다 | 개인정보 처리방침 5항 |
| 라이선스 서버 — 운영 주체 비그빅(Beakbig) · 613-40-01820 · support@shouarchive.beakbig.com, 서버는 Cloudflare, Inc.(미국)의 Workers, 데이터베이스는 아시아 · 태평양 지역(그 지역 안의 실제 위치는 Cloudflare 가 정함), 결제는 Paddle.com Market Limited(영국)가 판매대행 | 이용약관 7항 · 개인정보 처리방침 6항 |
| 기기 식별값 — 하드웨어 UUID 에 앱 전용 접두어를 붙여 SHA-256 으로 바꾼 값의 앞 32자. 하드웨어 UUID 원문 · 호스트 이름 · 사용자 이름은 서버로 보내지 않으며, 하드웨어 UUID 를 못 읽으면 첫 실행 때 만든 무작위 설치 id 를 같은 방식으로 씁니다. Mac 이름이나 네트워크가 바뀌어도 값은 그대로 | 개인정보 처리방침 5항 |
| 저장 방식 — 기기 · 설치 식별값은 HMAC-SHA256 해시만. 라이선스 키는 조회용 SHA-256 해시와 함께 같은 키를 다시 보내려고 AES-256-GCM 암호문으로 보관(열쇠는 DB 밖 Workers secret — 2026-10-16 결정, 이전 「해시만」 문구를 고침). 결제 확인 값 · 키 다시 받기 이메일은 해시만. Mac 모델명 · 앱 버전 · 구매 이메일은 원문 그대로. 저장하지 않는 것(IP · 요청 헤더와 본문 · macOS 버전 · 이름/주소 · 카드 번호 · 마케팅 동의 · 사용 통계)도 5항에 있음 | 개인정보 처리방침 5항 (시행일 2026-10-17) |
| 보관 기간 — 접근 기록 30일(시각 · 동작 · 결과 · 라이선스 id · 기기 해시 · 앱 버전 · 짧은 사유, IP 없음) · 결제 알림 처리 기록 90일 · 키 발송 기록 365일 · 발급 대기 7일 · 결제 확인 기록 30일 · 다른 Mac 해제 기록 30일 · 키 다시 받기 요청 1일은 매일 자동 삭제, 라이선스 · 기기 · 이메일은 라이선스가 있는 동안 보관하고 환불 · chargeback 으로 해지된 뒤 2년(또는 삭제 요청 시) 삭제 또는 익명화 | 개인정보 처리방침 5 · 6항 |
| 개인정보 삭제 — `erase.html` 에서 구매 이메일 확인 뒤 본인이 직접(모든 라이선스 해지 · Mac 해제 · 이메일 · 키 · 발송 기록 · 확인 링크 삭제 · 구독 해지). 결제 기록(거래 id · 종류 · 시각)만 전자상거래법상 5년 보관. Paddle 이 가진 정보는 Paddle(privacy@paddle.com · paddle.net)에 따로. 열람 · 정정과 삭제 페이지를 쓸 수 없는 경우는 support@ 로 10일 이내 | 개인정보 처리방침 6 · 11항 · 지원 FAQ · `erase.html` |
| 보내는 메일 종류 — 라이선스 키 · 키 다시 받기 · 키 바꾸기 확인 · 새 키 · 새 Mac 등록 알림 · 갱신 결제 안내 · 갱신 7일 전 안내 · 갱신 요금 변경 예고 · 개인정보 삭제 확인(마케팅 메일 없음). 개인정보 보호책임자 대표 강현진 · support@shouarchive.beakbig.com. 문의 메일로 받은 내용은 답변 · 문제 해결에만 쓰고 판매자 메일함에 보관 | 개인정보 처리방침 6 · 14항 |
| Cloudflare — 라이선스 서버와 사이트는 Cloudflare 가 전송 · 보안 목적으로 처리하며 판매자는 Cloudflare 요청 로그를 끄고 IP 를 저장하지 않음(D3 (가)). Paddle 은 Paddle.com Market Limited(영국 런던), 미국 거래는 Paddle.com Inc. — 7항에 한 번만 적고 다른 곳은 「Paddle(7항)」. 구매 페이지의 Paddle.js 가 처리하는 정보 고지. 앱은 `os_version` 을 더 보내지 않음 | 개인정보 처리방침 5 · 6 · 7 · 12항 |
| 키 발송 이메일 서비스 — Resend, Inc.(미국) | 개인정보 처리방침 6 · 12항 · 이용약관 7항 |
| 라이선스 등록 — 결제 완료 화면 · 메일의 등록 링크(사이트 중계 `/activate#key=` → 앱 확인 창) · 앱의 「키 입력…」(구매 이메일 + 키) · 앱에서 결제한 Mac 은 「자동 확인」. 결제만으로 Mac 이 등록되지 않음. 자리가 가득 차면 등록된 Mac(모델명 · 등록일 · 마지막 사용일)에서 해제(다른 Mac 해제는 30일에 3번). 키 다시 받기는 구매 이메일로만 같은 키 | 지원 FAQ · 구매 페이지 · 개인정보 처리방침 5항 |
| 국외 이전 — Cloudflare(미국) · Paddle(영국), 활성화 · 확인 · 결제 때 네트워크로. 저장 위치는 서버가 있는 미국과 데이터베이스의 아시아 · 태평양 지역. 보호 조치와 거부 방법(라이선스를 쓰지 않으면 이전 없음, 빌드 기능은 체험 기간 뒤 잠김) | 개인정보 처리방침 12항 |
| 좌석 해제 — 다른 Mac 으로 옮길 때 설정 › 라이선스 의 「해제」로 자리를 돌려준 뒤 새 Mac 에서 키 입력. Mac 이름이나 네트워크가 바뀌어도 같은 Mac 으로 계산 | 이용약관 3.2항 |
| 정지 통지 — 구매에 쓴 이메일 주소로 알림, 문의는 support@shouarchive.beakbig.com | 이용약관 11항 |

아직 정하지 않아 자리 표시로 남은 것 (한국어판 기준 — 다른 5개 언어는 새 한국어판으로 다시 번역할 예정):

- [ ] **대표자 · 사업장 주소 · 전화번호 · 통신판매업 신고번호** — `pricing.json` 의 `seller.owner` · `address` · `phone` · `mail_order` 를 채우고 `fill-pricing.py` 실행 (모든 페이지 바닥 · 이용약관 2항)
- [ ] **출시일** — `commercial.release_date`
- [ ] **Paddle client-side token · 가격 id 두 개** — `paddle.*` (채우기 전에는 구매 페이지가 「결제를 아직 열지 않았습니다」)
- [ ] 「광고 · 추적 · 행동 분석 SDK 없음」 — 근거 자료가 없어 남겼습니다 (개인정보 5항)
- [ ] 공유 범위 — 「라이선스 서버와 Paddle 외에는 넘기지 않는다」는 문장을 근거 자료로 확정할 수 없어 남겼습니다 (개인정보 9항 — 라이선스 서버 · Resend · Paddle 로 고쳐 두었고, 문장 확정만 남음)
- [ ] 출시 시 실제 지원 범위 — 빌드 · 업로드 · 기기 설치가 어디까지 지원하는지 (이용약관 3.3항)
- [ ] 국외 이전의 보호 조치 문구를 실제 계약(표준계약조항 등)에 맞춰 확정 — 개인정보 12항은 서술만 넣었고 조항 번호가 없습니다

## Paddle 가 판매자 웹사이트에 요구하는 것 — 확인 목록

Paddle 공식 문서(developer.paddle.com · paddle.com/help · paddle.com/legal)만 보고 적은 것입니다. 원문과 링크는 각 항목 뒤에 있습니다. 이 목록은 **확인용**이고, 위 초안 문서들이 근거입니다.

### 이 사이트가 이미 갖춰 둔 것

| Paddle 가 요구하는 것 | 이 사이트 | 상태 |
| --- | --- | --- |
| 상품 · 서비스 설명 | `index.html` · `pricing.html` | ✅ |
| 가격 정보 또는 가격 페이지 | `pricing.html` (체험 · 라이선스 카드, 체험 중 / 체험이 끝난 뒤 / 구매 후 기능표, 처음 구매 · 업데이트 갱신) | ✅ |
| 구매에 포함된 주요 기능 | `pricing.html` 비교표 · `index.html` | ✅ |
| 이용약관 (Terms) | `terms.html` (+ 영문 등 6개 언어) | ⚠️ 초안 |
| 환불 정책 (Refund Policy) | `refund.html` (+ 6개 언어) | ⚠️ 초안 · Paddle 표준 정책(`https://www.paddle.com/legal/refund-policy`)보다 불리해선 안 됨 |
| 개인정보 처리방침 (Privacy Policy) | `privacy.html` (+ 6개 언어) | ✅ 앱 하나 기준 (2026-10-15 시행) |
| 이 문서들이 웹사이트 탐색(메뉴)에서 명확히 드러남 | 모든 페이지 푸터: 홈 · 가격 · 다운로드 · 지원 · 개인정보 처리방침 · 이용약관 · 환불 정책 | ✅ |
| 이용약관에 회사명(개인사업자는 실명 권장) | `terms.html` 2항 「비그빅(Beakbig)」 · 사업자등록번호 | ⚠️ 대표자 실명 · 주소 채우기 |
| 사이트가 HTTPS로 공개되어 있음 | `https://shouarchive.beakbig.com/` | ✅ |

> 출처: Domain Review — https://www.paddle.com/help/start/account-verification/what-is-domain-verification

### 판매를 시작하기 전에 사용자가 해야 하는 일 (이 저장소 밖)

- [ ] **Paddle 계정 만들기 · 도메인 심사 신청** — `shouarchive.beakbig.com`(그리고 결제 링크를 열 도메인)을 제출해야 그 도메인에서만 결제를 시작할 수 있습니다. 심사 결과에 따라 Paddle 이 페이지의 문구 수정을 요구할 수 있습니다.
  - https://www.paddle.com/help/start/account-verification · https://developer.paddle.com/build/go-live-checklist
- [ ] **제품 · 가격 등록** — 상품 설명 · 세금 분류(`tax_category`, 기본값 `standard`) · 라이선스 가격(US$14, 1회) · 업데이트 가격(US$15, 1년마다 반복). 체험은 Paddle 이 아니라 앱이 처리하므로 Paddle 가격에 `trial_period` 를 넣지 않습니다. 가격 id 두 개를 `paddle.price_license` · `price_updates` 에 넣습니다.
  - https://developer.paddle.com/build/products/create-products-prices · https://developer.paddle.com/build/trials/create-trial
- [ ] **기본 결제 링크 · 공개 설정 넣기** — Paddle › Checkout settings 의 기본 결제 링크(default payment link)를 `https://shouarchive.beakbig.com/checkout` 으로 정합니다. 라이선스 서버가 만든 거래(`?_ptxn=…`)는 이 페이지에서 Paddle.js 가 열고, 그냥 들어온 방문자에게는 「구매하기」 버튼(라이선스 + 업데이트 두 항목, 오버레이 결제)을 보여 줍니다. client-side token 을 `paddle.client_token` 에, 실서비스로 바꿀 때는 `paddle.environment` 를 `production` 으로 바꾸고, 판매를 열 때 `commercial.checkout` 에 구매 페이지 주소를 넣습니다.
  - https://developer.paddle.com/build/transactions/default-payment-link
- [ ] **다운로드 링크(.dmg) 넣기** — 승인된 도메인에 파일을 올리고 `commercial.download` 에 경로를 넣습니다.
- [ ] **세금 표시 방식 정하기** — 가격에 세금을 포함(유럽형) / 별도(미국형) / 지역에 따라 자동 중 고릅니다. **Paddle 의무가 아니라 판매자 선택**입니다.
  - https://www.paddle.com/help/sell/tax/do-you-support-tax-inclusiveexclusive-pricing · https://developer.paddle.com/changelog/2025/automatic-tax-inclusive-exclusive-prices
- [ ] **정산 통화 정하기** — 고객이 지불할 통화와 정산 통화는 달라도 됩니다(고객은 지원 통화 어느 것으로든 결제 가능). 단 결제 통화별 최소 금액이 있습니다(USD 0.70 등).
  - https://www.paddle.com/help/start/set-up-paddle/how-do-i-change-my-default-(balance)-currency · https://developer.paddle.com/concepts/sell/supported-currencies
- [ ] **자동 갱신 끄기 경로 확인** — 업데이트 갱신은 Paddle 에서 반복 결제(subscription)로 처리되므로, Paddle 이 보내는 안내 메일과 고객 포털에 취소 링크가 이미 들어 있습니다. 앱의 설정 › 라이선스 › 「결제 관리…」 는 라이선스 서버(`/v1/licenses/manage`)에서 그 포털 링크를 받아 엽니다 — 문서(약관 4.4 · 환불 6항 · 가격 · 구매 페이지)가 두 경로를 함께 적고 있으니 포털 링크가 실제로 열리는지 확인합니다.
  - https://developer.paddle.com/build/subscriptions/cancel-subscriptions

### Paddle 가 정해 둔 사실 — 문서와 어긋나면 안 되는 것

- **Paddle 이 판매대행(Merchant of Record)입니다.** 고객은 Paddle 로부터 구매하고, 결제 수단 확인 · 세금 계산· 부과 · 영수증 발행 · 환불 처리를 Paddle 이 합니다. 판매자는 **고객에게 따로 청구서를 발행하거나 대금을 요구할 수 없습니다**(MSA 10.1). 여기 문서들은 그에 맞췄습니다.
  - https://www.paddle.com/legal/terms · https://www.paddle.com/help/sell/tax/how-paddle-handles-vat-on-your-behalf
- **반복 결제(업데이트 갱신)는 자동 갱신됩니다.** 고객이 끄기 전까지 같은 기간으로 계속 결제됩니다. 가격 인상 시에는 고지하고, 법이 요구하면 동의를 받습니다.
  - https://www.paddle.com/legal/buyer-terms
- **환불은 Paddle 이 최종 결정합니다.** 기본 정책은 「거래일로부터 14일 이내 요청 시 Paddle 이 재량으로 환불할 수 있으나 요청만으로 보장되지는 않으며, 법이 요구하는 경우 외에는 환불 불가」입니다. 지역별 법정 최소 기간(한국·브라질·중국 7일, EU/영국/스위스·터키·이스라엘 14일, 캐나다 7일, 싱가포르 5일)이 이보다 우선합니다. 환불되면 그 기간의 제품 접근은 종료됩니다. **저희 환불 정책은 Paddle 의 정책보다 불리해지면 안 됩니다.**
  - https://www.paddle.com/legal/refund-policy
- **환불은 Paddle 의 창구로.** 영수증·계정 결제 페이지의 지원 링크, 또는 paddle.net 의 「Request refund」로 요청합니다. 판매자가 직접 환불금을 송금하지 않습니다. 카드 환불은 보통 3–5 영업일, 결제 후 120일 이내 거래만 가능하고(페이팔 179일), 판매자가 수수료를 부담합니다.
  - https://www.paddle.com/help/manage/your-customers/how-do-i-issue-refunds
- **한국 고객은 갱신 동의 단계가 표시됩니다.** 무료 체험·할인 기간이 끝나면 계속 과금하려면 한국 공정위 규정에 따라 명시적 동의가 필요하며, 2025년 7월부터 Paddle 이 이 단계를 제공합니다.
  - https://developer.paddle.com/changelog/2026/subscription-consent-requirements
- **Paddle 의 체험은 가격에 붙는 항목이고 반복 결제가 필수입니다.** 이 판매 방식은 Paddle 체험을 쓰지 않습니다 — 14일 체험은 앱과 라이선스 서버가 결제 수단 없이 처리합니다.
  - https://developer.paddle.com/concepts/subscriptions/trials
- **한 결제 화면에 1회 가격과 반복 가격을 함께 넣을 수 있습니다.** 처음 구매는 라이선스(1회) + 업데이트(1년 반복) 두 항목입니다. 반복 항목끼리는 결제 주기가 같아야 합니다.
  - https://developer.paddle.com/build/products/create-products-prices
- **Paddle 은 라이선스 키를 발급해 주지 않습니다.** 다운로드 링크와 라이선스 발급은 판매자 쪽에서 직접 처리해야 합니다(웹훅으로 거래 · 반복 결제 상태를 받아 라이선스를 발급하고 업데이트 기간을 늘림). 여기 문서들은 그 전제로 「라이선스 서버」를 두었습니다.
  - https://developer.paddle.com/build/subscriptions/provision-access-webhooks

### 인라인 체크아웃을 쓸 경우 (이 사이트는 오버레이 결제를 씀 — 해당 없음)

자체 결제 화면(Paddle.js 인라인)을 만들면 Paddle 이 아래 다섯 가지를 직접 구현하라고 요구합니다: 반복 결제 주기와 갱신 시 결제 금액(체험이면 체험 기간), 구매하는 상품 설명, 소계·세금·합계와 통화가 표시된 금액, Paddle 약관·개인정보 처리방침이 포함된 결제 화면 푸터(Merchant of Record 표시), 그리고 **Paddle 표준 환불 정책과 다를 경우 우리 환불 정책 링크**. `checkout.html` 은 Paddle.js 의 **오버레이** 결제(Paddle 이 금액 · 세금 · 약관 표시까지 그리는 화면)를 쓰므로 해당 없음. 인라인으로 바꾸면 이 다섯 가지를 직접 구현해야 합니다.

- https://developer.paddle.com/build/checkout/brand-customize-inline-checkout · https://developer.paddle.com/changelog/2024/inline-checkout-compliance-changes

### 개인정보 — Paddle 측 처리와 우리에게 넘어오는 것

- Paddle 은 구매자에 대해 이름·주소·이메일·결제 수단 정보·결제 내역·IP 주소·기기 정보를 수집·처리합니다(자세는 Paddle 개인정보 처리방침).
- 데이터 공유 부속서에 따라 **판매자에게 넘어오는 것**은 구매자의 이름·주소·이메일, 구매 내역, 대시보드의 거래 분석입니다. **민감 정보 범주(특수 카테고리)는 공유되지 않습니다.** 양쪽은 각자 **독립적인 데이터 통제자**입니다.
- Paddle 은 법적 의무를 위해 거래 데이터를 5년 보관합니다.
- 따라서 개인정보 처리방침에는 Paddle 이 무엇을 수집하는지, 무엇이 우리에게 오는지, Paddle 이 판매대행이라는 점을 밝혀 두어야 합니다 → `privacy.html` 7항에 그 내용을 넣었습니다.

출처: https://www.paddle.com/legal/data-sharing-addendum · https://www.paddle.com/legal/privacy · https://www.paddle.com/help/manage/your-customers/requesting-buyer-data-deletion

### 「Made with Paddle」 배지 · 문구

필수라는 공식 근거를 찾지 못했습니다(MSA 5.1 은 로고 사용 *권리*만 부여). Paddle 이 수정을 요구할 수 있으니(MSA 9.2–9.3) 도메인 심사 결과에 따라 판단하세요.

### 공식 문서에서 확인하지 못한 것 (추정하지 말 것)

- 지원/문의 페이지의 필수 여부, 회사 주소의 명시 의무, 개인정보·이용약관·환불 정책의 필수 제목·문구.
- 가격 통화와 정산 통화가 같아야 한다는 요건 — 오히려 반대 문서(“고객은 어떤 통화로도 결제 가능”)가 있습니다.
- 「가격에 세금을 반드시 포함해야 한다」는 규칙 — 판매자 선택입니다.
- Paddle 기본 약관을 결제 화면에서 교체하거나 판매자 EULA 를 올리는 방법 — 공식 문서에 없습니다. 고객이 보는 것은 Paddle 구매자 약관 + 「공급자 약관(우리의 이용약관)」 참조입니다.
  - https://www.paddle.com/legal/buyer-terms

## 출시 체크리스트

지금 공개된 결제 페이지는 **Paddle 샌드박스**를 가리킵니다(`check-site.py` 가 경고로 알려 줍니다). 판매를 열기 전에 순서대로:

1. [ ] `tools/pricing.json` 의 `paddle.environment` 를 `production`, `paddle.client_token` 을 라이브 client-side token(`live_…`), `paddle.price_license` · `price_updates` 를 라이브 가격 id 로 바꾼다 → `python3 tools/fill-pricing.py`. `check-site.py` 의 샌드박스 경고가 사라져야 한다.
2. [ ] 라이선스 서버(`~/Developer/shouarchive-license`)의 `PADDLE_ENVIRONMENT` 와 Paddle 시크릿(API 키 · 웹훅 비밀값)을 production 으로 바꾸고 배포한다. 라이브 웹훅 주소를 Paddle 대시보드에 등록한다.
3. [ ] 샌드박스로 생긴 라이선스 · 결제 · Mac · 알림 · 발송 기록을 서버 데이터베이스에서 정리한다 — 서버 저장소 `scripts/` 의 정리 스크립트 참고. 테스트 구매 이메일로 `erase.html` 을 돌려 보는 것도 방법이다.
4. [ ] `commercial.checkout`(`https://shouarchive.beakbig.com/checkout`) · `commercial.download`(`.dmg` 주소) · `commercial.download_sha256`(`shasum -a 256 ShouArchive.dmg`) · `commercial.release_date` 를 채운다 → `fill-pricing.py`. 「출시 예정」 안내가 사라지고 구매 · 다운로드 버튼과 SHA-256 줄이 나타나는지 본다.
5. [ ] `python3 tools/check-site.py` 통과(경고 0건). `python3 tools/localize-nav.py` · `python3 tools/mail-links.py` 도 한 번씩.
6. [ ] **DMG 호스팅을 정한다** — GitHub Releases(저장소 `BeakBig/…` 의 Release 자산, 다운로드가 GitHub 을 거침) vs Cloudflare R2(판매자 계정, 커스텀 도메인 가능). 정한 뒤 **개인정보 처리방침의 제3자 목록(3 · 9 · 12항)** 에 다운로드 호스트(GitHub, Inc. 또는 Cloudflare R2)와 그때 처리되는 정보(IP · User-Agent 등 접속 기록)를 추가하고, Sparkle 업데이트 목록(`SUFeedURL`)이 같은 곳을 가리키는지 확인한다(W19).
7. [ ] 법률 문서 세 개의 시행일을 공개하는 날짜로 바꾼다(`terms.html` · `refund.html` · `privacy.html` 의 hero · `p.meta`, 6개 언어).
8. [ ] 푸시 뒤 공개 주소에서 확인: `curl -sI https://shouarchive.beakbig.com/checkout | grep -i content-security` 에 CSP 가 보이고, `/checkout` 에서 결제 창이 실제로 열리는지(광고 차단기를 켠 브라우저에서는 「결제 모듈을 불러오지 못했습니다」 가 뜨는지), `/없는주소` 가 404.html 인지.
9. [ ] Paddle 라이브 대시보드 › Retain 설정 Step 4 「Check Paddle.js installation」 에 `https://shouarchive.beakbig.com/en/billing` 을 넣고 Check → Step 5 Live. 1번(라이브 client token)이 배포된 뒤에야 통과한다 — 샌드박스 토큰으로는 라이브 Retain 이 설치를 알아보지 못한다. Step 1 – 3(보내는 사람 `support@shouarchive.beakbig.com` 확인)은 2026-10-23 에 끝냈다.

## 올리기

```bash
git add -A && git commit -m "..." && git push
```

**`deploy` 브랜치에 푸시하면** Cloudflare 빌드가 `npx wrangler deploy` 로 1분 안팎에 shouarchive.beakbig.com 에 올립니다 (GitHub Pages 원본에도 1분 안팎). 다른 브랜치(`release/*` 등)는 공개되지 않으니, 공개할 때 `deploy` 에 병합합니다. 공개 브랜치 이름은 2026-10-21 에 `main` → `deploy` 로 바꿨습니다 — Cloudflare 대시보드의 빌드 브랜치도 `deploy` 여야 합니다.

### 주의 — 배포 구조와 빌드가 실패했던 일

- `shouarchive.beakbig.com` 을 서비스하는 것은 Cloudflare 계정의 **`shouarchive` Worker**(정적 파일만)입니다. 이 저장소에 푸시하면 Cloudflare 빌드가 저장소 루트를 그대로 정적 파일로 올립니다 — 설정은 루트 `wrangler.jsonc`, 올리지 않을 파일은 `.assetsignore`, 응답 헤더(CSP 등)는 `_headers`, 없는 주소는 `404.html`. 예전 프록시 Worker 안(`worker/`)은 2026-10-20 에 지웠습니다.
- **2026-10-03 빌드 실패**: `.assetsignore` 가 없어 `.git` 까지 올리다가 `.git` 압축 파일(29.1 MiB)이 Workers 파일 한도 **25 MiB** 를 넘어 실패했고, 공개 주소는 예전 내용 · 새 파일 404 로 남았습니다. `.assetsignore` 에 `.git` 등을 넣어 해결.
- `.assetsignore` · `wrangler.jsonc` · `_headers` 를 지우지 마세요(`_headers` 를 `.assetsignore` 에 넣어도 안 됩니다 — `check-site.py` 가 봅니다). 정적 파일 하나도 25 MiB 를 넘으면 안 됩니다 (스크린샷은 장당 1 MB 안팎).
- 푸시한 뒤에는 공개 주소에서 새로 넣은 파일이 열리는지 확인하세요. 예: `curl -sI https://shouarchive.beakbig.com/assets/screenshots/ko/10.png` 가 200 인지. 반영되지 않으면 Cloudflare 대시보드 › Workers & Pages › `shouarchive` › Deployments · Builds 의 빌드 로그를 봅니다 (빌드 로그는 대시보드에서만 보입니다).
- GitHub Pages 원본(`beakbig.github.io/shouarchive-site/`)은 `_headers` 를 무시하므로 CSP 가 없습니다. 공개 주소는 Cloudflare 쪽만 알립니다.

## 남은 일

- 「출시 체크리스트」 절의 항목.
- 저장소 이름을 바꾸면 GitHub Pages 원본 주소가 바뀝니다(Cloudflare 쪽은 영향 없음).
