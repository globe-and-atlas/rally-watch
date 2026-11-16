"""Public verification handles gallery duplication and bounded HTTP failures."""
from pathlib import Path
import importlib.util
import io
import urllib.error
import pytest

ROOT = Path(__file__).resolve().parents[1]


def verifier():
    spec = importlib.util.spec_from_file_location('public_verifier', ROOT / 'execution/verify_public.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_gallery_order_and_deduplication():
    module = verifier()
    parser = module.Listing('example')
    first = 'https://assets.repebble.com/screenshots/example/emery/first.gif'
    second = first.replace('first.gif', 'second.png')
    parser.feed(f'<img src="{first}"><img src="{first}"><img src="{second}">')
    assert parser.previews == [first, second]


def test_transient_retry_is_bounded(monkeypatch):
    module = verifier()
    attempts = []
    def fail(request, timeout):
        attempts.append(timeout)
        raise urllib.error.HTTPError(request.full_url, 503, 'temporary', {}, io.BytesIO())
    monkeypatch.setattr(module.urllib.request, 'urlopen', fail)
    monkeypatch.setattr(module.time, 'sleep', lambda delay: None)
    with pytest.raises(urllib.error.HTTPError):
        module.fetch('https://apps.repebble.com/example')
    assert attempts == [30] * 4


def test_auth_failure_is_not_retried(monkeypatch):
    module = verifier()
    attempts = []
    def fail(request, timeout):
        attempts.append(timeout)
        raise urllib.error.HTTPError(request.full_url, 401, 'unauthorized', {}, io.BytesIO())
    monkeypatch.setattr(module.urllib.request, 'urlopen', fail)
    with pytest.raises(urllib.error.HTTPError):
        module.fetch('https://apps.repebble.com/example')
    assert len(attempts) == 1


def test_unexpected_host_rejected():
    with pytest.raises(ValueError):
        verifier().fetch('https://unrelated.example/file')
