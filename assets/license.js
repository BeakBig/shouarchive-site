/*
 * ShouArchive 라이선스 — 결제 완료 화면 · 결제 수단 바꾸기 · 앱을 여는 중계 페이지 · 키 다시 받기 · 키 바꾸기 · 개인정보 삭제.
 * 6개 언어 페이지가 모두 이 파일 하나를 쓴다. 문구는 각 페이지의 HTML 에 있고, 여기서는
 * 보이고 숨기기와 값 채우기만 한다 (그래서 tools/check-site.py 의 언어별 구조 비교를 그대로 통과한다).
 *
 * 실행: 페이지가 <script src="assets/license.js" data-page="checkout|billing|activate|resend|rotate|erase"></script> 로
 * 불러오면 그 이름의 함수를 바로 실행한다 (인라인 <script> 는 _headers 의 CSP 가 막으므로 두지 않는다).
 *
 * 라이선스 서버 계약: shouarchive-license 저장소 docs/app-contract.md §2.10 ~ §2.13, 개인정보 삭제는 2026-10-20 계약 §8.
 *   POST /v1/web/checkout             사이트에서 사는 결제를 만든다 → { transaction_id, claim } · 409 checkout_limit 이면 잠시 뒤 다시
 *                                     월 구독은 { plan: "monthly" } (2026-11-02 · §2.20) — 판매 전이면 403 not_on_sale
 *   POST /v1/purchase/status          결제가 끝나면 그 확인 값으로 키를 받는다 → { status: processing | ready, key, plan, paid_until, … }
 *   POST /v1/licenses/resend          구매 이메일로 같은 키를 다시 보낸다 → 늘 { status: accepted }
 *   POST /v1/licenses/rotate          구매 이메일로 키 바꾸기 확인 링크를 보낸다 → 늘 { status: accepted }
 *   POST /v1/licenses/rotate/confirm  확인 링크의 값으로 키를 바꾼다 → { status: rotated, email_hint, email_sent }
 *   POST /v1/privacy/erase            구매 이메일로 개인정보 삭제 확인 링크(24시간)를 보낸다 → 늘 { status: accepted }
 *   POST /v1/privacy/erase/confirm    확인 링크의 값으로 삭제한다 → { status: erased, licenses } · 404 erase_not_found · 410 erase_expired
 * 키 · 확인 값은 주소의 # 뒤에만 둔다 — 브라우저가 서버로 보내지 않아 사이트 로그에 남지 않는다. 읽은 뒤에는 주소에서 지운다.
 */
(function () {
  'use strict';

  var API_DEFAULT = 'https://license.beakbig.com';
  /** SA-XXXXX-XXXXX-XXXXX-XXXXX (헷갈리는 글자 I · L · O · U 없음) */
  var KEY_RE = /^SA(-[0-9ABCDEFGHJKMNPQRSTVWXYZ]{5}){4}$/;
  /**
   * 결제 뒤 키를 기다리는 시간 — 2초 간격 30번(1분). 그래도 없으면 「결제는 완료됐으니 메일을 확인해 주세요」 를 띄우고,
   * 페이지를 열어 둔 동안 5초 간격으로 5분 더 본다(준비되면 그때 키를 보여 준다).
   */
  var POLL_MS = 2000;
  var POLL_TRIES = 30;
  var SLOW_POLL_MS = 5000;
  var SLOW_POLL_TRIES = 60;

  /** 이 스크립트가 있는 assets/ 주소 — 언어 폴더(en/ …)의 페이지에서 불러도 같은 곳을 가리킨다 */
  var ASSETS = document.currentScript && document.currentScript.src ? new URL('.', document.currentScript.src).href : null;

  function byId(id) { return document.getElementById(id); }
  function show(id, on) { var el = byId(id); if (el) el.hidden = !on; }
  /** 결제 창을 닫고 보여 주는 안내 — 그냥 닫힌 것처럼 보이지 않게 팝업으로 띄운다(Jin 11/11 「왜 창을 닫았는지 알려줘야」).
   *  상자는 페이지에도 남긴다(팝업을 닫은 뒤에도 읽을 수 있게). 팝업은 그 상자의 제목 · 글을 그대로 옮긴 <dialog> 다. */
  function reveal(id) {
    show(id, true);
    var el = byId(id);
    if (!el) return;
    try { el.scrollIntoView({ block: 'center' }); } catch (e) { /* 옛 브라우저 */ }
    var title = el.querySelector('h2');
    var text = el.querySelector('p');
    if (!title || !text || typeof HTMLDialogElement === 'undefined') { try { el.focus({ preventScroll: true }); } catch (e) { /* 그대로 */ } return; }
    var old = byId(id + '-dialog');
    if (old) old.remove();
    var dialog = document.createElement('dialog');
    dialog.id = id + '-dialog';
    dialog.className = 'checkout-dialog';
    dialog.appendChild(title.cloneNode(true));
    dialog.appendChild(text.cloneNode(true));
    var actions = document.createElement('div');
    actions.className = 'plan-actions';
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'btn';
    button.textContent = el.dataset.ok || 'OK';
    button.addEventListener('click', function () { dialog.close(); });
    actions.appendChild(button);
    dialog.appendChild(actions);
    dialog.addEventListener('close', function () { dialog.remove(); });
    document.body.appendChild(dialog);
    // Paddle 결제 창(iframe)이 닫히는 중이어도 맨 위 층에 뜬다
    try { dialog.showModal(); button.focus(); } catch (e) { dialog.remove(); }
  }

  function apiBase() {
    var config = byId('paddle-config');
    return (config && config.dataset.licenseApi) || API_DEFAULT;
  }

  /** POST JSON — 2xx 면 본문, 아니면 { code } 를 담은 오류로 거절한다 */
  function post(path, body) {
    return fetch(apiBase() + path, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(body)
    }).then(function (response) {
      return response.json().catch(function () { return {}; }).then(function (json) {
        if (response.ok) return json;
        var error = new Error('license api ' + response.status);
        error.code = json && json.error && json.error.code;
        throw error;
      });
    });
  }

  function pageLocale() { return document.documentElement.lang || 'en'; }
  function fragment() { return new URLSearchParams(location.hash.replace(/^#/, '')); }

  /** 사람이 친 키를 SA-XXXXX-… 모양으로 정리한다 (소문자 · 공백 · 하이픈 무시) */
  function normalizeKey(raw) {
    var compact = String(raw || '').toUpperCase().replace(/[^0-9A-Z]/g, '');
    if (compact.length !== 22 || compact.indexOf('SA') !== 0) return compact;
    var body = compact.slice(2);
    return ['SA', body.slice(0, 5), body.slice(5, 10), body.slice(10, 15), body.slice(15, 20)].join('-');
  }

  function appUrl(key) { return 'shouarchive://activate?key=' + encodeURIComponent(key); }

  /** Mac 데스크톱 브라우저인가 (iPad 는 Macintosh 로 나오지만 터치가 있다) — 여기서만 앱을 저절로 연다 */
  function isMacDesktop() { return /Macintosh/.test(navigator.userAgent) && !('ontouchend' in document); }

  /** Mac 에서만 뜻이 있는 것(data-mac-only — 앱 열기 버튼 · 「이 Mac 에 등록」 안내)과 다른 기기용 안내(data-not-mac)를 고른다 */
  function fitDevice() {
    var mac = isMacDesktop();
    var i, els = document.querySelectorAll('[data-mac-only]');
    for (i = 0; i < els.length; i++) els[i].hidden = !mac;
    els = document.querySelectorAll('[data-not-mac]');
    for (i = 0; i < els.length; i++) els[i].hidden = mac;
  }

  /** 복사 버튼 — 안 되면 키 글자를 골라 둔다 (직접 ⌘C) */
  function wireCopy(buttonId, keyId) {
    var button = byId(buttonId);
    var keyEl = byId(keyId);
    if (!button || !keyEl) return;
    var label = button.textContent;
    button.addEventListener('click', function () {
      var text = keyEl.textContent;
      var done = function () {
        button.textContent = button.dataset.done || label;
        setTimeout(function () { button.textContent = label; }, 2000);
      };
      var selectText = function () {
        var range = document.createRange();
        range.selectNodeContents(keyEl);
        var selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, selectText);
      } else {
        selectText();
      }
    });
  }

  /** 키 · 앱 열기 버튼 · 복사를 한 묶음으로 채운다 (prefix-key · prefix-open · prefix-copy) */
  function fillKey(prefix, key) {
    byId(prefix + '-key').textContent = key;
    byId(prefix + '-open').href = appUrl(key);
    wireCopy(prefix + '-copy', prefix + '-key');
    fitDevice();
  }

  // ------------------------------------------------------------------ 결제 페이지 (checkout.html)

  /** 얼리버드 할인 id (data-discount) — 마지막 날(data-discount-last-day, 이 날 포함)이 세계 어디서든 끝나기 전(다음 날 12:00 UTC)일 때만 */
  function earlyBirdDiscount(cfg) {
    if (!cfg.discount || !/^\d{4}-\d{2}-\d{2}$/.test(cfg.discountLastDay || '')) return null;
    var ends = Date.parse(cfg.discountLastDay + 'T00:00:00Z') + 36 * 3600000;
    return Date.now() < ends ? cfg.discount : null;
  }

  /** 이 브라우저의 오늘 (YYYY-MM-DD) — 월 구독 판매일은 방문자의 날짜로 본다 (assets/nav.js 와 같은 규칙) */
  function localDay() {
    var now = new Date();
    return now.getFullYear() + '-' + ('0' + (now.getMonth() + 1)).slice(-2) + '-' + ('0' + now.getDate()).slice(-2);
  }

  /** 월 구독을 지금 열 수 있나 — 가격 id(data-price-monthly)가 있고 판매일(data-monthly-from)이 방문자의 날짜로 왔다 */
  function monthlyOpen(cfg) {
    return Boolean(cfg.priceMonthly) && /^\d{4}-\d{2}-\d{2}$/.test(cfg.monthlyFrom || '') && localDay() >= cfg.monthlyFrom;
  }

  /** 월 구독(?plan=monthly · #kind=monthly)이면 [data-plan-monthly] 문구를, 아니면 [data-plan-perpetual] 문구를 보인다 */
  function fitPlan(monthly) {
    var i, els = document.querySelectorAll('[data-plan-monthly]');
    for (i = 0; i < els.length; i++) els[i].hidden = !monthly;
    els = document.querySelectorAll('[data-plan-perpetual]');
    for (i = 0; i < els.length; i++) els[i].hidden = monthly;
  }

  function checkout() {
    var config = byId('paddle-config');
    if (!config) return;
    var cfg = config.dataset;
    var params = new URLSearchParams(location.search);
    var hash = fragment();
    // 앱에서 시작한 결제는 서버가 # 뒤에 확인 값(claim)과 종류를 붙여 준다
    var claim = hash.get('claim');
    var fromApp = hash.get('from') === 'app';
    var renewal = hash.get('kind') === 'renewal';
    // 월 구독 (2026-11-02) — 가격 페이지의 「구독하기」(?plan=monthly) · 앱의 「다시 구독…」(#kind=monthly) — 영구 문구 대신 월 구독 문구
    var resubscribe = hash.get('kind') === 'monthly';
    var monthly = params.get('plan') === 'monthly' || hash.get('plan') === 'monthly' || resubscribe;
    var transactionId = params.get('_ptxn');
    fitPlan(monthly);
    if (claim !== null || hash.get('from') !== null || hash.get('kind') !== null) {
      // 확인 값을 읽었으면 주소에서 지운다 — 방문 기록 · 화면 공유에 남지 않게 (# 뒤라 서버로는 애초에 가지 않았다). ?_ptxn= 은 남긴다
      try { history.replaceState(null, '', location.pathname + location.search); } catch (e) { /* 그대로 둔다 */ }
    }

    if (params.get('done') === '1') {         // 예전 방식으로 돌아온 경우 (successUrl)
      show('checkout-closed', false);
      show('checkout-done', true);
      return;
    }
    if (!cfg.token) return;                    // 아직 결제를 열지 않음 → 「출시 전」 안내만
    if (monthly && !transactionId && !monthlyOpen(cfg)) {   // 월 구독 판매 전(또는 가격 id 없음) → 「아직 구독할 수 없습니다」
      show('checkout-closed', false);
      show('checkout-monthly-soon', true);
      return;
    }
    if (!window.Paddle) {                      // Paddle.js 를 불러오지 못함(광고 차단기 · 네트워크) — 출시 전 안내와 구분한다
      show('checkout-closed', false);
      show('checkout-blocked', true);
      return;
    }

    var LOCALES = { 'ko': 'ko', 'en': 'en', 'ja': 'ja', 'zh-Hans': 'zh-Hans', 'es': 'es' };  // zh-Hant 은 Paddle 이 지원하지 않아 생략
    // successUrl 로 페이지를 옮기지 않는다 — 결제 완료를 여기서 받아 확인 값으로 키를 가져온다
    var settings = { displayMode: 'overlay' };
    var locale = LOCALES[pageLocale()];
    if (locale) settings.locale = locale;
    if (cfg.env === 'sandbox') Paddle.Environment.set('sandbox');
    Paddle.Initialize({
      token: cfg.token,
      checkout: { settings: settings },
      eventCallback: function (event) {
        if (!event) return;
        if (event.name === 'checkout.completed') {
          completed((event.data && event.data.transaction_id) || transactionId);
        }
        // 결제 창에서 이메일을 넣었다 — 이미 월 구독 중인 고객이면 결제 전에 막는다 (2026-11-11 · 중복 월 구독)
        if (event.name === 'checkout.customer.created' || event.name === 'checkout.customer.updated') {
          checkSubscribed((event.data && event.data.transaction_id) || transactionId);
        }
      }
    });
    show('checkout-closed', false);

    // ?_ptxn= (라이선스 서버가 만든 앱 구매 · 갱신 · 다시 구독 거래) 이면 Paddle.js 가 결제 화면을 스스로 연다.
    if (transactionId) return;
    if (monthly) { openMonthly(); return; }
    if (!cfg.priceLicense || !cfg.priceUpdates) { show('checkout-closed', true); return; }
    show('checkout-buy', true);

    byId('checkout-open').addEventListener('click', function () {
      var button = this;
      button.disabled = true;
      show('checkout-limit', false);
      post('/v1/web/checkout', { locale: pageLocale() })
        .then(function (result) {
          transactionId = result.transaction_id;
          claim = result.claim;
          Paddle.Checkout.open({ transactionId: transactionId });
        })
        .catch(function (error) {
          // 시간당 결제 만들기 상한(409 checkout_limit) — 잠시 뒤 다시 누르라고 안내하고 결제 창은 열지 않는다
          if (error && error.code === 'checkout_limit') { show('checkout-limit', true); return; }
          // 라이선스 서버에 닿지 못하면 예전처럼 연다 — 키는 메일로만 받는다
          claim = null;
          var settings = { items: [
            { priceId: cfg.priceLicense, quantity: 1 },
            { priceId: cfg.priceUpdates, quantity: 1 }
          ] };
          // 얼리버드 — 서버가 붙이는 할인을 이 예비 길에서도 붙인다
          var discount = earlyBirdDiscount(cfg);
          if (discount) settings.discountId = discount;
          Paddle.Checkout.open(settings);
        })
        .then(function () { button.disabled = false; });
    });

    /** 월 구독 「구독하기」 — 서버가 월 구독 거래를 만든다. 판매 전(403 not_on_sale)이면 안내로 바꾼다 */
    function openMonthly() {
      show('checkout-buy-monthly', true);
      byId('checkout-open-monthly').addEventListener('click', function () {
        var button = this;
        button.disabled = true;
        show('checkout-limit', false);
        post('/v1/web/checkout', { locale: pageLocale(), plan: 'monthly' })
          .then(function (result) {
            transactionId = result.transaction_id;
            claim = result.claim;
            Paddle.Checkout.open({ transactionId: transactionId });
          })
          .catch(function (error) {
            if (error && error.code === 'checkout_limit') { show('checkout-limit', true); return; }
            // 서버의 판매일이 아직이다 (사이트의 판매일 · 방문자의 시계와 어긋남) — 결제 창을 열지 않는다
            if (error && error.code === 'not_on_sale') {
              show('checkout-buy-monthly', false);
              show('checkout-monthly-soon', true);
              return;
            }
            // 라이선스 서버에 닿지 못하면 월 구독 가격 하나로 연다 — 영구 라이선스 항목 · 얼리버드 할인은 넣지 않는다. 키는 메일로만 받는다
            claim = null;
            Paddle.Checkout.open({ items: [{ priceId: cfg.priceMonthly, quantity: 1 }] });
          })
          .then(function () { button.disabled = false; });
      });
    }

    /** 이 결제의 고객이 이미 월 구독 중인지 서버에 묻는다 (이메일은 보내지 않는다 — 거래 id + 확인 값). 구독 중이면 결제 창을 닫고 안내한다.
     *  앱의 「다시 구독…」 · 영구 라이선스 결제 · 확인 값이 없는 예비 길에서는 묻지 않는다. 서버에 닿지 못하면 그대로 둔다(결제 뒤 서버가 해지 · 환불한다). */
    var subscribedShown = false;
    function checkSubscribed(id) {
      if (!monthly || resubscribe || !claim || !id || subscribedShown) return;
      post('/v1/web/checkout/check', { transaction_id: id, claim: claim })
        .then(function (result) {
          if (!result || !result.subscribed || subscribedShown) return;
          subscribedShown = true;
          try { Paddle.Checkout.close(); } catch (e) { /* 이미 닫힘 */ }
          show('checkout-buy-monthly', false);
          reveal('checkout-already-subscribed');
        })
        .catch(function () { /* 묻지 못함 — 결제를 막지 않는다 */ });
    }

    function completed(id) {
      show('checkout-buy', false);
      show('checkout-buy-monthly', false);
      // Paddle 의 완료 화면을 잠깐 보여 준 뒤 닫고, 이 페이지의 안내로 넘어간다
      setTimeout(function () { try { Paddle.Checkout.close(); } catch (e) { /* 이미 닫힘 */ } }, 1500);
      if (renewal) { show('checkout-renewed', true); return; }
      if (resubscribe) { show('checkout-resubscribed', true); return; }   // 같은 키 · 같은 Mac 으로 월 구독을 다시 시작
      if (!claim || !id) { show('checkout-done', true); return; }
      show('checkout-processing', true);
      startWaitingAnimation();
      poll(id, 0);
    }

    function poll(id, attempt) {
      post('/v1/purchase/status', { transaction_id: id, claim: claim })
        .then(function (result) {
          if (result.status === 'ready') return ready(result);
          if (result.status === 'already_subscribed') return duplicate();   // 이미 구독 중 — 서버가 새 구독을 해지 · 환불했다
          retry(id, attempt);
        })
        .catch(function (error) {
          // 확인 값이 맞지 않으면 더 묻지 않는다 — 메일로 받는다
          if (error && error.code === 'claim_not_found') return mailed();
          retry(id, attempt);
        });
    }

    function retry(id, attempt) {
      var next = attempt + 1;
      if (next === POLL_TRIES) slow();
      if (next >= POLL_TRIES + SLOW_POLL_TRIES) return;  // 안내를 띄운 채 그만 본다
      setTimeout(function () { poll(id, next); }, next < POLL_TRIES ? POLL_MS : SLOW_POLL_MS);
    }

    /** 오래 걸린다 — 결제는 끝났으니 메일을 확인하고, 안 오면 문의하라고 안내한다 (뒤에서 계속 확인한다) */
    function slow() {
      show('checkout-processing', false);
      stopWaitingAnimation();
      show('checkout-slow', true);
    }

    function ready(result) {
      show('checkout-processing', false);
      stopWaitingAnimation();
      show('checkout-slow', false);
      if (!result.key) return mailed();  // 서버가 키를 보관하지 않는 설정 — 메일로 받는다
      fillKey('license', result.key);
      // 월 구독 키 — 앱에서 시작한 결제는 주소에 종류가 없어 서버 답(plan)으로 고른다
      show('checkout-ready-monthly', monthly || result.plan === 'monthly');
      show('checkout-ready', true);
      // 앱에서 시작한 결제면 앱을 바로 연다 (브라우저가 열지 묻는다 · 앱은 등록할지 한 번 더 묻는다)
      if (fromApp) location.href = appUrl(result.key);
    }

    function duplicate() {
      show('checkout-processing', false);
      stopWaitingAnimation();
      show('checkout-slow', false);
      show('checkout-duplicate', true);
    }

    function mailed() {
      show('checkout-processing', false);
      stopWaitingAnimation();
      show('checkout-slow', false);
      show('checkout-done', true);
    }
  }

  // ------------------------------------------------------------------ 결제 수단 바꾸기 (billing.html)

  /*
   * Paddle Retain 의 결제 복구(갱신 결제 실패 → 결제 수단 바꾸기)가 쓰는 페이지. Retain 설정은 결제 · 가격 페이지가 아닌
   * 공개 페이지에 Paddle.js 가 있는지 확인하고, 복구 링크가 이 페이지를 열면 Paddle.js 가 결제 수단 변경 창을 스스로 띄운다.
   * 여기서는 Paddle.js 를 초기화만 한다 — pwCustomer 는 넘기지 않는다(사이트에 로그인한 고객이 없다 · 2026-10-23 결정 41).
   */
  function billing() {
    var config = byId('paddle-config');
    if (!config) return;
    var cfg = config.dataset;
    if (!cfg.token) return;
    if (!window.Paddle) { show('billing-blocked', true); return; }   // 광고 차단기 · 네트워크
    var LOCALES = { 'ko': 'ko', 'en': 'en', 'ja': 'ja', 'zh-Hans': 'zh-Hans', 'es': 'es' };  // zh-Hant 은 Paddle 이 지원하지 않아 생략
    var settings = { displayMode: 'overlay' };
    var locale = LOCALES[pageLocale()];
    if (locale) settings.locale = locale;
    if (cfg.env === 'sandbox') Paddle.Environment.set('sandbox');
    Paddle.Initialize({ token: cfg.token, checkout: { settings: settings } });
  }

  // ------------------------------------------------------------------ 결제 확인 중 그림 (앱과 같은 Lottie)

  /**
   * 앱의 로딩 표시와 같은 Lottie 퍼즐 애니메이션 (assets/loading/puzzle_loading.json · lottie-web 5.12.2 light,
   * assets/vendor). 결제 확인 카드를 띄울 때 그때 불러온다 — 결제 페이지를 처음 열 때는 받지 않는다.
   * 못 불러오면 도는 원이 그대로 돈다. 「동작 줄이기」 면 천천히 돈다.
   */
  var waitingAnimation = null;

  function startWaitingAnimation() {
    var box = byId('checkout-loading');
    if (!box || !ASSETS || waitingAnimation) return;
    loadScript(ASSETS + 'vendor/lottie_light.min.js')
      .then(function () {
        if (!window.lottie || waitingAnimation || box.closest('[hidden]')) return;
        waitingAnimation = window.lottie.loadAnimation({
          container: box,
          renderer: 'svg',
          loop: true,
          autoplay: true,
          path: ASSETS + 'loading/puzzle_loading.json'
        });
        if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) waitingAnimation.setSpeed(0.4);
        waitingAnimation.addEventListener('DOMLoaded', function () { box.classList.add('is-lottie'); });
      })
      .catch(function () { /* 도는 원 그대로 */ });
  }

  function stopWaitingAnimation() {
    if (waitingAnimation) {
      waitingAnimation.destroy();
      waitingAnimation = null;
    }
    var box = byId('checkout-loading');
    if (box) box.classList.remove('is-lottie');
  }

  /** 스크립트 하나를 한 번만 불러온다 */
  var scriptLoads = {};
  function loadScript(src) {
    if (!scriptLoads[src]) {
      scriptLoads[src] = new Promise(function (resolve, reject) {
        var tag = document.createElement('script');
        tag.src = src;
        tag.async = true;
        tag.onload = function () { resolve(); };
        tag.onerror = function () { delete scriptLoads[src]; reject(new Error('load failed: ' + src)); };
        document.head.appendChild(tag);
      });
    }
    return scriptLoads[src];
  }

  // ------------------------------------------------------------------ 앱을 여는 중계 페이지 (activate.html)

  function activate() {
    var key = normalizeKey(fragment().get('key'));
    if (!KEY_RE.test(key)) { show('activate-invalid', true); return; }
    fillKey('activate', key);
    show('activate-ready', true);
    // 주소에서 키를 지운다 — 방문 기록 · 화면 공유에 남지 않게 (# 뒤라 서버로는 애초에 가지 않았다)
    try { history.replaceState(null, '', location.pathname + location.search); } catch (e) { /* 그대로 둔다 */ }
    // 메일의 링크를 Mac 에서 눌렀으면 앱을 바로 연다 (브라우저가 열지 묻는다). 휴대폰 · 태블릿에서는 버튼만.
    if (isMacDesktop()) location.href = appUrl(key);
  }

  // ------------------------------------------------------------------ 구매 이메일 양식 (키 다시 받기 · 키 바꾸기)

  /**
   * 구매 이메일 하나를 받아 보내는 양식 — prefix-form · prefix-submit · 안내 prefix-sent · prefix-invalid · prefix-error.
   * 서버는 구매가 있든 없든 같은 답을 하므로(구매 여부가 새지 않게) 보냈다는 안내도 늘 같다.
   */
  function emailForm(prefix, path) {
    var form = byId(prefix + '-form');
    if (!form) return;
    var button = byId(prefix + '-submit');
    form.addEventListener('submit', function (event) {
      event.preventDefault();
      var email = form.elements.email.value.trim();
      show(prefix + '-sent', false);
      show(prefix + '-error', false);
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { show(prefix + '-invalid', true); return; }
      show(prefix + '-invalid', false);
      button.disabled = true;
      post(path, { email: email, locale: pageLocale() })
        .then(function () { show(prefix + '-sent', true); })
        .catch(function (error) {
          if (error && error.code === 'malformed_email') show(prefix + '-invalid', true);
          else show(prefix + '-error', true);
        })
        .then(function () { button.disabled = false; });
    });
  }

  // ------------------------------------------------------------------ 키 다시 받기 (license.html)

  function resend() { emailForm('resend', '/v1/licenses/resend'); }

  // ------------------------------------------------------------------ 키 바꾸기 (rotate.html)

  /** 키 바꾸기 확인 값 — 라이선스 서버가 만든 32바이트 난수의 base64url (43자) */
  var TOKEN_RE = /^[A-Za-z0-9_-]{43}$/;

  /**
   * 메일의 링크(#token=…)로 왔으면 「키 바꾸기」 단추를, 아니면 확인 메일 요청 양식을 보인다.
   * 단추를 눌러야 바뀐다 — 메일 보안 검사기가 링크를 미리 열어도 키는 그대로다.
   * 새 키는 이 페이지에 보여 주지 않는다(구매 이메일로만 간다).
   */
  function rotate() {
    if (!byId('rotate-request')) return;
    var token = fragment().get('token');
    if (token !== null) {
      // 주소에서 확인 값을 지운다 — 방문 기록 · 화면 공유에 남지 않게 (# 뒤라 서버로는 애초에 가지 않았다)
      try { history.replaceState(null, '', location.pathname + location.search); } catch (e) { /* 그대로 둔다 */ }
    }
    if (token === null) show('rotate-request', true);
    else if (!TOKEN_RE.test(token)) requestAgain('rotate-used');
    else show('rotate-confirm', true);

    var confirmButton = byId('rotate-confirm-button');
    confirmButton.addEventListener('click', function () {
      confirmButton.disabled = true;
      show('rotate-confirm-error', false);
      post('/v1/licenses/rotate/confirm', { token: token, locale: pageLocale() })
        .then(function (result) {
          show('rotate-confirm', false);
          if (result.email_hint) {
            byId('rotate-email-hint').textContent = result.email_hint;
            show('rotate-hint-wrap', true);
          }
          show(result.email_sent ? 'rotate-done' : 'rotate-done-unsent', true);
        })
        .catch(function (error) {
          var code = error && error.code;
          if (code === 'rotation_not_found' || code === 'rotation_expired' || code === 'revoked') {
            show('rotate-confirm', false);
            if (code === 'revoked') show('rotate-revoked', true);
            else requestAgain(code === 'rotation_expired' ? 'rotate-expired' : 'rotate-used');
            return;
          }
          // 연결 실패 · 서버 오류 — 같은 링크로 다시 누를 수 있다
          show('rotate-confirm-error', true);
          confirmButton.disabled = false;
        });
    });

    emailForm('rotate', '/v1/licenses/rotate');

    /** 안내 한 줄과 함께 확인 메일 요청 양식을 보인다 (쓴 링크 · 만료된 링크) */
    function requestAgain(noteId) {
      show(noteId, true);
      show('rotate-request', true);
    }
  }

  // ------------------------------------------------------------------ 개인정보 삭제 (erase.html)

  /**
   * 키 바꾸기와 같은 두 모드 — 메일의 링크(#token=…)로 왔으면 삭제되는 내용과 「삭제」 단추를, 아니면 확인 메일 요청 양식을 보인다.
   * 단추를 눌러야 지워진다 — 메일 보안 검사기가 링크를 미리 열어도 그대로다. 서버는 구매가 있든 없든 요청에 같은 답을 한다.
   * 성공하면 해지한 라이선스 수(licenses)를 erase-count 에 채운다. 삭제한 라이선스는 되살리지 못한다.
   */
  function erase() {
    if (!byId('erase-request')) return;
    var token = fragment().get('token');
    if (token !== null) {
      // 주소에서 확인 값을 지운다 — 방문 기록 · 화면 공유에 남지 않게 (# 뒤라 서버로는 애초에 가지 않았다)
      try { history.replaceState(null, '', location.pathname + location.search); } catch (e) { /* 그대로 둔다 */ }
    }
    if (token === null) show('erase-request', true);
    else if (!TOKEN_RE.test(token)) requestAgain('erase-used');
    else show('erase-confirm', true);

    var confirmButton = byId('erase-confirm-button');
    confirmButton.addEventListener('click', function () {
      confirmButton.disabled = true;
      show('erase-confirm-error', false);
      post('/v1/privacy/erase/confirm', { token: token, locale: pageLocale() })
        .then(function (result) {
          show('erase-confirm', false);
          var count = byId('erase-count');
          if (count) count.textContent = String(result.licenses == null ? 0 : result.licenses);
          show('erase-done', true);
        })
        .catch(function (error) {
          var code = error && error.code;
          if (code === 'erase_not_found' || code === 'erase_expired') {
            show('erase-confirm', false);
            requestAgain(code === 'erase_expired' ? 'erase-expired' : 'erase-used');
            return;
          }
          // 연결 실패 · 서버 오류 — 같은 링크로 다시 누를 수 있다
          show('erase-confirm-error', true);
          confirmButton.disabled = false;
        });
    });

    emailForm('erase', '/v1/privacy/erase');

    function requestAgain(noteId) {
      show(noteId, true);
      show('erase-request', true);
    }
  }

  window.ShouArchiveLicense = { checkout: checkout, billing: billing, activate: activate, resend: resend, rotate: rotate, erase: erase };

  // <script src="assets/license.js" data-page="…"> 의 이름으로 바로 실행한다 (스크립트는 </body> 앞에 있어 DOM 은 이미 있다)
  var page = document.currentScript && document.currentScript.dataset.page;
  if (page && Object.prototype.hasOwnProperty.call(window.ShouArchiveLicense, page)) window.ShouArchiveLicense[page]();
})();
