# ShouArchive 홈페이지

ShouArchive(macOS) 의 소개 · 지원 · 개인정보 처리방침 페이지입니다. 순수 정적 HTML/CSS 이고 빌드 단계가 없습니다.

- 공개 주소: https://shouarchive.beakbig.com/ — Cloudflare 에서 이 저장소를 서브도메인에 연결해 서비스 중 (`.html` 주소는 확장자 없는 주소로 307 리다이렉트되므로 외부에 알릴 때는 `/support`, `/privacy` 처럼 확장자 없이)
- 원본(GitHub Pages): https://beakbig.github.io/shouarchive-site/ (`main` 브랜치 루트, Worker 배포 전에도 이 주소는 열립니다)
- 저장소: `BeakBig/shouarchive-site` (공개)

## 구성

| 경로 | 내용 |
| --- | --- |
| `index.html` · `pricing.html` · `download.html` | 한국어 랜딩 · 가격(체험 · 구매 후 기능표) · 다운로드 |
| `support.html` · `privacy.html` · `terms.html` · `refund.html` | 한국어 지원(FAQ) · 개인정보 처리방침 · 이용약관 · 환불 정책 |
| `checkout.html` | 한국어 구매 페이지 — Paddle 의 「기본 결제 링크(default payment link)」. 「구매하기」 는 라이선스 서버에 결제를 만들고(`/v1/web/checkout`, 실패하면 예전처럼 가격 id 로) Paddle.js 오버레이를 엽니다. `?_ptxn=` 거래(라이선스 서버가 만든 갱신 · 앱 안 구매)는 Paddle.js 가 스스로 엽니다. 결제가 끝나면(`checkout.completed`) 「결제를 확인하고 있습니다」 카드(앱과 같은 Lottie 퍼즐 로딩 — 못 불러오면 도는 원)를 띄우고 `#claim` 확인 값으로 키를 받아 와 「ShouArchive 에서 열기」 · 「키 복사」 를 보여 주고, 앱에서 시작한 결제(`from=app`)면 앱을 바로 엽니다. 1분(2초 간격)이 지나도 키가 없으면 「결제는 완료되었습니다 — 메일함 · 스팸함을 확인하고, 안 오면 support@beakbig.com 으로」 안내(`checkout-slow`)로 바꾸고, 페이지를 열어 둔 동안 5초 간격으로 5분 더 확인해 준비되면 키를 보여 줍니다. 갱신(`#kind=renewal`)은 기간 연장 안내. 서버가 키를 보관하지 않거나 확인 값이 맞지 않으면 메일 안내. `?done=1`(예전 successUrl)도 메일 안내. 메뉴에는 넣지 않습니다 |
| `activate.html` | 메일의 「앱에서 바로 등록하기」 링크가 여는 중계 페이지 — `#key=` 의 키를 보여 주고 `shouarchive://activate?key=…` 로 앱을 엽니다(Mac 데스크톱에서만 저절로, 휴대폰에서는 버튼만). 키는 `#` 뒤라 서버로 가지 않고, 읽은 뒤 주소에서 지웁니다. 메뉴에 넣지 않고 검색에서 뺍니다(`noindex`) |
| `license.html` | 키 다시 받기 — 구매 이메일을 받아 라이선스 서버(`/v1/licenses/resend`)에 보냅니다. 서버는 늘 같은 답을 주고 구매 이메일로만 같은 키를 보냅니다. 메뉴에 넣지 않습니다(`noindex`, 메일 · 지원 FAQ · 앱에서 링크) |
| `rotate.html` | 키 바꾸기(2026-10-17) — 키가 남에게 알려진 것 같을 때. 그냥 열면 구매 이메일을 받아 확인 메일을 요청하고(`/v1/licenses/rotate`), 메일의 링크(`#token=`)로 열면 「키 바꾸기」 단추를 보여 줍니다 — **단추를 눌러야** 바뀝니다(`/v1/licenses/rotate/confirm`, 메일 보안 검사기가 링크를 미리 열어도 그대로). 새 키는 페이지에 보여 주지 않고 구매 이메일로만 갑니다. 확인 값은 읽은 뒤 주소에서 지웁니다. 쓴 · 만료된 링크면 안내와 함께 요청 양식을 보여 줍니다. 새 Mac 등록 알림 메일의 「내가 아니라면」 링크도 여기로 옵니다. `noindex` |
| `en/` · `ja/` · `zh-Hans/` · `zh-Hant/` · `es/` | 영어 · 일본어 · 중국어 간체 · 번체 · 스페인어판 (같은 열한 페이지) |
| `assets/style.css` | 공용 스타일 (라이트 · 다크) |
| `assets/license.js` | 결제 완료 화면 · `activate.html` · `license.html` · `rotate.html` 이 함께 쓰는 스크립트 (언어 중립 — 문구는 각 페이지 HTML 에 있고 보이기 · 숨기기 · 값 채우기만 합니다). 라이선스 서버 주소는 `#paddle-config` 의 `data-license-api`, 없으면 기본값 `https://license.beakbig.com`. 서버 계약은 라이선스 서버 저장소 `docs/app-contract.md` §2.10 – §2.13 |
| `assets/vendor/lottie_light.min.js` | [lottie-web](https://github.com/airbnb/lottie-web) 5.12.2 의 light(SVG) 빌드 — 결제 확인 중 그림. npm 에서 받아 무결성(sha512)을 확인했고 라이선스는 `assets/vendor/lottie-web-LICENSE.md`(MIT). 외부 CDN 을 쓰지 않으려고 사이트에 둔다. 결제 확인 카드를 띄울 때만 불러온다 |
| `assets/loading/puzzle_loading.json` | 앱의 로딩 표시와 같은 Lottie 퍼즐 — 앱 저장소 `ShouArchive/Resources/Loading/puzzle_loading.json` 의 사본(앱 쪽을 바꾸면 같이 바꾼다) |
| `assets/icon.png` · `icon-64.png` | 앱 아이콘 |
| `assets/screenshots/<언어>/` | 갤러리 스크린샷 `01.png` ~ `06.png` (2880×1800), 6개 언어 |
| `assets/samples/` | 심사 · 테스트용 합성 APK · AAB |
| `.nojekyll` | GitHub Pages 가 Jekyll 처리 없이 그대로 서빙하게 함 |
| `worker/` | `shouarchive.beakbig.com` 을 이 사이트로 잇는 Cloudflare Worker 와 배포 설명 |
| `tools/localize-nav.py` | 모든 페이지의 6개 언어 전환 메뉴 · 헤더 · 푸터 링크 · `hreflang` 을 다시 맞추는 스크립트 (페이지를 고치거나 언어를 더하면 다시 실행) |
| `tools/pricing.json` · `tools/fill-pricing.py` | 가격 · 링크 · Paddle 공개 설정 · 판매자 정보의 유일한 출처와, 그 값을 페이지에 넣는 스크립트 |
| `tools/mail-links.py` | 모든 페이지의 support 메일 링크에 제목 「[ShouArchive][<페이지 코드>] <제목>」(제목이 없으면 언어별 「문의」 — 앱의 문의 메일 `[ShouArchive][이슈] …` 과 같은 모양)과 본문 맨 아래 「보낸 페이지: 주소 (코드)」 를 붙이는 스크립트. 페이지 코드(언어 무관, 메일 필터가 쓴다): `W-HOME` 홈 · `W-PRICE` 가격 · `W-DL` 다운로드 · `W-SUP` 지원 · `W-PRIV` 개인정보 · `W-TERMS` 약관 · `W-REFUND` 환불 · `W-BUY` 구매 · `W-ACT` 앱에서 등록 · `W-KEY` 키 다시 받기 · `W-ROTATE` 키 바꾸기. 메일 링크를 더하거나 페이지를 고치면 다시 실행(여러 번 돌려도 같다) |
| `tools/check-site.py` | 사이트 전체 점검 — 6개 언어 × 11개 페이지 구조 · 링크 · 번역 누락 · 가격 키 · Paddle 설정 · 25 MiB 한도 |

ShouArchive 는 이 사이트에서만 판매합니다 (2026-10-15 결정 — Mac App Store 판은 출시하지 않고 제출을 거둬들임). 그래서 `pricing.json` 에는 `appstore.*` 키가 없습니다. 다른 5개 언어 페이지는 새 한국어판으로 다시 번역하기 전까지 `appstore.*` 를 가리키므로 `fill-pricing.py` 가 그 자리를 「pricing.json 에 없는 키」로 알리고 코드 1 로 끝납니다 — 번역을 마치면 사라집니다.

외부에 알리는 주소:

- 지원: `https://shouarchive.beakbig.com/support` (다른 언어는 `<언어>/support`)
- 홈: `https://shouarchive.beakbig.com/` (다른 언어는 `<언어>/`)
- 개인정보 처리방침: `https://shouarchive.beakbig.com/privacy` (다른 언어는 `<언어>/privacy`)

## 가격 · 링크는 한 곳에서 바꾸기

가격 숫자 · 체험 기간 · 결제 링크 · 다운로드 링크 · Paddle 공개 설정 · 판매자(사업자) 정보는 **`tools/pricing.json` 한 곳에만** 적습니다. 페이지에는 자리 표시만 두고, `tools/fill-pricing.py` 가 그 값을 넣어 줍니다.

```bash
python3 tools/fill-pricing.py   # pricing.json → 모든 언어 페이지
python3 tools/localize-nav.py    # 언어 전환 · 헤더 · 푸터 · hreflang 다시 맞추기
python3 tools/check-site.py      # 6개 언어 × 11개 페이지 구조 · 링크 · 번역 · 용량 점검
```

페이지에 쓰는 표시 네 가지:

| 표시 | 쓰임 |
| --- | --- |
| `<span data-price="commercial.price">US$29</span>` | 글자 사이에 넣기. 값이 `null` 일 때 — `commercial.*` 키는 `undecided` 에 있는 그 언어 문장(「가격 미정」)을 넣고(정하지 않은 금액이 숫자로 남지 않게), `seller.*` 같은 다른 키는 페이지의 주황색 자리 표시(`<span class="placeholder" data-price="seller.owner">[대표자]</span>`)를 그대로 둡니다. 값이 채워지면 `placeholder` class 도 떼어 냅니다. pricing.json 에 없는 키는 건드리지 않고 마지막에 목록으로 알립니다(종료 코드 1) |
| `<a data-src="commercial.checkout" href="#">` | 링크. JSON 이 비어 있으면 `hidden` 으로 숨겨 두었다가, 값을 채우면 `href` 가 바뀌면서 스스로 나타납니다 |
| `data-live-hide` / `data-live-show` | 출시 전에만 보이는 문장 / 공개된 뒤에 보이는 문장. 공개 여부는 `commercial.checkout` 이 채워져 있는지로 판단합니다 |
| `<div id="paddle-config" data-env data-token data-price-license data-price-updates data-license-api hidden>` | `checkout.html` 의 Paddle.js 설정과 라이선스 서버 주소. 실행할 때마다 `paddle.*` 값으로 속성을 다시 씁니다(값을 바꿔 다시 실행하면 그대로 반영) |

`pricing.json` 의 키:

| 키 | 뜻 |
| --- | --- |
| `commercial.price` · `price_renewal` | 처음 구매(라이선스 + 업데이트 1년, US$29) · 업데이트 1년 갱신(US$15, 자동 갱신). 세금 별도 |
| `commercial.devices` · `refund_days` | 라이선스 하나로 쓰는 Mac 수(2) · 결제 후 전액 환불 기간(14일) |
| `commercial.release_date` | 출시일 — 아직 `null` |
| `commercial.checkout` · `download` | 구매 페이지 주소(보통 `checkout.html`) · `.dmg` 주소. `checkout` 이 채워지면 출시(판매 시작)로 봅니다 — 「출시 예정」 안내가 사라지고 구매 · 다운로드 버튼이 나타납니다 |
| `paddle.environment` | `sandbox` 또는 `production` |
| `paddle.client_token` | Paddle 의 **client-side token**(`test_…` / `live_…`). 비어 있으면 `checkout.html` 은 「결제를 아직 열지 않았습니다」만 보여 줍니다 |
| `paddle.price_license` · `price_updates` | 가격 id(`pri_…`) — 라이선스(US$14, 1회) · 업데이트 1년(US$15, 매년 자동 갱신). 처음 구매 화면에 두 항목을 함께 넣어 합계 US$29 (라이선스 서버에 닿지 못할 때만 이 값으로 직접 엽니다) |
| `paddle.license_api` | 라이선스 서버 주소(`https://license.beakbig.com`) — 결제 완료 화면이 키를 받아 오고 사이트 결제를 만듭니다. 라이선스 서버의 `SITE_ORIGINS` 에 이 사이트 주소가 있어야 브라우저가 부를 수 있습니다(CORS). `activate.html` · `license.html` · `rotate.html` 은 `assets/license.js` 의 기본값을 쓰므로 주소를 바꾸면 거기도 고칩니다 |
| `seller.reg_no` · `owner` · `address` · `phone` · `mail_order` | 페이지 바닥 사업자 정보와 이용약관 2항. 사업자등록번호(613-40-01820)만 정해졌고 나머지는 `null`(주황색 자리 표시) |
| `contact.email` | 문의 주소 `support@beakbig.com` |

> **Paddle 값 중 사이트에 넣어도 되는 것은 client-side token 과 가격 id 뿐입니다** — 둘 다 브라우저에 그대로 보이는 공개 값입니다. **API 키(`pdl_…`)와 웹훅 비밀값(notification secret)은 절대 `pricing.json` 이나 페이지에 넣지 마세요.** 라이선스 서버의 비밀값(Cloudflare Workers secret)으로만 둡니다.

> 숨길 때 쓰는 `hidden` 속성이 CSS 의 `display` 규칙에 밀리지 않게 `assets/style.css` 에 `[hidden] { display: none !important; }` 규칙이 있습니다. 이 규칙을 지우면 출시 전 구매 · 다운로드 버튼이 그대로 보입니다(`check-site.py` 가 확인합니다).

새 페이지를 만들면 `tools/localize-nav.py` 와 `tools/check-site.py` 의 `PAGES` 에 파일 이름을 추가하고 그 페이지를 만들고, 스크립트를 한 번씩 실행하세요. `check-site.py` 가 번역이 밀렸거나 링크가 끊긴 페이지를 찾아냅니다 — 6개 언어 × 11개 페이지 = 66개 파일이 모두 같은 구조여야 통과합니다.

모든 페이지 바닥(`<footer>` 안 `<p class="biz">`)에 사업자 정보(상호 · 대표 · 사업자등록번호 · 통신판매업 신고 · 주소 · 전화 · 이메일 · 결제 대행 Paddle)가 있습니다. `localize-nav.py` 는 바닥의 `<nav>` 만 다시 쓰므로 이 줄은 건드리지 않습니다.

## ⚠️ 법률 문서는 초안입니다 — 검토 후, 발행 전에 고치세요

`terms.html`(이용약관) · `refund.html`(환불 정책) · `privacy.html`(개인정보 처리방침 — 앱 하나 기준으로 합침)는 **법률 검토를 거치지 않은 초안**입니다. **이 문서를 검토하기 전에는 Paddle 판매를 시작하지 마세요.** 주황색(`<span class="placeholder">`)으로 표시한 자리는 아직 판매자가 정하지 못한 값입니다.

이미 정해 둔 것 (초안에 반영되어 자리 표시가 지워짐):

| 정한 내용 | 들어간 곳 |
| --- | --- |
| 판매자 — 상호 비그빅(Beakbig) · 사업자등록번호 613-40-01820(간이과세자) · support@beakbig.com | 이용약관 2항 · 모든 페이지 바닥 |
| 요금 — 처음 구매 US$29(라이선스 + 업데이트 1년, Mac 2대), 업데이트 갱신 1년 US$15(자동 갱신 · 언제든 끄기), 기간 안에 나온 버전은 영구 사용, 기간 뒤 버전은 갱신해야 설치, 끊긴 뒤 갱신하면 결제일부터 1년 | 가격 페이지 · 이용약관 1 · 3.2 · 4항 |
| 체험 — 14일, 결제 수단 없이 앱 안에서 시작, 자동 결제 없음. 키 없이 끝나면 프로파일 관리 · 산출물 검사만 | 가격 페이지 · 이용약관 4.3항 · 환불 정책 3항 |
| 만 14세 이상(14세 미만은 법정대리인 동의), 지역 제한 없음(Paddle 판매 불가 지역 제외) | 이용약관 3.1항 |
| 라이선스당 Mac 2대 | 이용약관 3.2항 |
| 가격은 세금 별도 표시, 결제 시 Paddle 이 지역에 맞춰 자동 계산 | 이용약관 4.1항 · 가격 페이지 |
| 환불 — 처음 구매 · 갱신 모두 결제 후 14일 안 전액(한국 청약철회 기간과 같음). 처음 구매 환불은 라이선스 해지, 갱신 환불은 업데이트 기간만 1년 되돌림. chargeback 은 라이선스 해지. 14일 뒤는 법이 정한 경우 외 환불 없음 | 환불 정책 4 – 9항 |
| 책임 상한 — 최근 12개월 동안 고객이 낸 금액까지. 고의 · 중대한 과실은 제한하지 않음 | 이용약관 10.2항 |
| 자동 갱신 끄기 — 언제든 Paddle 결제 안내 메일의 관리 링크에서, 꺼도 앱은 계속 씀. 위반은 이메일로 알린 뒤 정지 | 이용약관 4.4 · 11항 |
| 준거법 — 대한민국 법, 1심 관할은 판매자 주소지 관할 법원, 중재 조항 없음, 소비자가 사는 나라의 강행 소비자 보호 규정 그대로 적용 | 이용약관 12항 |
| 개인정보 권리 처리 기한 — 요청을 받은 날부터 10일 이내 · 적용 관할은 대한민국 개인정보 보호법, EU · EEA · 영국 이용자에게는 GDPR · UK GDPR 의 권리도 보장 | 개인정보 처리방침 11항 |
| 개인정보 5항 「사용자 이름 · 기기에 직접 붙인 이름은 쓰지 않습니다」 — 확정했습니다. 기기 식별값이 이미 해시된 값이라 사실과 맞습니다 | 개인정보 처리방침 5항 |
| 라이선스 서버 — 운영 주체 비그빅(Beakbig) · 613-40-01820 · support@beakbig.com, 서버는 Cloudflare, Inc.(미국)의 Workers, 데이터베이스는 아시아 · 태평양 지역(그 지역 안의 실제 위치는 Cloudflare 가 정함), 결제는 Paddle.com Market Limited(영국)가 판매대행 | 이용약관 7항 · 개인정보 처리방침 6항 |
| 기기 식별값 — 하드웨어 UUID 에 앱 전용 접두어를 붙여 SHA-256 으로 바꾼 값의 앞 32자. 하드웨어 UUID 원문 · 호스트 이름 · 사용자 이름은 서버로 보내지 않으며, 하드웨어 UUID 를 못 읽으면 첫 실행 때 만든 무작위 설치 id 를 같은 방식으로 씁니다. Mac 이름이나 네트워크가 바뀌어도 값은 그대로 | 개인정보 처리방침 5항 |
| 저장 방식 — 기기 · 설치 식별값은 HMAC-SHA256 해시만. 라이선스 키는 조회용 SHA-256 해시와 함께 같은 키를 다시 보내려고 AES-256-GCM 암호문으로 보관(열쇠는 DB 밖 Workers secret — 2026-10-16 결정, 이전 「해시만」 문구를 고침). 결제 확인 값 · 키 다시 받기 이메일은 해시만. Mac 모델명 · 앱 버전 · 구매 이메일은 원문 그대로. 저장하지 않는 것(IP · 요청 헤더와 본문 · macOS 버전 · 이름/주소 · 카드 번호 · 마케팅 동의 · 사용 통계)도 5항에 있음 | 개인정보 처리방침 5항 (시행일 2026-10-17) |
| 보관 기간 — 접근 기록 30일 · 결제 알림 처리 기록 90일 · 키 발송 기록 365일 · 발급 대기 7일 · 결제 확인 기록 30일 · 다른 Mac 해제 기록 30일 · 키 다시 받기 요청 1일은 매일 자동 삭제, 라이선스 · 기기 · 이메일은 라이선스가 있는 동안 보관하고 환불 · chargeback 으로 해지된 뒤 2년(또는 삭제 요청 시) 삭제 또는 익명화 | 개인정보 처리방침 6항 |
| 키 발송 이메일 서비스 — Resend, Inc.(미국) | 개인정보 처리방침 6 · 12항 · 이용약관 7항 |
| 라이선스 등록 — 결제 완료 화면 · 메일의 등록 링크(사이트 중계 `/activate#key=` → 앱 확인 창) · 앱의 「키 입력…」(구매 이메일 + 키) · 앱에서 결제한 Mac 은 「자동 확인」. 결제만으로 Mac 이 등록되지 않음. 자리가 가득 차면 등록된 Mac(모델명 · 등록일 · 마지막 사용일)에서 해제(다른 Mac 해제는 30일에 3번). 키 다시 받기는 구매 이메일로만 같은 키 | 지원 FAQ · 구매 페이지 · 개인정보 처리방침 5항 |
| 국외 이전 — Cloudflare(미국) · Paddle(영국), 활성화 · 확인 · 결제 때 네트워크로. 저장 위치는 서버가 있는 미국과 데이터베이스의 아시아 · 태평양 지역. 보호 조치와 거부 방법(라이선스를 쓰지 않으면 이전 없음, 빌드 기능은 체험 기간 뒤 잠김) | 개인정보 처리방침 12항 |
| 좌석 해제 — 다른 Mac 으로 옮길 때 설정 › 라이선스 의 「해제」로 자리를 돌려준 뒤 새 Mac 에서 키 입력. Mac 이름이나 네트워크가 바뀌어도 같은 Mac 으로 계산 | 이용약관 3.2항 |
| 정지 통지 — 구매에 쓴 이메일 주소로 알림, 문의는 support@beakbig.com | 이용약관 11항 |

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
- [ ] **자동 갱신 끄기 경로 확인** — 업데이트 갱신은 Paddle 에서 반복 결제(subscription)로 처리되므로, Paddle 이 보내는 안내 메일과 고객 포털에 취소 링크가 이미 들어 있습니다. 별도 취소 UI를 만들 필요는 없습니다.
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

- Cloudflare Worker 배포 (`worker/README.md`) — 이것이 끝나야 `https://shouarchive.beakbig.com/` 가 열립니다.
- 저장소 이름을 바꾸면 GitHub Pages 원본 주소가 바뀌므로 `worker/wrangler.toml` 의 `UPSTREAM` 도 함께 고쳐야 합니다.
