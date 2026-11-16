"""Publish the user-authorized GIF-first release through the Pebble SDK CLI."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true', help='Perform the authorized public upload')
    args = parser.parse_args()
    store = ROOT / 'media/store'
    spec = json.loads((store / 'spec.json').read_text())
    manifest = json.loads((store / 'manifest.json').read_text())
    package = json.loads((ROOT / 'watchface/package.json').read_text())
    screenshots = [store / name for name in manifest['screenshots']]
    assert screenshots[0].suffix == '.gif'
    assert len(screenshots) == 5 and all(path.is_file() for path in screenshots)
    assert hashlib.sha256(screenshots[0].read_bytes()).hexdigest() == manifest['gif_sha256']
    if not args.publish:
        print(f"READY: {spec['name']} {package['version']}, palette GIF first, four stills")
        return
    receipt_path = ROOT / 'release/store-release.json'
    if receipt_path.exists():
        raise SystemExit('A publication receipt exists; inspect the existing public release before another upload.')
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(('RALLY_', 'TERM_', 'LEDGER_'))}
    subprocess.run(['python3', 'execution/build.py'], cwd=ROOT, env=env, check=True,
                   stdout=subprocess.DEVNULL)
    subprocess.run(['python3', 'execution/verify.py'], cwd=ROOT, env=env, check=True)
    command = ['pebble', 'publish', '--non-interactive', '--is-published',
               '--no-gif-all-platforms', '--replace-screenshots', '--name', spec['name'],
               '--version', package['version'], '--description', (store / 'description.txt').read_text(),
               '--icon-small', str(store / 'icon-small.png'), '--icon-large', str(store / 'icon-large.png'),
               '--release-notes', 'First release: color palettes, custom colors, 12/24-hour time, date options and battery.',
               '--screenshots'] + [str(path) for path in screenshots]
    log_path = ROOT / '.tmp/publish.log'
    with log_path.open('w') as log:
        result = subprocess.run(command, cwd=ROOT / 'watchface', env=env,
                                stdout=log, stderr=subprocess.STDOUT, timeout=600)
    output = log_path.read_text()
    if result.returncode:
        raise SystemExit(f'Publish failed (exit {result.returncode}); inspect .tmp/publish.log before retrying.')
    matches = re.findall(r'App page: https://apps\.repebble\.com/([a-zA-Z0-9]+)', output, re.I)
    if not matches:
        raise SystemExit('Upload returned no app-page identity. Inspect log before retrying.')
    bundle = ROOT / 'watchface/build/watchface.pbw'
    for folder in ['dist', 'release']:
        destination = ROOT / folder / f"{spec['slug']}-{package['version']}.pbw"
        shutil.copy2(bundle, destination)
    receipt = {'name': spec['name'], 'app_id': matches[-1], 'version': package['version'],
               'url': 'https://apps.repebble.com/' + matches[-1],
               'uuid': package['pebble']['uuid'],
               'pbw_sha256': hashlib.sha256(bundle.read_bytes()).hexdigest(),
               'public_verified': False}
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    build_meta = {'name': receipt['name'], 'version': receipt['version'], 'uuid': receipt['uuid'],
                  'sha256': receipt['pbw_sha256'], 'published': True, 'url': receipt['url']}
    (ROOT / 'release/build.json').write_text(json.dumps(build_meta, indent=2) + '\n')
    print(json.dumps(receipt))
    if 'Screenshot upload warnings:' in output:
        raise SystemExit('Release created but screenshot upload warnings require inspection.')


if __name__ == '__main__':
    main()
