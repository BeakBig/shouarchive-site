/*
 * 언어 전환 메뉴 — 헤더의 <select class="lang-select"> 에서 언어를 고르면 그 언어의 같은 페이지로 간다.
 * 모든 페이지가 이 파일 하나를 쓴다 (tools/localize-nav.py 가 </body> 앞에 넣는다).
 * 인라인 <script> 를 두지 않는 이유: 루트 `_headers` 의 Content-Security-Policy 가 script-src 'self' 라서
 * 인라인 스크립트는 막힌다. 언어 중립 — 문구는 없다.
 */
document.querySelectorAll('.lang-select').forEach(function (select) {
  select.addEventListener('change', function () { location.href = select.value; });
});
