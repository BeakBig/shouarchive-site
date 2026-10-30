#!/usr/bin/env python3
"""sandbox 결제 사이트(https://shouarchive-sandbox.beakbig.com)를 만들어 올린다 (2026-10-30).

운영 사이트와 같은 파일(지금 브랜치의 마지막 커밋)을 임시 폴더에 풀고, 아래 sandbox 값으로 바꿔 다시 만든 뒤
`npx wrangler deploy --env sandbox`(wrangler.jsonc 의 env.sandbox — Worker shouarchive-sandbox)로 올린다.
저장소의 파일은 건드리지 않는다 — 운영 HTML · pricing.json 은 그대로다.

  python3 tools/deploy-sandbox.py             # 만들고 올린다
  python3 tools/deploy-sandbox.py --dry-run   # 만들기만 하고 폴더를 알려 준다 (올리지 않음)

sandbox 값
  pricing.json  paddle.environment = sandbox · checkout_open = true · license_api = sandbox 라이선스 서버
                commercial.checkout = 이 사이트의 /checkout (구매 버튼이 보인다 — 출시 화면 미리보기)
  _headers      connect-src 에 sandbox 라이선스 서버 · X-Robots-Tag noindex (검색에 안 나오게)
  license.js    「앱에서 바로 등록」 링크를 shouarchive-sandbox:// 로 — 앱 Debug 빌드만 받아 「sandbox 서버」 로 바꿔 등록한다
                (출시판 앱은 이 스킴이 없어 열리지 않는다)
  style.css     화면 위에 「SANDBOX — 테스트 카드로만 결제됩니다」 띠

sandbox 라이선스 서버(shouarchive-license-staging)의 SITE_ORIGINS · SITE_CHECKOUT_URL 이 이 사이트 주소여야 하고,
Paddle sandbox 의 기본 결제 링크도 이 사이트의 /checkout 이어야 한다.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://shouarchive-sandbox.beakbig.com'
LICENSE_API = 'https://license-staging.beakbig.com'
BANNER = '''
/* sandbox 사이트 표시 (tools/deploy-sandbox.py 가 sandbox 판에만 붙인다) */
body::before { content: "SANDBOX — 테스트 카드로만 결제됩니다 · Test cards only"; display: block; position: sticky; top: 0; z-index: 1000;
  padding: 6px 12px; background: #b45309; color: #fff; font: 600 12.5px/1.4 -apple-system, system-ui, sans-serif; text-align: center; }
'''


def run(cmd, cwd):
    print('$ ' + ' '.join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def main():
    dry = '--dry-run' in sys.argv[1:]
    commit = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, check=True,
                            capture_output=True, text=True).stdout.strip()
    if subprocess.run(['git', 'status', '--porcelain'], cwd=ROOT, capture_output=True, text=True).stdout.strip():
        print('알림: 커밋하지 않은 변경은 들어가지 않습니다 — 마지막 커밋(%s)으로 만듭니다.' % commit)

    out = tempfile.mkdtemp(prefix='shouarchive-sandbox-')
    archive = subprocess.run(['git', 'archive', 'HEAD'], cwd=ROOT, check=True, capture_output=True).stdout
    subprocess.run(['tar', '-x', '-C', out], input=archive, check=True)

    path = os.path.join(out, 'tools', 'pricing.json')
    cfg = json.load(open(path, encoding='utf-8'))
    cfg['paddle']['environment'] = 'sandbox'
    cfg['paddle']['checkout_open'] = True
    cfg['paddle']['license_api'] = LICENSE_API
    cfg['commercial']['checkout'] = SITE + '/checkout'
    json.dump(cfg, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

    run([sys.executable, os.path.join(out, 'tools', 'fill-pricing.py')], out)

    headers = os.path.join(out, '_headers')
    text = open(headers, encoding='utf-8').read()
    old = 'https://license.beakbig.com'
    assert text.count(old) >= 1, '_headers 에 라이선스 서버 주소가 없습니다'
    text = text.replace(old, LICENSE_API)
    assert text.count('/*\n') == 1, '_headers 의 /* 규칙을 찾지 못했습니다'
    text = text.replace('/*\n', '/*\n  X-Robots-Tag: noindex, nofollow\n')
    open(headers, 'w', encoding='utf-8').write(text)

    script = os.path.join(out, 'assets', 'license.js')
    text = open(script, encoding='utf-8').read()
    old = "'shouarchive://activate?key='"
    assert text.count(old) == 1, 'license.js 의 앱 링크를 찾지 못했습니다'
    open(script, 'w', encoding='utf-8').write(text.replace(old, "'shouarchive-sandbox://activate?key='"))

    with open(os.path.join(out, 'assets', 'style.css'), 'a', encoding='utf-8') as css:
        css.write(BANNER)

    run([sys.executable, os.path.join(out, 'tools', 'check-site.py')], out)

    if dry:
        print('\n만들기만 했습니다 (커밋 %s): %s' % (commit, out))
        return
    run(['npx', 'wrangler', 'deploy', '--config', os.path.join(out, 'wrangler.jsonc'), '--env', 'sandbox'], ROOT)
    shutil.rmtree(out, ignore_errors=True)
    print('\n올렸습니다 (커밋 %s): %s' % (commit, SITE))


if __name__ == '__main__':
    main()
