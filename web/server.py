import os
import sys

# Ensure web/ is on the path when run as `python web/server.py` from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, abort, request
import wiki as wiki_module
import search as search_module

WIKI_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

app = Flask(__name__, template_folder='templates', static_folder='static')

# Build indexes on startup
try:
    backlinks = wiki_module.build_backlink_index()
    search_index = search_module.build_search_index()
    sidebar = wiki_module.get_sidebar_data()
except Exception:
    backlinks = {}
    search_index = {}
    sidebar = {}


@app.route('/')
def home():
    path = os.path.join(WIKI_ROOT, 'index.md')
    if not os.path.exists(path):
        abort(404)
    page = wiki_module.parse_page(path)
    return render_template('page.html', page=page, backlinks=[],
                           sidebar=sidebar, current_slug='index')


@app.route('/wiki/<slug>')
def wiki_page(slug):
    path = wiki_module.find_slug_path(slug)
    if not path:
        abort(404)
    page = wiki_module.parse_page(path)
    return render_template('page.html', page=page,
                           backlinks=backlinks.get(slug, []),
                           sidebar=sidebar, current_slug=slug)


@app.route('/search')
def search_page():
    query = request.args.get('q', '').strip()
    results = search_module.search(search_index, query) if query else []
    return render_template('search.html', query=query, results=results,
                           sidebar=sidebar, current_slug='')


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html', sidebar=sidebar, current_slug=''), 404


if __name__ == '__main__':
    app.run(port=8000, debug=False)
