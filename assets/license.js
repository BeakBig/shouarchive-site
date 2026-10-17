/*
 * ShouArchive 라이선스 — 결제 완료 화면 · 앱을 여는 중계 페이지 · 키 다시 받기 · 키 바꾸기.
 * 6개 언어 페이지가 모두 이 파일 하나를 쓴다. 문구는 각 페이지의 HTML 에 있고, 여기서는
 * 보이고 숨기기와 값 채우기만 한다 (그래서 tools/check-site.py 의 언어별 구조 비교를 그대로 통과한다).
 *
 * 라이선스 서버 계약: shouarchive-license 저장소 docs/app-contract.md §2.10 ~ §2.13.
 *   POST /v1/web/checkout             사이트에서 사는 결제를 만든다 → { transaction_id, claim }
 *   POST /v1/purchase/status          결제가 끝나면 그 확인 값으로 키를 받는다 → { status: processing | ready, key, … }
 *   POST /v1/licenses/resend          구매 이메일로 같은 키를 다시 보낸다 → 늘 { status: accepted }
 *   POST /v1/licenses/rotate          구매 이메일로 키 바꾸기 확인 링크를 보낸다 → 늘 { status: accepted }
 *   POST /v1/licenses/rotate/confirm  확인 링크의 값으로 키를 바꾼다 → { status: rotated, email_hint, email_sent }
 * 키 · 확인 값은 주소의 # 뒤에만 둔다 — 브라우저가 서버로 보내지 않아 사이트 로그에 남지 않는다.
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

  function byId(id) { return document.getElementById(id); }
  function show(id, on) { var el = byId(id); if (el) el.hidden = !on; }

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
  }

  // ------------------------------------------------------------------ 결제 페이지 (checkout.html)

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
    var transactionId = params.get('_ptxn');

    if (params.get('done') === '1') {         // 예전 방식으로 돌아온 경우 (successUrl)
      show('checkout-closed', false);
      show('checkout-done', true);
      return;
    }
    if (!cfg.token || !window.Paddle) return;  // 아직 결제를 열지 않음 → 안내만

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
        if (event && event.name === 'checkout.completed') {
          completed((event.data && event.data.transaction_id) || transactionId);
        }
      }
    });
    show('checkout-closed', false);

    // ?_ptxn= (라이선스 서버가 만든 앱 구매 · 갱신 거래) 이면 Paddle.js 가 결제 화면을 스스로 연다.
    if (transactionId) return;
    if (!cfg.priceLicense || !cfg.priceUpdates) { show('checkout-closed', true); return; }
    show('checkout-buy', true);

    byId('checkout-open').addEventListener('click', function () {
      var button = this;
      button.disabled = true;
      post('/v1/web/checkout', { locale: pageLocale() })
        .then(function (result) {
          transactionId = result.transaction_id;
          claim = result.claim;
          Paddle.Checkout.open({ transactionId: transactionId });
        })
        .catch(function () {
          // 라이선스 서버에 닿지 못하면 예전처럼 연다 — 키는 메일로만 받는다
          claim = null;
          Paddle.Checkout.open({ items: [
            { priceId: cfg.priceLicense, quantity: 1 },
            { priceId: cfg.priceUpdates, quantity: 1 }
          ] });
        })
        .then(function () { button.disabled = false; });
    });

    function completed(id) {
      show('checkout-buy', false);
      // Paddle 의 완료 화면을 잠깐 보여 준 뒤 닫고, 이 페이지의 안내로 넘어간다
      setTimeout(function () { try { Paddle.Checkout.close(); } catch (e) { /* 이미 닫힘 */ } }, 1500);
      if (renewal) { show('checkout-renewed', true); return; }
      if (!claim || !id) { show('checkout-done', true); return; }
      show('checkout-processing', true);
      poll(id, 0);
    }

    function poll(id, attempt) {
      post('/v1/purchase/status', { transaction_id: id, claim: claim })
        .then(function (result) {
          if (result.status === 'ready') return ready(result);
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
      show('checkout-slow', true);
    }

    function ready(result) {
      show('checkout-processing', false);
      show('checkout-slow', false);
      if (!result.key) return mailed();  // 서버가 키를 보관하지 않는 설정 — 메일로 받는다
      fillKey('license', result.key);
      show('checkout-ready', true);
      // 앱에서 시작한 결제면 앱을 바로 연다 (브라우저가 열지 묻는다 · 앱은 등록할지 한 번 더 묻는다)
      if (fromApp) location.href = appUrl(result.key);
    }

    function mailed() {
      show('checkout-processing', false);
      show('checkout-slow', false);
      show('checkout-done', true);
    }
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

  window.ShouArchiveLicense = { checkout: checkout, activate: activate, resend: resend, rotate: rotate };
})();
