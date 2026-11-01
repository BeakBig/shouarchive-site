/*
 * 언어 전환 메뉴 — 헤더의 <select class="lang-select"> 에서 언어를 고르면 그 언어의 같은 페이지로 간다.
 * 모든 페이지가 이 파일 하나를 쓴다 (tools/localize-nav.py 가 </body> 앞에 넣는다).
 * 인라인 <script> 를 두지 않는 이유: 루트 `_headers` 의 Content-Security-Policy 가 script-src 'self' 라서
 * 인라인 스크립트는 막힌다. 언어 중립 — 문구는 없다.
 */
document.querySelectorAll('.lang-select').forEach(function (select) {
  select.addEventListener('change', function () { location.href = select.value; });
});

/*
 * 월 구독 판매일 (2026-11-02) — #sale-config 의 data-monthly-from(YYYY-MM-DD · tools/pricing.json 의 monthly.first_day,
 * fill-pricing.py 가 넣는다)이 방문자의 날짜로 오면 [data-monthly-open](「구독하기」 등)을 보이고 [data-monthly-soon]
 * (「판매 시작」 안내)을 숨긴다. 스크립트가 없거나 날짜를 못 읽으면 HTML 그대로 — 판매 시작 안내만 보인다.
 */
(function () {
  var config = document.getElementById('sale-config');
  var from = config && config.getAttribute('data-monthly-from');
  if (!from || !/^\d{4}-\d{2}-\d{2}$/.test(from)) return;
  var now = new Date();
  var today = now.getFullYear() + '-' + ('0' + (now.getMonth() + 1)).slice(-2) + '-' + ('0' + now.getDate()).slice(-2);
  if (today < from) return;
  document.querySelectorAll('[data-monthly-open]').forEach(function (el) { el.hidden = false; });
  document.querySelectorAll('[data-monthly-soon]').forEach(function (el) { el.hidden = true; });
})();
