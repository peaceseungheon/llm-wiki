import os
import sys
import pytest

# Make `web/` importable as a package root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def wiki_dir(tmp_path):
    """Creates a minimal temp wiki tree and returns its path."""
    prog = tmp_path / 'wiki' / 'programming'
    prog.mkdir(parents=True)
    politics = tmp_path / 'wiki' / 'politics'
    politics.mkdir(parents=True)
    ai = tmp_path / 'wiki' / 'ai'
    ai.mkdir(parents=True)

    (prog / 'python-3-13.md').write_text(
        '---\ntitle: "Python 3.13"\ntags: [programming, python]\nupdated: 2026-04-13\nsources:\n  - https://example.com\n---\n\n# Python 3.13\n\nSee also [[artemis-ii-fault-tolerant-computer]].\n\n## JIT\n\nFast.',
        encoding='utf-8',
    )
    (prog / 'artemis-ii-fault-tolerant-computer.md').write_text(
        '---\ntitle: "Artemis II"\ntags: [programming]\nupdated: 2026-04-13\nsources: []\n---\n\n# Artemis II\n\nRedundant CPUs.',
        encoding='utf-8',
    )
    (politics / 'trump-hormuz-blockade-2026.md').write_text(
        '---\ntitle: "Trump Hormuz"\ntags: [politics]\nupdated: 2026-04-13\nsources: []\n---\n\n# Trump Hormuz\n\nBlockade.',
        encoding='utf-8',
    )
    return tmp_path
