# ShouArchive 홈페이지

ShouArchive(macOS) 의 소개 · 지원 · 개인정보 처리방침 페이지입니다. 순수 정적 HTML/CSS 이고 빌드 단계가 없습니다.

- 공개 주소: https://beakbig.com/ShouArchive/ — beakbig.com 의 이 경로를 Cloudflare Worker(`worker/`)가 받아 GitHub Pages 원본을 돌려줍니다
- 원본(GitHub Pages): https://beakbig.github.io/shouarchive-site/ (`main` 브랜치 루트, Worker 배포 전에도 이 주소는 열립니다)
- 저장소: `BeakBig/shouarchive-site` (공개)

## 구성

| 경로 | 내용 |
| --- | --- |
| `index.html` · `support.html` · `privacy.html` | 한국어 랜딩 · 지원(FAQ) · 개인정보 처리방침 |
| `en/` · `ja/` · `zh-Hans/` · `zh-Hant/` · `es/` | 영어 · 일본어 · 중국어 간체 · 번체 · 스페인어판 (같은 세 페이지) |
| `assets/style.css` | 공용 스타일 (라이트 · 다크) |
| `assets/icon.png` · `icon-64.png` | 앱 아이콘 |
| `assets/screenshots/<언어>/` | 갤러리 스크린샷 `01.png` ~ `08.png` (2880×1800), 6개 언어 |
| `assets/samples/` | 심사 · 테스트용 합성 APK · AAB |
| `.nojekyll` | GitHub Pages 가 Jekyll 처리 없이 그대로 서빙하게 함 |
| `worker/` | `beakbig.com/ShouArchive/*` 를 이 사이트로 잇는 Cloudflare Worker 와 배포 설명 |
| `tools/localize-nav.py` | 모든 페이지에 6개 언어 전환 메뉴 · `hreflang` 을 넣는 스크립트 (페이지를 고치거나 언어를 더하면 다시 실행) |

App Store Connect 에 넣는 URL:

- 지원: `https://beakbig.com/ShouArchive/support.html` (다른 언어는 `<언어>/support.html`)
- 마케팅: `https://beakbig.com/ShouArchive/` (다른 언어는 `<언어>/`)
- 개인정보 처리방침: `https://beakbig.com/ShouArchive/privacy.html` (다른 언어는 `<언어>/privacy.html`)

## 올리기

```bash
git add -A && git commit -m "..." && git push
```

푸시하면 1분 안팎으로 GitHub Pages 에 반영되고, Worker 캐시(5분)가 지나면 beakbig.com/ShouArchive/ 에도 보입니다.

## 남은 일

- 앱이 App Store 에 올라가면 `index.html` · `en/index.html` 의 `APPSTORE_URL_PLACEHOLDER` 를 실제 링크로 바꿉니다.

  ```bash
  sed -i '' 's#APPSTORE_URL_PLACEHOLDER#https://apps.apple.com/app/id<Apple ID>#g' index.html en/index.html
  ```

- Cloudflare Worker 배포 (`worker/README.md`) — 이것이 끝나야 `https://beakbig.com/ShouArchive/` 가 열립니다.
- 저장소 이름을 바꾸면 GitHub Pages 원본 주소가 바뀌므로 `worker/wrangler.toml` 의 `UPSTREAM` 도 함께 고쳐야 합니다.
