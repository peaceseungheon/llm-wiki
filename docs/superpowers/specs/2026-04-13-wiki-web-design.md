# Wiki Web Interface — Design Spec

**Date:** 2026-04-13  
**Status:** Approved

## Overview

Wikipedia-style web interface for the llm-wiki personal knowledge system. Serves markdown wiki pages over HTTP at port 8000 with full-text search, automatic TOC generation, and backlink tracking.

## Requirements

- Python (Flask) backend — no Node.js
- Port 8000
- Files in `web/` directory
- Read-only viewer (no editing)
- Manual browser refresh to pick up file changes (no live reload)
- Features: [[WikiLinks]] rendering, full-text search, auto TOC, backlinks

## Architecture

```
web/
├── server.py          # Flask app entry point, routing
├── wiki.py            # Markdown parsing, WikiLinks conversion, backlink index
├── search.py          # In-memory full-text search
├── templates/
│   ├── base.html      # Shared layout (top nav, left sidebar, search bar)
│   ├── page.html      # Wiki page (TOC box + body + backlinks + sources)
│   └── search.html    # Search results page
└── static/
    └── style.css      # Wikipedia-style CSS
```

## Routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Renders `index.md` as home page |
| GET | `/wiki/<slug>` | Finds and renders `wiki/*/<slug>.md` |
| GET | `/search?q=<query>` | Full-text search results |

## Components

### `wiki.py` — Core Parser

Responsibilities:
- Parse YAML frontmatter with `python-frontmatter`
- Convert `[[WikiLink]]` to `<a href="/wiki/slug">WikiLink</a>` via regex; auto-detect domain by globbing `wiki/*/slug.md`
- Render markdown to HTML using `markdown` library with `toc` extension
- Build backlink reverse index on startup: `{slug: [linking_slugs]}`
- Slug → file path resolution: glob `wiki/*/slug.md` across all domains; if multiple matches exist, first result (alphabetical domain order) wins
- Broken WikiLinks (slug not found) render as red unlinked text

### `search.py` — In-Memory Search

Responsibilities:
- On startup, load title + tags + body of all wiki pages into memory
- Keyword search: case-insensitive substring match across all fields
- Return results with matched snippet (surrounding context of first match)
- No database; pure Python sufficient for hundreds of pages

### `templates/base.html` — Layout

Structure:
- **Top bar**: Site title ("LLM Wiki") + search input
- **Left sidebar** (180px): Domain folders (programming / ai / politics / _concepts) with page list; empty domains shown greyed out
- **Main content area**: Page content injected here

### `templates/page.html` — Wiki Page

Structure:
- Page title (H1) + tags (colored badges) + updated date
- Floating TOC box (top-right) — auto-generated from H2/H3 headings
- Rendered markdown body with clickable WikiLinks
- **Backlinks section** at bottom (← 이 페이지를 링크한 페이지)
- Sources box (from frontmatter `sources` list)

### `static/style.css` — Wikipedia Style

- Clean serif/sans-serif typography matching Wikipedia aesthetics
- Blue link color (#3366cc), visited links (#6611cc)
- TOC box: light grey background, right-floated
- Tags: light blue badge style
- Backlinks: visually separated with top border

## Startup

```bash
cd web
pip install flask markdown python-frontmatter
python server.py
# → http://localhost:8000
```

On startup, `server.py`:
1. Scans all `wiki/**/*.md` files
2. Builds backlink reverse index in memory
3. Builds search index in memory
4. Starts Flask on port 8000

## Dependencies

```
flask
markdown
python-frontmatter
```

## Non-Goals

- Editing wiki pages through the browser
- Live reload on file change
- User authentication
- Graph/network view
- Obsidian plugin integration
