# ShouArchive 홈페이지

ShouArchive(macOS) 의 소개 · 지원 · 개인정보 처리방침 페이지입니다. 순수 정적 HTML/CSS 이고 빌드 단계가 없습니다.

- 공개 주소: https://beakbig.github.io/shouarchive-site/ (GitHub Pages, `main` 브랜치 루트)
- 저장소: `BeakBig/shouarchive-site` (공개)

## 구성

| 경로 | 내용 |
| --- | --- |
| `index.html` · `support.html` · `privacy.html` | 한국어 랜딩 · 지원(FAQ) · 개인정보 처리방침 |
| `en/` | 영어판 (같은 세 페이지) |
| `assets/style.css` | 공용 스타일 (라이트 · 다크) |
| `assets/icon.png` · `icon-64.png` | 앱 아이콘 |
| `assets/screenshots/ko/`, `en/` | 갤러리 스크린샷 `01.png` ~ `08.png` (2880×1800) |
| `assets/samples/` | 심사 · 테스트용 합성 APK · AAB |
| `.nojekyll` | GitHub Pages 가 Jekyll 처리 없이 그대로 서빙하게 함 |

App Store Connect 에 넣는 URL:

- 지원: `https://beakbig.github.io/shouarchive-site/support.html` (영어 `en/support.html`)
- 마케팅: `https://beakbig.github.io/shouarchive-site/`
- 개인정보 처리방침: `https://beakbig.github.io/shouarchive-site/privacy.html` (영어 `en/privacy.html`)

## 올리기

```bash
git add -A && git commit -m "..." && git push
```

푸시하면 1분 안팎으로 반영됩니다. 확인: https://beakbig.github.io/shouarchive-site/

## 남은 일

- 앱이 App Store 에 올라가면 `index.html` · `en/index.html` 의 `APPSTORE_URL_PLACEHOLDER` 를 실제 링크로 바꿉니다.

  ```bash
  sed -i '' 's#APPSTORE_URL_PLACEHOLDER#https://apps.apple.com/app/id<Apple ID>#g' index.html en/index.html
  ```

- `og:image` 는 상대 경로라 SNS 미리보기에는 안 잡힐 수 있습니다. 필요하면 절대 주소(`https://beakbig.github.io/shouarchive-site/assets/icon.png`)로 바꾸세요.
- 저장소 이름을 `ShouArchiveWeb` 로 바꾸면 공개 주소도 `https://beakbig.github.io/ShouArchiveWeb/` 로 바뀌므로, 바꾼다면 App Store Connect 의 URL 과 `hreflang` 링크도 함께 고쳐야 합니다.
