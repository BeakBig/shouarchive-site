// beakbig.com/ShouArchive/* 를 ShouArchive 사이트로 이어 주는 Cloudflare Worker.
//
// beakbig.com 본 사이트는 그대로 두고, 이 경로만 UPSTREAM(기본: GitHub Pages) 에서 받아 온다.
// 라우트: beakbig.com/ShouArchive*  (wrangler.toml)
//
// - /ShouArchive         → /ShouArchive/ 로 301 (상대 경로 링크가 깨지지 않도록)
// - /ShouArchive/<path>  → UPSTREAM/<path>
// - 업스트림이 돌려주는 리다이렉트(Location)는 beakbig.com/ShouArchive/… 로 바꿔 준다
const BASE = "/ShouArchive";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (url.pathname === BASE) {
      return Response.redirect(`${url.origin}${BASE}/${url.search}`, 301);
    }
    if (!url.pathname.startsWith(`${BASE}/`)) {
      return fetch(request); // 라우트 밖 — 그대로 통과
    }

    const upstreamBase = (env.UPSTREAM || "https://beakbig.github.io/shouarchive-site").replace(/\/+$/, "");
    const rest = url.pathname.slice(BASE.length); // "/" 로 시작
    const upstream = `${upstreamBase}${rest}${url.search}`;

    const res = await fetch(upstream, {
      method: request.method,
      headers: {
        accept: request.headers.get("accept") || "*/*",
        "accept-language": request.headers.get("accept-language") || "",
        "user-agent": request.headers.get("user-agent") || "shouarchive-path-worker",
      },
      redirect: "manual",
      cf: { cacheEverything: true, cacheTtl: 300 },
    });

    const headers = new Headers(res.headers);
    const location = headers.get("location");
    if (location) {
      const target = new URL(location, upstream);
      if (target.href.startsWith(upstreamBase)) {
        headers.set("location", `${url.origin}${BASE}${target.href.slice(upstreamBase.length)}`);
      }
    }
    // 업스트림 호스트 기준 헤더는 뺀다
    headers.delete("content-security-policy");
    headers.delete("x-github-request-id");
    headers.set("x-shouarchive-upstream", upstreamBase);

    return new Response(res.body, { status: res.status, statusText: res.statusText, headers });
  },
};
