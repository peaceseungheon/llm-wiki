import os
import sys
import pytest

# Ensure web/ is on path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import wiki
import search


@pytest.fixture
def app(wiki_dir, monkeypatch):
    monkeypatch.setattr(wiki, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    monkeypatch.setattr(search, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    import server
    # Rebuild indexes using patched WIKI_DIR, then inject into server globals
    monkeypatch.setattr(server, 'backlinks', wiki.build_backlink_index())
    monkeypatch.setattr(server, 'search_index', search.build_search_index())
    monkeypatch.setattr(server, 'sidebar', wiki.get_sidebar_data())
    server.app.config['TESTING'] = True
    return server.app


@pytest.fixture
def client(app):
    return app.test_client()


def test_home_returns_200_or_404(client):
    # index.md doesn't exist in wiki_dir temp, expect 404 — just verify no 500 crash
    resp = client.get('/')
    assert resp.status_code in (200, 404)


def test_wiki_page_returns_200(client):
    resp = client.get('/wiki/python-3-13')
    assert resp.status_code == 200


def test_wiki_page_contains_title(client):
    resp = client.get('/wiki/python-3-13')
    assert b'Python 3.13' in resp.data


def test_wiki_page_contains_toc(client):
    resp = client.get('/wiki/python-3-13')
    # Page has ## JIT heading, so TOC div should appear
    assert b'toc' in resp.data.lower()


def test_wiki_page_404_for_missing(client):
    resp = client.get('/wiki/does-not-exist')
    assert resp.status_code == 404


def test_search_returns_200(client):
    resp = client.get('/search?q=Python')
    assert resp.status_code == 200


def test_search_shows_result(client):
    resp = client.get('/search?q=Python')
    assert b'python-3-13' in resp.data or b'Python 3.13' in resp.data


def test_search_empty_query(client):
    resp = client.get('/search?q=')
    assert resp.status_code == 200
