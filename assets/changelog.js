/*
 * 변경 사항 페이지(changelog.html · 6개 언어) — 버전이 늘어도 보기 쉽게 (2026-11-04 Jin 「점점 많아지니 스크롤하기 힘들다」).
 *
 * HTML 은 그대로 둔다 — <h2 id="v1-1-1">1.1.1 — 날짜</h2> 아래 <h3> · <ul> (tools/sync-releases.py 가 이 꼴을 읽고,
 * 릴리스 때도 같은 꼴로 맨 위에 넣는다). 이 파일은 화면만 바꾼다:
 *   - 왼쪽(좁은 화면은 위) 버전 목록 — 누르면 그 버전으로 가고, 스크롤하면 지금 보는 버전에 표시
 *   - 버전마다 접는 카드 — 최근 3개만 펼쳐 두고, 접힌 카드에도 「추가 2 · 고친 점 1」 처럼 무엇이 있는지 보인다
 *   - 「모두 펼치기 · 접기」
 *   - 주소에 #v1-0-3 이 있으면 그 버전을 펼친다 (앱 「소식」 의 「변경 사항 보기」 가 이렇게 연다)
 * 스크립트가 돌지 않으면 예전처럼 한 줄로 길게 보인다. 인라인 스크립트가 아닌 이유는 nav.js 와 같다(CSP script-src 'self').
 */
(function () {
  var wrap = document.querySelector('.doc .wrap');
  if (!wrap) return;
  var heads = Array.prototype.slice.call(wrap.querySelectorAll('h2[id^="v"]'));
  if (!heads.length) return;

  var TEXT = {
    'ko': { versions: '버전', expand: '모두 펼치기', collapse: '모두 접기', latest: '최신' },
    'en': { versions: 'Versions', expand: 'Expand all', collapse: 'Collapse all', latest: 'Latest' },
    'ja': { versions: 'バージョン', expand: 'すべて開く', collapse: 'すべて閉じる', latest: '最新' },
    'zh-Hans': { versions: '版本', expand: '全部展开', collapse: '全部收起', latest: '最新' },
    'zh-Hant': { versions: '版本', expand: '全部展開', collapse: '全部收合', latest: '最新' },
    'es': { versions: 'Versiones', expand: 'Desplegar todo', collapse: 'Contraer todo', latest: 'Última' }
  };
  var t = TEXT[document.documentElement.lang] || TEXT.en;
  var OPEN_COUNT = 3;

  var layout = document.createElement('div');
  layout.className = 'changelog-layout';
  var side = document.createElement('aside');
  side.className = 'release-side';
  var nav = document.createElement('nav');
  nav.className = 'release-index';
  nav.setAttribute('aria-label', t.versions);
  var list = document.createElement('div');
  list.className = 'releases';
  var cards = [];
  var links = [];

  heads.forEach(function (h2, index) {
    var card = document.createElement('details');
    card.className = 'release';
    if (index < OPEN_COUNT) card.open = true;
    var summary = document.createElement('summary');
    var body = document.createElement('div');
    body.className = 'release-body';

    // h2 뒤의 내용(다음 버전 h2 전까지)을 카드 안으로
    var node = h2.nextSibling;
    while (node && !(node.nodeType === 1 && node.matches('h2[id^="v"]'))) {
      var next = node.nextSibling;
      body.appendChild(node);
      node = next;
    }

    // 접혀 있어도 무엇이 들었는지 — 「추가 2 · 고친 점 1」
    var counts = [];
    Array.prototype.forEach.call(body.querySelectorAll('h3'), function (h3) {
      var ul = h3.nextElementSibling;
      if (ul && ul.tagName === 'UL') counts.push(h3.textContent.trim() + ' ' + ul.children.length);
    });

    summary.appendChild(h2);
    if (index === 0) {
      var badge = document.createElement('span');
      badge.className = 'release-latest';
      badge.textContent = t.latest;
      summary.appendChild(badge);
    }
    var meta = document.createElement('span');
    meta.className = 'release-meta';
    meta.textContent = counts.join(' · ');
    summary.appendChild(meta);
    card.appendChild(summary);
    card.appendChild(body);
    list.appendChild(card);
    cards.push(card);

    // 버전 목록 — 「1.1.1」 과 날짜
    var parts = h2.textContent.split(' — ');
    var link = document.createElement('a');
    link.href = '#' + h2.id;
    var version = document.createElement('b');
    version.textContent = parts[0].trim();
    link.appendChild(version);
    if (parts[1]) {
      var date = document.createElement('small');
      date.textContent = parts[1].trim();
      link.appendChild(date);
    }
    link.addEventListener('click', function () { card.open = true; });
    nav.appendChild(link);
    links.push(link);
  });

  var toggle = document.createElement('button');
  toggle.type = 'button';
  toggle.className = 'release-toggle';
  function allOpen() { return cards.every(function (c) { return c.open; }); }
  function syncToggle() { toggle.textContent = allOpen() ? t.collapse : t.expand; }
  toggle.addEventListener('click', function () {
    var open = !allOpen();
    cards.forEach(function (c) { c.open = open; });
    syncToggle();
  });
  cards.forEach(function (c) { c.addEventListener('toggle', syncToggle); });
  syncToggle();

  side.appendChild(nav);
  side.appendChild(toggle);
  layout.appendChild(side);
  layout.appendChild(list);
  wrap.appendChild(layout);
  wrap.classList.add('changelog-wide');

  // 주소의 #v… 로 온 버전은 펼쳐서 보인다
  function openFromHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    var target = id && document.getElementById(id);
    var card = target && target.closest('details.release');
    if (card) {
      card.open = true;
      target.scrollIntoView();
    }
  }
  window.addEventListener('hashchange', openFromHash);
  openFromHash();

  // 스크롤하면 지금 보는 버전을 목록에 표시 — 머리 아래 선(120px)을 지난 마지막 카드
  var ticking = false;
  function markCurrent() {
    ticking = false;
    var line = 120;
    var current = 0;
    cards.forEach(function (c, i) { if (c.getBoundingClientRect().top <= line) current = i; });
    links.forEach(function (l, i) {
      var on = i === current;
      l.classList.toggle('current', on);
      if (on && nav.scrollWidth > nav.clientWidth) {
        // 좁은 화면(가로 목록)에서는 지금 버전이 보이게 옆으로 민다
        nav.scrollLeft = l.offsetLeft - nav.clientWidth / 2 + l.clientWidth / 2;
      }
    });
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(markCurrent); }
  }, { passive: true });
  cards.forEach(function (c) { c.addEventListener('toggle', markCurrent); });
  markCurrent();
})();
