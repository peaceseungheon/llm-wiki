import os
import re
import glob

WIKI_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WIKI_DIR = os.path.join(WIKI_ROOT, 'wiki')


def find_slug_path(slug: str) -> str | None:
    """Return the file path for slug, searching all domain folders.
    If multiple matches exist, returns the first by alphabetical domain name."""
    matches = sorted(glob.glob(os.path.join(WIKI_DIR, '**', f'{slug}.md'), recursive=True))
    return matches[0] if matches else None


def preprocess_wikilinks(content: str) -> str:
    """Convert [[WikiLink]] to markdown links (existing) or broken-link spans (missing)."""
    def replace(match):
        raw = match.group(1)
        parts = raw.split('|', 1)
        link_target = parts[0].strip()
        display_text = parts[1].strip() if len(parts) > 1 else link_target
        slug = link_target.lower().replace(' ', '-')
        if find_slug_path(slug):
            return f'[{display_text}](/wiki/{slug})'
        return f'<span class="broken-link">{display_text}</span>'

    return re.sub(r'\[\[([^\]]+)\]\]', replace, content)
