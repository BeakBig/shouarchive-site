# shouarchive.beakbig.com 연결 (Cloudflare Worker)

`https://shouarchive.beakbig.com/` 로 이 사이트를 내보내는 Worker 입니다(`worker-subdomain.js`). beakbig.com 본 사이트는 건드리지 않고, 서브도메인 전체를 GitHub Pages(`beakbig.github.io/shouarchive-site`)의 내용으로 돌려줍니다. `worker.js` 는 경로 방식(`beakbig.com/ShouArchive/*`)용으로 남겨 둔 것입니다.

## 배포

한 번만 하면 됩니다. 이후 사이트 내용은 이 저장소에 `git push` 하면 GitHub Pages 를 거쳐 그대로 반영됩니다 (Worker 는 5분 캐시).

```bash
cd worker
# Cloudflare 대시보드 › My Profile › API Tokens › "Edit Cloudflare Workers" 템플릿으로 토큰 발급
export CLOUDFLARE_API_TOKEN=...
npx wrangler deploy
```

대시보드에서 직접 하려면: Workers & Pages › Create › Worker › `worker-subdomain.js` 내용 붙여 넣기 › Deploy › Settings › Domains & Routes › Add › Custom Domain `shouarchive.beakbig.com`.

## 확인

```bash
curl -I https://beakbig.com/ShouArchive          # 301 → /ShouArchive/
curl -I https://shouarchive.beakbig.com/         # 200, x-shouarchive-upstream 헤더
curl -I https://shouarchive.beakbig.com/en/support.html
```

## 원본을 Cloudflare Pages 로 바꾸려면

이 저장소를 Cloudflare Pages 프로젝트로 연결한 뒤 `wrangler.toml` 의 `UPSTREAM` 을 `https://<프로젝트>.pages.dev` 로 바꾸고 다시 `npx wrangler deploy`.
