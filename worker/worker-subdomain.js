// 서브도메인(예: shouarchive.beakbig.com) 전체를 ShouArchive 사이트로 잇는 Cloudflare Worker.
// 워커 › Settings › Domains & Routes › Add › Custom Domain 에 서브도메인을 넣으면 DNS · 인증서는 Cloudflare 가 만든다.
// 경로 접두어가 없으므로 그대로 UPSTREAM 에 넘긴다 (UPSTREAM 기본: GitHub Pages).
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const upstreamBase = (env.UPSTREAM || "https://beakbig.github.io/shouarchive-site").replace(/\/+$/, "");
    const upstream = `${upstreamBase}${url.pathname}${url.search}`;

    const res = await fetch(upstream, {
      method: request.method,
      headers: {
        accept: request.headers.get("accept") || "*/*",
        "accept-language": request.headers.get("accept-language") || "",
        "user-agent": request.headers.get("user-agent") || "shouarchive-worker",
      },
      redirect: "manual",
      cf: { cacheEverything: true, cacheTtl: 300 },
    });

    const headers = new Headers(res.headers);
    const location = headers.get("location");
    if (location) {
      const target = new URL(location, upstream);
      if (target.href.startsWith(upstreamBase)) {
        headers.set("location", `${url.origin}${target.href.slice(upstreamBase.length)}`);
      }
    }
    headers.delete("content-security-policy");
    headers.delete("x-github-request-id");
    headers.set("x-shouarchive-upstream", upstreamBase);
    return new Response(res.body, { status: res.status, statusText: res.statusText, headers });
  },
};
