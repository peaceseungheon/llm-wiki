import os
import re
import glob

WIKI_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WIKI_DIR = os.path.join(WIKI_ROOT, 'wiki')


def find_slug_path(slug: str) -> str | None:
    """Return the file path for slug, searching all domain folders.
    If multiple matches exist, returns the first by alphabetical domain name."""
    matches = sorted(glob.glob(os.path.join(WIKI_DIR, '*', f'{slug}.md')))
    return matches[0] if matches else None


def preprocess_wikilinks(content: str) -> str:
    """Convert [[WikiLink]] to markdown links (existing) or broken-link spans (missing)."""
    def replace(match):
        text = match.group(1)
        slug = text.lower().replace(' ', '-')
        if find_slug_path(slug):
            return f'[{text}](/wiki/{slug})'
        return f'<span class="broken-link">{text}</span>'

    return re.sub(r'\[\[([^\]]+)\]\]', replace, content)
