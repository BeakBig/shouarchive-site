# beakbig.com/ShouArchive 연결 (Cloudflare Worker)

`https://beakbig.com/ShouArchive/` 로 이 사이트를 내보내는 Worker 입니다. beakbig.com 본 사이트(Cloudflare Pages)는 건드리지 않고, `/ShouArchive*` 경로만 이 Worker 가 받아 GitHub Pages(`beakbig.github.io/shouarchive-site`)의 내용을 돌려줍니다.

## 배포

한 번만 하면 됩니다. 이후 사이트 내용은 이 저장소에 `git push` 하면 GitHub Pages 를 거쳐 그대로 반영됩니다 (Worker 는 5분 캐시).

```bash
cd worker
# Cloudflare 대시보드 › My Profile › API Tokens › "Edit Cloudflare Workers" 템플릿으로 토큰 발급
export CLOUDFLARE_API_TOKEN=...
npx wrangler deploy
```

대시보드에서 직접 하려면: Workers & Pages › Create › Worker › `worker.js` 내용 붙여 넣기 › Deploy › Settings › Domains & Routes › Route 추가 `beakbig.com/ShouArchive*` (zone `beakbig.com`) › Variables 에 `UPSTREAM` 추가(선택).

## 확인

```bash
curl -I https://beakbig.com/ShouArchive          # 301 → /ShouArchive/
curl -I https://beakbig.com/ShouArchive/         # 200, x-shouarchive-upstream 헤더
curl -I https://beakbig.com/ShouArchive/en/support.html
```

## 원본을 Cloudflare Pages 로 바꾸려면

이 저장소를 Cloudflare Pages 프로젝트로 연결한 뒤 `wrangler.toml` 의 `UPSTREAM` 을 `https://<프로젝트>.pages.dev` 로 바꾸고 다시 `npx wrangler deploy`.
