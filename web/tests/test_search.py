import pytest
import search


def test_build_search_index_includes_pages(wiki_dir, monkeypatch):
    monkeypatch.setattr(search, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    index = search.build_search_index()
    slugs = [p['slug'] for p in index]
    assert 'python-3-13' in slugs


def test_build_search_index_excludes_gitkeep(wiki_dir, monkeypatch):
    monkeypatch.setattr(search, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    index = search.build_search_index()
    slugs = [p['slug'] for p in index]
    assert '.gitkeep' not in slugs


def test_search_finds_title_match(wiki_dir, monkeypatch):
    monkeypatch.setattr(search, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    index = search.build_search_index()
    results = search.search(index, 'Python')
    slugs = [r['slug'] for r in results]
    assert 'python-3-13' in slugs


def test_search_finds_body_match(wiki_dir, monkeypatch):
    monkeypatch.setattr(search, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    index = search.build_search_index()
    results = search.search(index, 'Redundant')
    slugs = [r['slug'] for r in results]
    assert 'artemis-ii-fault-tolerant-computer' in slugs


def test_search_is_case_insensitive(wiki_dir, monkeypatch):
    monkeypatch.setattr(search, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    index = search.build_search_index()
    results = search.search(index, 'python')
    slugs = [r['slug'] for r in results]
    assert 'python-3-13' in slugs


def test_search_returns_snippet(wiki_dir, monkeypatch):
    monkeypatch.setattr(search, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    index = search.build_search_index()
    results = search.search(index, 'JIT')
    match = next(r for r in results if r['slug'] == 'python-3-13')
    assert 'JIT' in match['snippet'] or 'jit' in match['snippet'].lower()


def test_search_empty_query_returns_empty(wiki_dir, monkeypatch):
    monkeypatch.setattr(search, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    index = search.build_search_index()
    results = search.search(index, '')
    assert results == []
