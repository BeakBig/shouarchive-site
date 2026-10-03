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
| `tools/check-site.py` | 사이트 전체 점검 — 6개 언어 × 7개 페이지 구조 · 링크 · 번역 누락 · 25 MiB 한도 |

App Store Connect 에 넣는 URL:

- 지원: `https://shouarchive.beakbig.com/support` (다른 언어는 `<언어>/support`)
- 마케팅: `https://shouarchive.beakbig.com/` (다른 언어는 `<언어>/`)
- 개인정보 처리방침: `https://shouarchive.beakbig.com/privacy` (다른 언어는 `<언어>/privacy`)

## 가격 · 링크는 한 곳에서 바꾸기

가격 숫자 · 체험 기간 · 결제 링크 · 다운로드 링크는 **`tools/pricing.json` 한 곳에만** 적습니다. 페이지에는 자리 표시만 두고, `tools/fill-pricing.py` 가 그 값을 넣어 줍니다.

```bash
python3 tools/fill-pricing.py   # pricing.json → 모든 언어 페이지
python3 tools/localize-nav.py    # 언어 전환 · 헤더 · 푸터 · hreflang 다시 맞추기
python3 tools/check-site.py      # 6개 언어 × 7개 페이지 구조 · 링크 · 번역 · 용량 점검
```

페이지에 쓰는 표시 세 가지:

| 표시 | 쓰임 |
| --- | --- |
| `<span data-price="appstore.price_now">US$2</span>` | 글자 사이에 넣기 (JSON 값이 `null` 이면 페이지에 적힌 문장을 그대로 둡니다 — 각 언어 표현) |
| `<a data-src="commercial.checkout" href="#">` | 링크. JSON 이 비어 있으면 `hidden` 으로 숨겨 두었다가, 값을 채우면 `href` 가 바뀌면서 스스로 나타납니다 |
| `data-live-hide` / `data-live-show` | 상용 판 공개 전에만 보이는 문장 / 공개된 뒤에 보이는 문장. 공개 여부는 `commercial.checkout` 이 채워져 있는지로 판단합니다 |

값이 `null` 이거나 빈 문자열인 항목은 **상용 판이 아직 없다는 뜻**입니다 — 가격이 정해지면 `commercial.price_monthly` 같은 값을 채우고 `commercial.checkout`(Paddle 결제 링크)을 넣습니다. 그러면 「출시 예정」 안내가 자동으로 사라지고 구매 · 다운로드 버튼이 나타납니다.

새 페이지를 만들면 `tools/localize-nav.py` 의 `PAGES` 에 파일 이름을 추가하고 그 페이지를 만들고, 두 스크립트를 한 번씩 실행하세요. `check-site.py` 가 번역이 밀렸거나 링크가 끊긴 페이지를 찾아냅니다 — 6개 언어 × 7개 페이지 = 42개 파일이 모두 같은 구조여야 통과합니다.

## ⚠️ 법률 문서는 초안입니다 — 검토 후, 발행 전에 고치세요

`terms.html`(이용약관) · `refund.html`(환불 정책) · `privacy.html`(개인정보 처리방침 — 상용 판 내용 추가)는 **법률 검토를 거치지 않은 초안**입니다. 특히 주황색(`<span class="placeholder">`)으로 표시한 자리는 판매자가 정해야 하는 값이라 비워 두었습니다. **이 문서를 검토하기 전에는 Paddle 판매를 시작하지 마세요.** 발행 전에 최소한 다음을 결정하거나 전문가의 검토가 필요합니다.

- [ ] 사업자 정보 — 고유번호 · 주소 · 연락처 (이용약관 2항, 페이지 바닥에 고지)
- [ ] 라이선스 서버 — 운영 주체 · 위치 · 보관 기간 (이용약관 8항, 개인정보 10항)
- [ ] 기기 식별값 — 실제 무엇을 보내는지 (개인정보 9항 표)
- [ ] 환불 기준 — 부분 환불 · 연간 구독 · 취소 기한 (환불 정책 4항)
- [ ] 중재 조항과 준거법 — (이용약관 13항)
- [ ] 책임 상한 기준 (이용약관 11.2항)
- [ ] 개인정보 주체 권리 처리 기한 · 적용 관할 (개인정보 12항)
- [ ] 세금 표시 방식 — 포함 / 별도 / 지역에 따라 자동 (가격 페이지 「결제 · 구독 안내」)

## Paddle 가 판매자 웹사이트에 요구하는 것 — 확인 목록

Paddle 공식 문서(developer.paddle.com · paddle.com/help · paddle.com/legal)만 보고 적은 것입니다. 원문과 링크는 각 항목 뒤에 있습니다. 이 목록은 **확인용**이고, 위 초안 문서들이 근거입니다.

### 이 사이트가 이미 갖춰 둔 것

| Paddle 가 요구하는 것 | 이 사이트 | 상태 |
| --- | --- | --- |
| 상품 · 서비스 설명 | `index.html` · `pricing.html` | ✅ |
| 가격 정보 또는 가격 페이지 | `pricing.html` (두 판 비교표 · 월/연간 · 체험) | ✅ 상용 판 가격은 미정 — 공개 전에 채움 |
| 구매에 포함된 주요 기능 | `pricing.html` 비교표 · `index.html` | ✅ |
| 이용약관 (Terms) | `terms.html` (+ 영문 등 6개 언어) | ⚠️ 초안 |
| 환불 정책 (Refund Policy) | `refund.html` (+ 6개 언어) | ⚠️ 초안 · Paddle 표준 정책(`https://www.paddle.com/legal/refund-policy`)보다 불리해선 안 됨 |
| 개인정보 처리방침 (Privacy Policy) | `privacy.html` (+ 6개 언어) | ✅ App Store 판 · 상용 판 모두 |
| 이 문서들이 웹사이트 탐색(메뉴)에서 명확히 드러남 | 모든 페이지 푸터: 홈 · 가격 · 다운로드 · 지원 · 개인정보 처리방침 · 이용약관 · 환불 정책 | ✅ |
| 이용약관에 회사명(개인사업자는 실명 권장) | `terms.html` 2항 「BeakBig」 | ⚠️ 실제 등록 상호로 확정 |
| 사이트가 HTTPS로 공개되어 있음 | `https://shouarchive.beakbig.com/` | ✅ |

> 출처: Domain Review — https://www.paddle.com/help/start/account-verification/what-is-domain-verification

### 상용 판을 파기 전에 사용자가 해야 하는 일 (이 저장소 밖)

- [ ] **Paddle 계정 만들기 · 도메인 심사 신청** — `shouarchive.beakbig.com`(그리고 결제 링크를 열 도메인)을 제출해야 그 도메인에서만 결제를 시작할 수 있습니다. 심사 결과에 따라 Paddle 이 페이지의 문구 수정을 요구할 수 있습니다.
  - https://www.paddle.com/help/start/account-verification · https://developer.paddle.com/build/go-live-checklist
- [ ] **제품 · 가격 등록** — 상품 설명 · 세금 분류(`tax_category`, 기본값 `standard`) · 월 가격 · 연간 가격 · 14일 체험. 체험은 가격이 반복 결제로 설정된 **가격**에 붙는 항목입니다(별도 상품이 아님).
  - https://developer.paddle.com/build/products/create-products-prices · https://developer.paddle.com/build/trials/create-trial
- [ ] **결제 링크 넣기** — Paddle 기본 결제 링크(`?_ptxn=…`)를 만들어 `tools/pricing.json` 의 `commercial.checkout` 에 넣습니다. 이 사이트는 Paddle.js 를 넣지 않고 **Paddle 이 호스팅하는 결제 페이지**로 연결합니다(인라인 체크아웃을 쓰려면 아래 「인라인 체크아웃을 쓸 경우」의 5가지를 직접 구현해야 합니다).
  - https://developer.paddle.com/build/transactions/default-payment-link
- [ ] **다운로드 링크(.dmg) 넣기** — 승인된 도메인에 파일을 올리고 `commercial.download` 에 경로를 넣습니다.
- [ ] **세금 표시 방식 정하기** — 가격에 세금을 포함(유럽형) / 별도(미국형) / 지역에 따라 자동 중 고릅니다. **Paddle 의무가 아니라 판매자 선택**입니다.
  - https://www.paddle.com/help/sell/tax/do-you-support-tax-inclusiveexclusive-pricing · https://developer.paddle.com/changelog/2025/automatic-tax-inclusive-exclusive-prices
- [ ] **정산 통화 정하기** — 고객이 지불할 통화와 정산 통화는 달라도 됩니다(고객은 지원 통화 어느 것으로든 결제 가능). 단 결제 통화별 최소 금액이 있습니다(USD 0.70 등).
  - https://www.paddle.com/help/start/set-up-paddle/how-do-i-change-my-default-(balance)-currency · https://developer.paddle.com/concepts/sell/supported-currencies
- [ ] **취소 경로 확인** — Paddle 이 보내는 구독 안내 메일과 고객 포털에 취소 링크가 이미 들어 있으며, 일부 지역은 원클릭 취소가 적용됩니다. 별도 취소 UI를 만들 필요는 없습니다.
  - https://developer.paddle.com/build/subscriptions/cancel-subscriptions

### Paddle 가 정해 둔 사실 — 문서와 어긋나면 안 되는 것

- **Paddle 이 판매대행(Merchant of Record)입니다.** 고객은 Paddle 로부터 구매하고, 결제 수단 확인 · 세금 계산· 부과 · 영수증 발행 · 환불 처리를 Paddle 이 합니다. 판매자는 **고객에게 따로 청구서를 발행하거나 대금을 요구할 수 없습니다**(MSA 10.1). 여기 문서들은 그에 맞췄습니다.
  - https://www.paddle.com/legal/terms · https://www.paddle.com/help/sell/tax/how-paddle-handles-vat-on-your-behalf
- **구독은 자동 갱신됩니다.** 고객이 해지하기 전까지 처음 기간과 같은 기간으로 계속 결제됩니다. 가격 인상 시에는 고지하고, 법이 요구하면 동의를 받습니다.
  - https://www.paddle.com/legal/buyer-terms
- **환불은 Paddle 이 최종 결정합니다.** 기본 정책은 「거래일로부터 14일 이내 요청 시 Paddle 이 재량으로 환불할 수 있으나 요청만으로 보장되지는 않으며, 법이 요구하는 경우 외에는 환불 불가」입니다. 지역별 법정 최소 기간(한국·브라질·중국 7일, EU/영국/스위스·터키·이스라엘 14일, 캐나다 7일, 싱가포르 5일)이 이보다 우선합니다. 환불되면 그 기간의 제품 접근은 종료됩니다. **저희 환불 정책은 Paddle 의 정책보다 불리해지면 안 됩니다.**
  - https://www.paddle.com/legal/refund-policy
- **환불은 Paddle 의 창구로.** 영수증·계정 결제 페이지의 지원 링크, 또는 paddle.net 의 「Request refund」로 요청합니다. 판매자가 직접 환불금을 송금하지 않습니다. 카드 환불은 보통 3–5 영업일, 결제 후 120일 이내 거래만 가능하고(페이팔 179일), 판매자가 수수료를 부담합니다.
  - https://www.paddle.com/help/manage/your-customers/how-do-i-issue-refunds
- **한국 고객은 갱신 동의 단계가 표시됩니다.** 무료 체험·할인 기간이 끝나면 계속 과금하려면 한국 공정위 규정에 따라 명시적 동의가 필요하며, 2025년 7월부터 Paddle 이 이 단계를 제공합니다.
  - https://developer.paddle.com/changelog/2026/subscription-consent-requirements
- **체험은 가격에 붙는 항목이고 반복 결제가 필수입니다.** `trial_period` 을 가격에 설정하며, 체험이 끝나면 등록된 결제 수단으로 자동 과금되고 그 전에 끝내면 과금이 없습니다.
  - https://developer.paddle.com/concepts/subscriptions/trials
- **같은 결제 화면의 항목은 결제 주기가 같아야 합니다.** 월·연간을 함께 넣을 때에는 각각 별도 가격으로 등록합니다.
  - https://developer.paddle.com/build/products/create-products-prices
- **Paddle 은 라이선스 키를 발급해 주지 않습니다.** 다운로드 링크와 라이선스 발급은 판매자 쪽에서 직접 처리해야 합니다(웹훅으로 구독 상태를 받아 라이선스를 발급). 여기 문서들은 그 전제로 「라이선스 서버」를 두었습니다.
  - https://developer.paddle.com/build/subscriptions/provision-access-webhooks

### 인라인 체크아웃을 쓸 경우 (이 사이트는 쓰지 않음)

자체 결제 화면(Paddle.js 인라인)을 만들면 Paddle 이 아래 다섯 가지를 직접 구현하라고 요구합니다: 반복 결제 주기와 갱신 시 결제 금액(체험이면 체험 기간), 구매하는 상품 설명, 소계·세금·합계와 통화가 표시된 금액, Paddle 약관·개인정보 처리방침이 포함된 결제 화면 푸터(Merchant of Record 표시), 그리고 **Paddle 표준 환불 정책과 다를 경우 우리 환불 정책 링크**. 이 사이트는 이 구현 대신 Paddle 호스팅 결제 페이지로 연결하므로 해당 없음.

- https://developer.paddle.com/build/checkout/brand-customize-inline-checkout · https://developer.paddle.com/changelog/2024/inline-checkout-compliance-changes

### 개인정보 — Paddle 측 처리와 우리에게 넘어오는 것

- Paddle 은 구매자에 대해 이름·주소·이메일·결제 수단 정보·결제 내역·IP 주소·기기 정보를 수집·처리합니다(자세는 Paddle 개인정보 처리방침).
- 데이터 공유 부속서에 따라 **판매자에게 넘어오는 것**은 구매자의 이름·주소·이메일, 구매 내역, 대시보드의 거래 분석입니다. **민감 정보 범주(특수 카테고리)는 공유되지 않습니다.** 양쪽은 각자 **독립적인 데이터 통제자**입니다.
- Paddle 은 법적 의무를 위해 거래 데이터를 5년 보관합니다.
- 따라서 개인정보 처리방침에는 Paddle 이 무엇을 수집하는지, 무엇이 우리에게 오는지, Paddle 이 판매대행이라는 점을 밝혀 두어야 합니다 → `privacy.html` 11항에 그 내용을 넣었습니다.

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

- App Store 링크는 `https://apps.apple.com/app/id6814686766` 로 넣어 두었습니다 (여섯 언어 랜딩 페이지). 앱이 승인돼 게시되기 전에는 이 링크가 「앱을 사용할 수 없음」으로 보입니다.
- Cloudflare Worker 배포 (`worker/README.md`) — 이것이 끝나야 `https://shouarchive.beakbig.com/` 가 열립니다.
- 저장소 이름을 바꾸면 GitHub Pages 원본 주소가 바뀌므로 `worker/wrangler.toml` 의 `UPSTREAM` 도 함께 고쳐야 합니다.
