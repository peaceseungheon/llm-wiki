import os
import re
import glob
import frontmatter
import markdown as md_lib

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


def parse_page(path: str) -> dict:
    """Parse a wiki page file into a dict with title, tags, updated, sources, body (HTML), toc (HTML)."""
    try:
        post = frontmatter.load(path)
    except Exception as exc:
        raise ValueError(f"Failed to parse frontmatter in {path}: {exc}") from exc
    processed = preprocess_wikilinks(post.content)
    converter = md_lib.Markdown(extensions=['toc', 'fenced_code', 'tables'])
    body = converter.convert(processed)
    return {
        'title': post.get('title', os.path.basename(path).replace('.md', '')),
        'tags': post.get('tags', []),
        'updated': post.get('updated', None),
        'sources': post.get('sources', []),
        'body': body,
        'toc': converter.toc,
    }


def build_backlink_index() -> dict[str, list[str]]:
    """Scan all wiki pages and return {target_slug: [linking_slugs]}."""
    index: dict[str, list[str]] = {}
    for path in glob.glob(os.path.join(WIKI_DIR, '**', '*.md'), recursive=True):
        slug = os.path.basename(path).replace('.md', '')
        if slug == '.gitkeep':
            continue
        try:
            post = frontmatter.load(path)
            for match in re.finditer(r'\[\[([^\]]+)\]\]', post.content):
                # Handle pipe alias: [[Target|Alias]] → use Target for slug
                raw = match.group(1)
                link_target = raw.split('|', 1)[0].strip()
                target = link_target.lower().replace(' ', '-')
                index.setdefault(target, [])
                if slug not in index[target]:
                    index[target].append(slug)
        except Exception:
            pass
    return index


def get_sidebar_data() -> dict[str, list[str]]:
    """Return {domain: [slugs]} for all wiki domains, in fixed display order."""
    domains = ['programming', 'ai', 'politics', '_concepts']
    result: dict[str, list[str]] = {}
    for domain in domains:
        domain_dir = os.path.join(WIKI_DIR, domain)
        if os.path.isdir(domain_dir):
            slugs = [
                os.path.basename(f).replace('.md', '')
                for f in sorted(glob.glob(os.path.join(domain_dir, '*.md')))
            ]
            result[domain] = [s for s in slugs if s != '.gitkeep']
        else:
            result[domain] = []
    return result
