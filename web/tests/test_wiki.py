import os
import pytest
import wiki  # importable because conftest.py adds web/ to sys.path


def test_find_slug_path_returns_file(wiki_dir, monkeypatch):
    monkeypatch.setattr(wiki, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    result = wiki.find_slug_path('python-3-13')
    assert result is not None
    assert result.endswith('python-3-13.md')


def test_find_slug_path_returns_none_for_missing(wiki_dir, monkeypatch):
    monkeypatch.setattr(wiki, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    result = wiki.find_slug_path('does-not-exist')
    assert result is None


def test_find_slug_path_alphabetical_on_collision(wiki_dir, monkeypatch):
    """When slug exists in two domains, alphabetically first domain wins."""
    ai = wiki_dir / 'wiki' / 'ai'
    ai.mkdir(exist_ok=True)
    (ai / 'python-3-13.md').write_text('---\ntitle: dupe\ntags: []\nupdated: 2026-01-01\nsources: []\n---\ndupe', encoding='utf-8')
    monkeypatch.setattr(wiki, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    result = wiki.find_slug_path('python-3-13')
    assert result is not None
    # 'ai' < 'programming' alphabetically
    assert os.sep + 'ai' + os.sep in result or '/ai/' in result


def test_preprocess_wikilinks_existing(wiki_dir, monkeypatch):
    monkeypatch.setattr(wiki, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    text = 'See [[python-3-13]] for details.'
    result = wiki.preprocess_wikilinks(text)
    assert '[python-3-13](/wiki/python-3-13)' in result


def test_preprocess_wikilinks_broken(wiki_dir, monkeypatch):
    monkeypatch.setattr(wiki, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    text = 'See [[nonexistent-page]] here.'
    result = wiki.preprocess_wikilinks(text)
    assert 'broken-link' in result
    assert 'nonexistent-page' in result


def test_preprocess_wikilinks_pipe_alias(wiki_dir, monkeypatch):
    monkeypatch.setattr(wiki, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    text = 'See [[python-3-13|Python]] for details.'
    result = wiki.preprocess_wikilinks(text)
    assert '[Python](/wiki/python-3-13)' in result


def test_parse_page_returns_title(wiki_dir, monkeypatch):
    monkeypatch.setattr(wiki, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    path = str(wiki_dir / 'wiki' / 'programming' / 'python-3-13.md')
    page = wiki.parse_page(path)
    assert page['title'] == 'Python 3.13'


def test_parse_page_returns_tags(wiki_dir, monkeypatch):
    monkeypatch.setattr(wiki, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    path = str(wiki_dir / 'wiki' / 'programming' / 'python-3-13.md')
    page = wiki.parse_page(path)
    assert 'python' in page['tags']


def test_parse_page_body_is_html(wiki_dir, monkeypatch):
    monkeypatch.setattr(wiki, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    path = str(wiki_dir / 'wiki' / 'programming' / 'python-3-13.md')
    page = wiki.parse_page(path)
    assert '<h2' in page['body']  # '## JIT' rendered as h2


def test_parse_page_wikilinks_converted(wiki_dir, monkeypatch):
    monkeypatch.setattr(wiki, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    path = str(wiki_dir / 'wiki' / 'programming' / 'python-3-13.md')
    page = wiki.parse_page(path)
    assert '/wiki/artemis-ii-fault-tolerant-computer' in page['body']


def test_build_backlink_index(wiki_dir, monkeypatch):
    monkeypatch.setattr(wiki, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    index = wiki.build_backlink_index()
    # python-3-13.md links to artemis-ii-fault-tolerant-computer
    assert 'python-3-13' in index.get('artemis-ii-fault-tolerant-computer', [])


def test_get_sidebar_data_lists_pages(wiki_dir, monkeypatch):
    monkeypatch.setattr(wiki, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    sidebar = wiki.get_sidebar_data()
    assert 'programming' in sidebar
    assert 'python-3-13' in sidebar['programming']


def test_get_sidebar_data_empty_domain(wiki_dir, monkeypatch):
    monkeypatch.setattr(wiki, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    sidebar = wiki.get_sidebar_data()
    assert sidebar['ai'] == []
