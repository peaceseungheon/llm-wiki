import os
import glob
import frontmatter

WIKI_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WIKI_DIR = os.path.join(WIKI_ROOT, 'wiki')


def build_search_index() -> list[dict]:
    """Load title + tags + body of all wiki pages into memory."""
    index = []
    for path in glob.glob(os.path.join(WIKI_DIR, '**', '*.md'), recursive=True):
        slug = os.path.basename(path).replace('.md', '')
        if slug == '.gitkeep':
            continue
        try:
            post = frontmatter.load(path)
            index.append({
                'slug': slug,
                'title': post.get('title', slug),
                'tags': ' '.join(post.get('tags', [])),
                'body': post.content,
            })
        except Exception:
            pass
    return index


def search(index: list[dict], query: str) -> list[dict]:
    """Case-insensitive keyword search across title, tags, and body. Returns [] for empty query."""
    if not query:
        return []
    q = query.lower()
    results = []
    for page in index:
        combined = f"{page['title']} {page['tags']} {page['body']}".lower()
        if q in combined:
            results.append({
                'slug': page['slug'],
                'title': page['title'],
                'snippet': _extract_snippet(page['body'], q),
            })
    return results


def _extract_snippet(body: str, query: str, context: int = 100) -> str:
    """Return the text surrounding the first occurrence of query in body."""
    body_lower = body.lower()
    idx = body_lower.find(query)
    if idx == -1:
        return (body[:context * 2] + '...') if len(body) > context * 2 else body
    start = max(0, idx - context)
    end = min(len(body), idx + len(query) + context)
    snippet = body[start:end]
    if start > 0:
        snippet = '...' + snippet
    if end < len(body):
        snippet = snippet + '...'
    return snippet
