"""Verify public listing order and exact downloaded release assets."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import io
import json
import random
import time
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HOSTS = {'apps.repebble.com', 'assets.repebble.com', 'appstore-api.repebble.com',
         'pebble-appstore-backend.497e529f13ec4afbfce4dfe3cfd3634d.r2.cloudflarestorage.com'}


def fetch(url: str) -> bytes:
    if urllib.parse.urlparse(url).hostname not in HOSTS:
        raise ValueError('Unexpected public asset host')
    request = urllib.request.Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'NativeWatchfaceReleaseVerifier/1'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                if urllib.parse.urlparse(response.url).hostname not in HOSTS:
                    raise ValueError('Unexpected redirect host')
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code not in {408, 425, 429, 500, 502, 503, 504} or attempt == 3:
                raise
            retry = error.headers.get('Retry-After', '')
            delay = min(float(retry), 15) if retry.isdigit() else 2 ** attempt + random.random()
        except (urllib.error.URLError, TimeoutError):
            if attempt == 3:
                raise
            delay = 2 ** attempt + random.random()
        time.sleep(delay)
    raise RuntimeError('Unreachable retry state')


class Listing(HTMLParser):
    def __init__(self, app_id: str):
        super().__init__()
        self.app_id = app_id
        self.previews: list[str] = []
        self.downloads: list[str] = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'img':
            url = values.get('src', '')
            parsed = urllib.parse.urlparse(url)
            if parsed.path.startswith('/_next/image'):
                url = urllib.parse.parse_qs(parsed.query).get('url', [''])[0]
            if f'/screenshots/{self.app_id}/emery/' in url and url not in self.previews:
                self.previews.append(url)
        if tag == 'a':
            url = values.get('href', '')
            if '.pbw' in url and url not in self.downloads:
                self.downloads.append(url)


def main() -> None:
    receipt_path = ROOT / 'release/store-release.json'
    receipt = json.loads(receipt_path.read_text())
    store = ROOT / 'media/store'
    manifest = json.loads((store / 'manifest.json').read_text())
    spec = json.loads((store / 'spec.json').read_text())
    output = ROOT / '.tmp/public-release'
    output.mkdir(parents=True, exist_ok=True)
    for attempt in range(8):
        html = fetch(receipt['url'] + '?release_check=' + str(time.time_ns())).decode('utf-8')
        listing = Listing(receipt['app_id'])
        listing.feed(html)
        if (len(listing.previews) == 5 and listing.previews[0].split('?')[0].endswith('.gif')
                and any('/' + receipt['version'] + '/' in url for url in listing.downloads)):
            break
        print(f'Waiting for public assets: attempt {attempt + 1}', flush=True)
        time.sleep(2)
    else:
        (output / 'listing.html').write_text(html)
        raise AssertionError('Public listing does not expose the requested version/GIF-first gallery')
    (output / 'listing.html').write_text(html)
    assert spec['name'] in html, 'Public app name differs'
    for index, url in enumerate(listing.previews):
        data = fetch(url)
        local = store / manifest['screenshots'][index]
        (output / local.name).write_bytes(data)
        if index == 0:
            assert data == local.read_bytes(), 'Public GIF differs'
        else:
            assert Image.open(io.BytesIO(data)).convert('RGB').tobytes() == Image.open(local).convert('RGB').tobytes(), 'Public still differs'
    pbw_url = next(url for url in listing.downloads if '/' + receipt['version'] + '/' in url)
    pbw = fetch(pbw_url)
    (output / 'download.pbw').write_bytes(pbw)
    assert hashlib.sha256(pbw).hexdigest() == receipt['pbw_sha256'], 'Public PBW differs'
    proof = {'name': receipt['name'], 'url': receipt['url'], 'version': receipt['version'],
             'preview_urls': listing.previews, 'pbw_url': pbw_url,
             'gif_first': True, 'exact_gif': True, 'exact_pbw': True, 'four_stills_match': True}
    (output / 'verification.json').write_text(json.dumps(proof, indent=2) + '\n')
    receipt['public_verified'] = True
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(proof))


if __name__ == '__main__':
    main()
