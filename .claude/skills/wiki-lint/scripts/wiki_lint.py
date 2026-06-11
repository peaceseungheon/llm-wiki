"""LLM Wiki 구조 점검 도구.

위키 루트(wiki/ 와 index.md가 있는 디렉터리)에서 실행:
    python .claude/skills/wiki-lint/scripts/wiki_lint.py [--root PATH] [--json]

검사 항목:
  [ERROR]  frontmatter 누락/형식 오류 (title, type, tags, updated, sources)
  [ERROR]  잘못된 type / maturity 값, concept·entity의 maturity 누락
  [ERROR]  첫 태그가 도메인명과 불일치
  [ERROR]  파일명 kebab-case 위반
  [ERROR]  깨진 [[WikiLinks]] (존재하지 않는 페이지 참조)
  [ERROR]  index.md에 없는 페이지
  [ERROR]  도메인 MOC에 등재되지 않은 페이지 / MOC 자체가 없는 도메인
  [WARN]   moc/event 페이지에 불필요한 maturity
  [WARN]   어떤 페이지도 링크하지 않는 고아 페이지 (index 제외)
  [INFO]   오래된 페이지 (updated 6개월 초과), 빈 도메인, maturity 분포

종료 코드: ERROR가 하나라도 있으면 1, 아니면 0.
"""
import argparse
import glob
import json
import os
import re
import sys
from datetime import date, datetime, timedelta

REQUIRED_FIELDS = ['title', 'type', 'tags', 'updated', 'sources']
VALID_TYPES = {'concept', 'moc', 'event', 'entity'}
VALID_MATURITY = {'seed', 'growing', 'solid'}
MATURITY_REQUIRED = {'concept', 'entity'}
MATURITY_OMITTED = {'moc', 'event'}
DOMAIN_TAG_ALIAS = {'_concepts': 'concepts'}  # 폴더명 → 태그명
STALE_DAYS = 183
KEBAB_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
WIKILINK_RE = re.compile(r'\[\[([^\]]+)\]\]')


def parse_frontmatter(text):
    """Return (metadata dict, body str). 단순 YAML 서브셋 파서 (외부 의존성 없음)."""
    if not text.startswith('---'):
        return None, text
    end = text.find('\n---', 3)
    if end == -1:
        return None, text
    raw = text[3:end].strip('\n')
    body = text[end + 4:]
    meta = {}
    current_list_key = None
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith('#'):
            continue
        if line.startswith((' ', '\t')) and line.strip().startswith('- '):
            if current_list_key:
                meta[current_list_key].append(line.strip()[2:].strip())
            continue
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip()
            if value == '':
                meta[key] = []
                current_list_key = key
            elif value == '[]':
                meta[key] = []
                current_list_key = None
            elif value.startswith('[') and value.endswith(']'):
                meta[key] = [v.strip().strip('"\'') for v in value[1:-1].split(',') if v.strip()]
                current_list_key = None
            else:
                meta[key] = value.strip('"\'')
                current_list_key = None
    return meta, body


def normalize_link(raw):
    """[[Target|Alias]] / [[Target#Section]] → target slug."""
    target = raw.split('|', 1)[0].split('#', 1)[0].strip()
    return target.lower().replace(' ', '-')


def parse_updated(value):
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


def load_pages(wiki_dir):
    pages = {}
    for path in sorted(glob.glob(os.path.join(wiki_dir, '**', '*.md'), recursive=True)):
        slug = os.path.basename(path)[:-3]
        rel = os.path.relpath(path, wiki_dir)
        domain = rel.replace('\\', '/').split('/')[0]
        with open(path, encoding='utf-8') as f:
            text = f.read()
        meta, body = parse_frontmatter(text)
        pages[slug] = {
            'slug': slug, 'path': path, 'rel': rel.replace('\\', '/'),
            'domain': domain, 'meta': meta, 'body': body,
            'links': [normalize_link(m) for m in WIKILINK_RE.findall(body or '')],
        }
    return pages


def lint(root):
    wiki_dir = os.path.join(root, 'wiki')
    index_path = os.path.join(root, 'index.md')
    errors, warnings, infos = [], [], []

    if not os.path.isdir(wiki_dir):
        return [f'wiki/ 디렉터리가 없음: {wiki_dir}'], [], []
    pages = load_pages(wiki_dir)
    slugs = set(pages)
    index_text = ''
    if os.path.isfile(index_path):
        with open(index_path, encoding='utf-8') as f:
            index_text = f.read()
    else:
        errors.append('index.md가 없음')

    domains = sorted({p['domain'] for p in pages.values()})

    # --- 페이지별 frontmatter 검사 ---
    for p in pages.values():
        loc = p['rel']
        meta = p['meta']
        if meta is None:
            errors.append(f'{loc}: YAML frontmatter 없음')
            continue
        for field in REQUIRED_FIELDS:
            if field not in meta:
                errors.append(f'{loc}: frontmatter 필드 누락 — {field}')
        ptype = meta.get('type')
        if ptype and ptype not in VALID_TYPES:
            errors.append(f'{loc}: 잘못된 type "{ptype}" (concept|moc|event|entity)')
        maturity = meta.get('maturity')
        if ptype in MATURITY_REQUIRED and not maturity:
            errors.append(f'{loc}: type={ptype}인데 maturity 누락')
        if maturity and maturity not in VALID_MATURITY:
            errors.append(f'{loc}: 잘못된 maturity "{maturity}" (seed|growing|solid)')
        if ptype in MATURITY_OMITTED and maturity:
            warnings.append(f'{loc}: type={ptype}에 불필요한 maturity (생략 권장)')
        tags = meta.get('tags') or []
        expected_tag = DOMAIN_TAG_ALIAS.get(p['domain'], p['domain'])
        if tags and tags[0] != expected_tag:
            errors.append(f'{loc}: 첫 태그가 도메인명이 아님 — "{tags[0]}" (기대값: {expected_tag})')
        if not KEBAB_RE.match(p['slug']):
            errors.append(f'{loc}: 파일명이 kebab-case가 아님')
        upd = parse_updated(meta.get('updated'))
        if meta.get('updated') and upd is None:
            errors.append(f'{loc}: updated 날짜 형식 오류 (YYYY-MM-DD)')
        elif upd and (date.today() - upd).days > STALE_DAYS:
            infos.append(f'{loc}: 오래된 페이지 — updated {upd} ({(date.today() - upd).days}일 경과)')

    # --- 깨진 링크 ---
    for p in pages.values():
        for target in p['links']:
            if target not in slugs:
                errors.append(f"{p['rel']}: 깨진 링크 [[{target}]]")

    # --- index.md 등재 여부 ---
    if index_text:
        for slug in sorted(slugs):
            if f'[[{slug}]]' not in index_text:
                errors.append(f'index.md에 [[{slug}]] 누락')

    # --- 고아 페이지 (다른 어떤 페이지도 링크하지 않음; MOC는 허브이므로 제외) ---
    linked = {t for p in pages.values() for t in p['links']}
    for p in pages.values():
        is_moc = (p['meta'] or {}).get('type') == 'moc'
        if not is_moc and p['slug'] not in linked:
            warnings.append(f"{p['rel']}: 고아 페이지 — 어떤 위키 페이지도 링크하지 않음")

    # --- MOC 검사 ---
    for domain in domains:
        domain_pages = [p for p in pages.values() if p['domain'] == domain]
        mocs = [p for p in domain_pages if (p['meta'] or {}).get('type') == 'moc']
        if not mocs:
            errors.append(f'도메인 {domain}: MOC 페이지 없음')
            continue
        moc_text = ''.join(m['body'] or '' for m in mocs)
        for p in domain_pages:
            if (p['meta'] or {}).get('type') == 'moc':
                continue
            if f"[[{p['slug']}]]" not in moc_text and f"[[{p['slug']}|" not in moc_text:
                errors.append(f"{p['rel']}: 도메인 MOC({mocs[0]['slug']})에 등재되지 않음")
        if len(domain_pages) == len(mocs):
            infos.append(f'도메인 {domain}: MOC 외 페이지 없음 (빈 지식 영역)')

    # --- maturity 분포 ---
    dist = {}
    for p in pages.values():
        m = (p['meta'] or {}).get('maturity')
        if m in VALID_MATURITY:
            dist.setdefault(p['domain'], {}).setdefault(m, 0)
            dist[p['domain']][m] += 1
    for domain in sorted(dist):
        parts = ', '.join(f'{k}={v}' for k, v in sorted(dist[domain].items()))
        infos.append(f'maturity 분포 — {domain}: {parts}')

    return errors, warnings, infos


def main():
    parser = argparse.ArgumentParser(description='LLM Wiki 구조 점검')
    parser.add_argument('--root', default='.', help='위키 루트 (wiki/와 index.md가 있는 곳)')
    parser.add_argument('--json', action='store_true', help='JSON으로 출력')
    args = parser.parse_args()

    errors, warnings, infos = lint(os.path.abspath(args.root))

    if args.json:
        print(json.dumps({'errors': errors, 'warnings': warnings, 'infos': infos,
                          'ok': not errors}, ensure_ascii=False, indent=2))
    else:
        for e in errors:
            print(f'[ERROR] {e}')
        for w in warnings:
            print(f'[WARN]  {w}')
        for i in infos:
            print(f'[INFO]  {i}')
        print(f'\n결과: ERROR {len(errors)} / WARN {len(warnings)} / INFO {len(infos)}')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
