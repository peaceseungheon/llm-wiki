# LLM Wiki 구조 재설계 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 위키를 6개 도메인(dev/cs/ai/geopolitics/military/_concepts)으로 재편하고 type/maturity 스키마와 MOC 허브 시스템을 도입한다.

**Architecture:** 마크다운 파일 기반 위키(Karpathy LLM Wiki 패턴) + Flask 웹 인터페이스. 폴더 재구성은 git mv, 스키마 변경은 프론트매터 편집, 웹 서버는 `get_sidebar_data()`의 하드코딩 제거(동적 폴더 탐색)만 수정.

**Tech Stack:** Markdown/YAML frontmatter, Python 3 + Flask + python-frontmatter, pytest

**Spec:** `docs/superpowers/specs/2026-06-11-llm-wiki-redesign-design.md`

**주의사항:**
- 작업 트리에 `log.md`, `wiki/programming/python-3-13.md`의 미커밋 변경이 이미 존재한다. 각 태스크 커밋 시 해당 태스크 파일만 `git add` 한다.
- 모든 명령은 프로젝트 루트 `D:\side-projects\llm-wiki`에서 실행 (Windows PowerShell).

---

### Task 1: get_sidebar_data() 동적 도메인 탐색 (TDD)

`web/wiki.py:76`의 하드코딩된 `domains = ['programming', 'ai', 'politics', '_concepts']`를 제거하고 `wiki/` 하위 폴더를 동적으로 탐색하게 한다. 언더스코어로 시작하는 도메인(`_concepts`)은 정렬 시 마지막에 온다.

**Files:**
- Modify: `web/wiki.py:74-95` (get_sidebar_data 함수)
- Test: `web/tests/test_wiki.py` (테스트 2개 추가)

- [ ] **Step 1: 실패하는 테스트 작성**

`web/tests/test_wiki.py` 끝에 추가:

```python
def test_get_sidebar_data_discovers_new_domain(wiki_dir, monkeypatch):
    """Domains are discovered from the filesystem, not hardcoded."""
    dev = wiki_dir / 'wiki' / 'dev'
    dev.mkdir()
    (dev / 'spring-core.md').write_text(
        '---\ntitle: "Spring Core"\ntags: [dev]\nupdated: 2026-06-11\nsources: []\n---\n\nIoC.',
        encoding='utf-8',
    )
    monkeypatch.setattr(wiki, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    sidebar = wiki.get_sidebar_data()
    assert 'dev' in sidebar
    assert [p['slug'] for p in sidebar['dev']] == ['spring-core']


def test_get_sidebar_data_underscore_domains_sort_last(wiki_dir, monkeypatch):
    """_concepts must appear after regular domains."""
    concepts = wiki_dir / 'wiki' / '_concepts'
    concepts.mkdir()
    monkeypatch.setattr(wiki, 'WIKI_DIR', str(wiki_dir / 'wiki'))
    sidebar = wiki.get_sidebar_data()
    keys = list(sidebar.keys())
    assert keys[-1] == '_concepts'
    assert keys == sorted(keys, key=lambda d: (d.startswith('_'), d))
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python -m pytest web/tests/test_wiki.py -v`
Expected: `test_get_sidebar_data_discovers_new_domain` FAIL — 하드코딩 목록에 `dev`가 없어 `KeyError: 'dev'` 또는 assert 실패. 기존 테스트는 모두 PASS.

- [ ] **Step 3: get_sidebar_data 구현 교체**

`web/wiki.py`의 `get_sidebar_data` 전체를 다음으로 교체:

```python
def get_sidebar_data() -> dict[str, list[dict]]:
    """Return {domain: [{'slug': slug, 'title': title}]} for all wiki domains.

    Domains are discovered from wiki/ subdirectories; underscore-prefixed
    domains (e.g. _concepts) sort last."""
    if not os.path.isdir(WIKI_DIR):
        return {}
    domains = sorted(
        (d for d in os.listdir(WIKI_DIR)
         if os.path.isdir(os.path.join(WIKI_DIR, d))),
        key=lambda d: (d.startswith('_'), d),
    )
    result: dict[str, list[dict]] = {}
    for domain in domains:
        pages = []
        for f in sorted(glob.glob(os.path.join(WIKI_DIR, domain, '*.md'))):
            slug = os.path.basename(f).replace('.md', '')
            if slug == '.gitkeep':
                continue
            try:
                post = frontmatter.load(f)
                title = post.get('title', slug)
            except Exception:
                title = slug
            pages.append({'slug': slug, 'title': title})
        result[domain] = pages
    return result
```

참고: dict는 삽입 순서를 유지하므로 정렬된 도메인 순서가 사이드바 표시 순서가 된다. 기존 `test_get_sidebar_data_empty_domain`은 fixture가 빈 `ai/` 폴더를 만들기 때문에 그대로 통과한다.

- [ ] **Step 4: 전체 테스트 통과 확인**

Run: `python -m pytest web/tests -v`
Expected: 전부 PASS

- [ ] **Step 5: 커밋**

```powershell
git add web/wiki.py web/tests/test_wiki.py
git commit -m "refactor: sidebar 도메인 목록을 하드코딩에서 동적 폴더 탐색으로 변경"
```

---

### Task 2: 도메인 폴더 재구성 + 페이지 마이그레이션

기존 `programming/`, `politics/` 폴더를 해체하고 6개 도메인 구조로 페이지를 이동, 모든 페이지 프론트매터에 type(+concept에는 maturity) 추가.

**Files:**
- Move: `wiki/programming/python-3-13.md` → `wiki/dev/python-3-13.md`
- Move: `wiki/programming/compiler-writing-intro.md` → `wiki/cs/compiler-writing-intro.md`
- Move: `wiki/programming/artemis-ii-fault-tolerant-computer.md` → `wiki/cs/artemis-ii-fault-tolerant-computer.md`
- Move: `wiki/politics/trump-hormuz-blockade-2026.md` → `wiki/geopolitics/trump-hormuz-blockade-2026.md`
- Modify: 위 4개 + `wiki/ai/java-vs-python-agent-frameworks.md` 프론트매터
- Create: `wiki/dev/.gitkeep`, `wiki/cs/.gitkeep`, `wiki/geopolitics/.gitkeep`, `wiki/military/.gitkeep`
- Delete: `wiki/programming/`, `wiki/politics/` (잔여 .gitkeep 포함)

- [ ] **Step 1: 새 폴더 생성 및 git mv**

```powershell
New-Item -ItemType Directory -Force wiki/dev, wiki/cs, wiki/geopolitics, wiki/military
git mv wiki/programming/python-3-13.md wiki/dev/python-3-13.md
git mv wiki/programming/compiler-writing-intro.md wiki/cs/compiler-writing-intro.md
git mv wiki/programming/artemis-ii-fault-tolerant-computer.md wiki/cs/artemis-ii-fault-tolerant-computer.md
git mv wiki/politics/trump-hormuz-blockade-2026.md wiki/geopolitics/trump-hormuz-blockade-2026.md
git mv wiki/programming/.gitkeep wiki/cs/.gitkeep
git mv wiki/politics/.gitkeep wiki/geopolitics/.gitkeep
New-Item -ItemType File wiki/dev/.gitkeep, wiki/military/.gitkeep
git add wiki/dev/.gitkeep wiki/military/.gitkeep
Remove-Item wiki/programming, wiki/politics -Force
```

참고: `python-3-13.md`는 미커밋 수정이 있는 상태지만 git mv는 정상 동작한다. 마지막 Remove-Item은 빈 디렉터리 잔재 제거(git은 빈 폴더를 추적하지 않음).

- [ ] **Step 2: 프론트매터 갱신 (5개 파일)**

각 파일의 기존 프론트매터 블록을 아래로 교체한다. **본문은 건드리지 않는다.** maturity 초기값은 전부 `growing`(이미 읽고 요약·정리를 거친 페이지들이므로).

`wiki/dev/python-3-13.md`:
```yaml
---
title: "Python 3.13 새 기능"
type: concept
tags: [dev, python, release-notes]
maturity: growing
updated: 2026-04-13
sources:
  - https://docs.python.org/3.13/whatsnew/3.13.html
---
```

`wiki/cs/compiler-writing-intro.md`:
```yaml
---
title: "컴파일러 작성 입문"
type: concept
tags: [cs, compiler, education]
maturity: growing
updated: 2026-04-16
sources:
  - https://prog21.dadgum.com/30.html
---
```

`wiki/cs/artemis-ii-fault-tolerant-computer.md`:
```yaml
---
title: "Artemis II 내결함성 컴퓨터"
type: concept
tags: [cs, fault-tolerance, aerospace, embedded-systems, real-time-os, redundancy]
maturity: growing
updated: 2026-04-13
sources:
  - https://cacm.acm.org/news/how-nasa-built-artemis-iis-fault-tolerant-computer/
---
```

`wiki/ai/java-vs-python-agent-frameworks.md`:
```yaml
---
title: "자바 vs 파이썬 에이전트 프레임워크 비교"
type: concept
tags: [ai, agent, java, python, langgraph, embabel]
maturity: growing
updated: 2026-04-16
sources:
  - https://yozm.wishket.com/magazine/detail/3708/
  - https://medium.com/@springrod/build-better-agents-in-java-vs-python-embabel-vs-langgraph-f7951a0d855c
---
```

`wiki/geopolitics/trump-hormuz-blockade-2026.md` (event — maturity 없음):
```yaml
---
title: "트럼프 호르무즈 해협 봉쇄 선언 (2026)"
type: event
tags: [geopolitics, usa, iran, trump, middle-east]
updated: 2026-04-13
sources:
  - https://n.news.naver.com/mnews/article/018/0006255836
---
```

- [ ] **Step 3: 테스트로 회귀 없음 확인**

Run: `python -m pytest web/tests -v`
Expected: 전부 PASS (테스트는 임시 fixture를 쓰므로 실제 위키 변경에 영향받지 않음 — 회귀 확인용)

- [ ] **Step 4: 커밋**

```powershell
git add wiki/
git commit -m "refactor: 위키를 6개 도메인 구조로 재편, type/maturity 프론트매터 도입"
```

---

### Task 3: MOC 허브 페이지 6개 생성

각 도메인에 Map of Content 페이지를 만든다. 형식: 헤딩으로 주제 그룹, 리스트로 페이지 링크 + 숙련도(🌱seed / 🟡growing / 🟢solid), **페이지가 없는 주제는 [[링크]] 없이 일반 텍스트 + "*아직 페이지 없음*"** (깨진 링크를 만들지 않기 위함).

**Files:**
- Create: `wiki/dev/dev-moc.md`
- Create: `wiki/cs/cs-moc.md`
- Create: `wiki/ai/ai-moc.md`
- Create: `wiki/geopolitics/geopolitics-moc.md`
- Create: `wiki/military/military-moc.md`
- Create: `wiki/_concepts/concepts-moc.md`

- [ ] **Step 1: dev-moc.md 작성**

```markdown
---
title: "Dev MOC — 개발"
type: moc
tags: [dev, moc]
updated: 2026-06-11
sources: []
---

# Dev MOC — 개발

Java/Spring 중심 개발 지식의 지도. 숙련도: 🌱seed → 🟡growing → 🟢solid

## Java

- 자바 언어 코어 (제네릭, 컬렉션, 동시성) — *아직 페이지 없음*
- JVM 내부 (GC, JIT, 클래스로딩) — *아직 페이지 없음*

## Spring

- 스프링 코어 (IoC, DI, 빈 라이프사이클) — *아직 페이지 없음*
- 스프링 트랜잭션 — *아직 페이지 없음*
- 스프링 시큐리티 — *아직 페이지 없음*
- 스프링 부트 내부 동작 — *아직 페이지 없음*

## 기타 언어·도구

- [[python-3-13]] 🟡growing
```

- [ ] **Step 2: cs-moc.md 작성**

```markdown
---
title: "CS MOC — 컴퓨터 과학"
type: moc
tags: [cs, moc]
updated: 2026-06-11
sources: []
---

# CS MOC — 컴퓨터 과학

CS 이론과 소프트웨어 공학 지식의 지도. 숙련도: 🌱seed → 🟡growing → 🟢solid

## 컴파일러·언어 구현

- [[compiler-writing-intro]] 🟡growing

## 시스템·아키텍처

- [[artemis-ii-fault-tolerant-computer]] 🟡growing
- 운영체제 (프로세스, 메모리, 스케줄링) — *아직 페이지 없음*
- 분산 시스템 (합의, 복제, 파티셔닝) — *아직 페이지 없음*

## 기초 이론

- 자료구조·알고리즘 — *아직 페이지 없음*
- 네트워크 (TCP/IP, HTTP) — *아직 페이지 없음*

## 소프트웨어 공학

- 설계 패턴·아키텍처 패턴 — *아직 페이지 없음*
- 테스트 전략 — *아직 페이지 없음*
```

- [ ] **Step 3: ai-moc.md 작성**

```markdown
---
title: "AI MOC — 인공지능"
type: moc
tags: [ai, moc]
updated: 2026-06-11
sources: []
---

# AI MOC — 인공지능

LLM·에이전트·연구 동향 지식의 지도. 숙련도: 🌱seed → 🟡growing → 🟢solid

## 에이전트

- [[java-vs-python-agent-frameworks]] 🟡growing
- 에이전트 설계 패턴 (ReAct, 플래닝, 멀티에이전트) — *아직 페이지 없음*

## LLM 기초

- 트랜스포머 아키텍처 — *아직 페이지 없음*
- 프롬프트 엔지니어링 — *아직 페이지 없음*
- RAG vs 위키 패턴 — *아직 페이지 없음*
```

- [ ] **Step 4: geopolitics-moc.md 작성**

```markdown
---
title: "Geopolitics MOC — 국제정치"
type: moc
tags: [geopolitics, moc]
updated: 2026-06-11
sources: []
---

# Geopolitics MOC — 국제정치

국제정치·외교 지식의 지도. 숙련도: 🌱seed → 🟡growing → 🟢solid

## 국제정치 이론

- 현실주의·자유주의·구성주의 — *아직 페이지 없음*
- 세력균형과 동맹 이론 — *아직 페이지 없음*

## 중동

- [[trump-hormuz-blockade-2026]] (event)

## 동아시아

- 한반도 안보 구조 — *아직 페이지 없음*
- 미중 전략 경쟁 — *아직 페이지 없음*
```

- [ ] **Step 5: military-moc.md 작성**

```markdown
---
title: "Military MOC — 군사"
type: moc
tags: [military, moc]
updated: 2026-06-11
sources: []
---

# Military MOC — 군사

군사전략·무기체계·분쟁 지식의 지도. 숙련도: 🌱seed → 🟡growing → 🟢solid

## 군사전략

- 핵전략과 억제 이론 — *아직 페이지 없음*
- 해양 전략 — *아직 페이지 없음*

## 무기체계

- 주요 무기체계 (entity 페이지로 축적) — *아직 페이지 없음*

## 분쟁·전쟁

- 진행 중 분쟁 추적 (event 페이지로 축적) — *아직 페이지 없음*
```

- [ ] **Step 6: concepts-moc.md 작성**

```markdown
---
title: "Concepts MOC — 횡단 개념"
type: moc
tags: [concepts, moc]
updated: 2026-06-11
sources: []
---

# Concepts MOC — 횡단 개념

여러 도메인에 걸치는 인물·기업·기관·개념의 지도.

## 인물

- *아직 페이지 없음*

## 기업·기관

- *아직 페이지 없음*
```

- [ ] **Step 7: 웹 렌더링 확인 후 커밋**

Run: `python -m pytest web/tests -v` → 전부 PASS

```powershell
git add wiki/
git commit -m "feat: 도메인별 MOC 허브 페이지 6개 추가"
```

---

### Task 4: index.md 갱신

**Files:**
- Modify: `index.md` (전체 교체)

- [ ] **Step 1: index.md 전체를 아래로 교체**

```markdown
# Wiki Index

모든 위키 페이지의 한 줄 요약. Claude가 관련 페이지를 찾는 색인으로 사용.
도메인별 구조적 지도는 각 MOC 페이지 참조.

## dev
- [[dev-moc]] — 개발 도메인 지도 (Java, Spring, 도구)
- [[python-3-13]] — Python 3.13 주요 변경사항: JIT 컴파일러(실험적), GIL 비활성화(PEP 703), 오류 메시지 개선, REPL 개선

## cs
- [[cs-moc]] — 컴퓨터 과학 도메인 지도 (이론, 시스템, SW공학)
- [[artemis-ii-fault-tolerant-computer]] — Artemis II 오리온 캡슐의 8중 CPU 내결함성 컴퓨팅 아키텍처 (fail-silent, ARINC653, BFS)
- [[compiler-writing-intro]] — 컴파일러 작성 입문: Crenshaw 시리즈와 Nanopass 논문으로 시작하는 실용적 접근법

## ai
- [[ai-moc]] — AI 도메인 지도 (LLM, 에이전트, 연구)
- [[java-vs-python-agent-frameworks]] — Java(Embabel) vs Python(LangGraph) 에이전트 프레임워크 6가지 패턴 비교. Rod Johnson 관점

## geopolitics
- [[geopolitics-moc]] — 국제정치 도메인 지도 (이론, 지역 분석)
- [[trump-hormuz-blockade-2026]] — 2026년 4월 트럼프의 호르무즈 해협 전면 봉쇄 선언, 미-이란 핵 협상 결렬 이후

## military
- [[military-moc]] — 군사 도메인 지도 (전략, 무기체계, 분쟁)

## _concepts
- [[concepts-moc]] — 횡단 개념 지도 (인물, 기업, 기관)
```

- [ ] **Step 2: 커밋**

```powershell
git add index.md
git commit -m "docs: index.md를 6개 도메인 구조로 갱신"
```

---

### Task 5: SCHEMA.md 갱신

**Files:**
- Modify: `SCHEMA.md` (전체 교체)

- [ ] **Step 1: SCHEMA.md 전체를 아래로 교체**

````markdown
# 위키 스키마

## 도메인 분류

| 폴더 | 다루는 내용 |
|------|------------|
| `wiki/dev/` | Java, Spring, 언어, 프레임워크, 도구, 패턴, 라이브러리 |
| `wiki/cs/` | 자료구조, 알고리즘, OS, 컴파일러, 분산시스템, SW공학 |
| `wiki/ai/` | LLM, 에이전트, 모델, 연구, AI 회사, 벤치마크 |
| `wiki/geopolitics/` | 국제정치, 외교, 정책, 지역 분석, 국가별 동향 |
| `wiki/military/` | 군사전략, 무기체계, 분쟁, 안보 |
| `wiki/_concepts/` | 여러 도메인에 걸치는 인물·기업·기관·개념 |

세부 분류는 하위 폴더를 만들지 않고 **태그와 MOC**로 처리한다.

## 프론트매터 형식

모든 위키 페이지는 반드시 아래 YAML 프론트매터로 시작해야 한다:

```yaml
---
title: "페이지 제목"
type: concept            # concept | moc | event | entity
tags: [도메인, 세부태그1, 세부태그2]
maturity: growing        # seed | growing | solid (concept/entity만, moc/event는 생략)
updated: YYYY-MM-DD
sources:
  - https://원본-url-1
---
```

### type 정의

| type | 의미 | 예 |
|------|------|-----|
| `concept` | 지식 본문 (개념, 이론, 기법) | spring-transaction-propagation |
| `moc` | 도메인 허브 (Map of Content) | dev-moc |
| `event` | 날짜가 있는 시사·사건 | trump-hormuz-blockade-2026 |
| `entity` | 인물·기업·기관·무기체계 | sam-altman, f-35 |

### maturity 정의

| 값 | 의미 |
|----|------|
| `seed` | 스크랩만 한 수준, 아직 소화 못 함 |
| `growing` | 이해하고 정리함 |
| `solid` | 남에게 설명 가능, 실무 적용 가능 |

- `moc`, `event` 타입은 maturity를 생략한다 (숙련도 개념이 무의미)
- **첫 번째 태그는 반드시 도메인명** (dev/cs/ai/geopolitics/military). `_concepts`는 `concepts` 사용

## MOC 작성 규칙

각 도메인 루트에 `{도메인}-moc.md` 허브 페이지를 하나씩 둔다.

- 하위 주제를 헤딩 + 리스트 트리로 정리
- 페이지 링크 옆에 숙련도 표시: `[[페이지명]] 🌱seed` / `🟡growing` / `🟢solid`
- event 페이지는 숙련도 대신 `(event)` 표시
- **페이지가 없는 주제도 기록한다** — `주제명 — *아직 페이지 없음*` 형식 (일반 텍스트, [[링크]] 금지 — 깨진 링크 방지)
- 페이지를 추가·갱신하면 해당 도메인 MOC도 함께 갱신한다

## 네이밍 규칙

- 파일명: 소문자 kebab-case
- 고유명사도 소문자 (예: `openai-gpt4.md`, `sam-altman.md`)
- 날짜가 중요한 경우: `YYYY-MM-DD-제목.md`
- 공백 대신 하이픈 사용

### 올바른 예
- `llm-reasoning-costs.md`
- `rust-async-patterns.md`
- `korea-ai-policy.md`

### 잘못된 예
- `LLM Reasoning Costs.md` (대문자, 공백)
- `gpt4Analysis.md` (camelCase)

## 교차 참조

- 같은 위키 내 페이지 링크: `[[페이지명]]`
- 섹션 링크: `[[페이지명#섹션]]`
- 외부 링크: `[링크텍스트](https://url)`

## 페이지 작성 원칙

1. **하나의 페이지 = 하나의 주제** — 여러 주제가 섞이면 분리
2. **사실만 기록** — 의견은 `> 인용 블록`으로 구분
3. **[[WikiLinks]] 적극 활용** — 관련 페이지를 연결해 그래프 구성
4. **출처 명시** — 프론트매터 sources에 원본 URL 항상 포함
5. **업데이트 날짜 갱신** — 내용 변경 시 updated 필드 갱신
6. **MOC 동기화** — 페이지 생성·갱신 시 도메인 MOC에 반영
````

- [ ] **Step 2: 커밋**

```powershell
git add SCHEMA.md
git commit -m "docs: SCHEMA.md에 6개 도메인, type/maturity, MOC 규칙 반영"
```

---

### Task 6: CLAUDE.md 갱신

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: 위키 구조 섹션 갱신**

`## 위키 구조`의 위키 페이지 항목을 다음으로 교체:

```markdown
- **위키 페이지**: `wiki/dev/`, `wiki/cs/`, `wiki/ai/`, `wiki/geopolitics/`, `wiki/military/`, `wiki/_concepts/`
- **MOC 허브**: 각 도메인 루트의 `{도메인}-moc.md` — 도메인 지식 지도 (숙련도 표시 포함)
```

(나머지 항목 — 미처리 소스, 색인, 로그, 규칙 — 은 유지)

- [ ] **Step 2: inbox 처리 워크플로우에 MOC 갱신 단계 추가**

`## "inbox 처리해줘" 명령 시`의 4번 항목을 다음으로 교체:

```markdown
4. 모든 inbox 파일 처리 완료 후:
   - 처리된 파일을 `sources/processed/`로 이동
   - `index.md` 업데이트 (새 페이지 추가 또는 기존 항목 갱신)
   - **해당 도메인 MOC 업데이트** (새 페이지 링크 + 숙련도 추가, 신규 페이지 기본 maturity는 `seed`)
   - `log.md`에 항목 추가: `## [YYYY-MM-DD] ingest | {변경 요약}`
```

- [ ] **Step 3: "공부한 내용 정리해줘" 워크플로우 신설**

`## "inbox 처리해줘" 명령 시` 섹션 다음에 새 섹션 추가:

```markdown
## "공부한 내용 정리해줘" / "이 내용 위키에 저장해줘" 명령 시

대화에서 배우거나 논의한 내용을 위키 페이지로 변환한다:

1. 대화 내용에서 주제 단위로 지식 추출 (하나의 페이지 = 하나의 주제)
2. `index.md` 확인 → 기존 페이지가 있으면 업데이트, 없으면 새 페이지 제안
3. SCHEMA.md 규칙에 따라 페이지 작성 (type은 보통 `concept`, maturity는 사용자에게 확인)
4. 변경 내용 설명 후 **사용자 승인 대기**
5. 승인 시: 페이지 쓰기 + `index.md` 갱신 + 해당 도메인 MOC 갱신 + `log.md`에 `## [YYYY-MM-DD] learn | {요약}` 추가
```

- [ ] **Step 4: "위키 점검해줘" 항목 추가**

`## "위키 점검해줘" 명령 시` 리스트 끝에 추가:

```markdown
6. **maturity 분포**: 도메인별 seed/growing/solid 페이지 수 통계
7. **MOC 불일치**: MOC에 없는 위키 페이지 / MOC가 [[링크]]했지만 존재하지 않는 페이지
```

- [ ] **Step 5: 페이지 작성 규칙에 type/maturity 추가**

`## 위키 페이지 작성 규칙`의 "반드시 YAML 프론트매터 포함" 항목을 다음으로 교체:

```markdown
- 반드시 YAML 프론트매터 포함: title, type, tags, maturity(concept/entity만), updated, sources
- 첫 번째 태그는 도메인명 (dev/cs/ai/geopolitics/military/concepts)
```

- [ ] **Step 6: 커밋**

```powershell
git add CLAUDE.md
git commit -m "docs: CLAUDE.md에 새 도메인 구조, MOC 갱신 단계, 학습 정리 워크플로우 추가"
```

---

### Task 7: log.md 기록 + 최종 검증

**Files:**
- Modify: `log.md` (항목 추가)

- [ ] **Step 1: log.md에 항목 추가**

log.md 끝에 추가 (기존 미커밋 변경 내용은 건드리지 않고 그대로 둔 채 끝에 덧붙임):

```markdown
## [2026-06-11] restructure | 위키 6개 도메인 재편(dev/cs/ai/geopolitics/military/_concepts), type·maturity 스키마 도입, MOC 허브 6개 생성
```

- [ ] **Step 2: 전체 테스트 실행**

Run: `python -m pytest web/tests -v`
Expected: 전부 PASS

- [ ] **Step 3: 깨진 링크·고아 페이지 검사**

Run (프로젝트 루트):

```powershell
python -c "
import glob, os, re
files = glob.glob('wiki/**/*.md', recursive=True)
slugs = {os.path.basename(f)[:-3] for f in files}
broken = []
for f in files:
    text = open(f, encoding='utf-8').read()
    for m in re.finditer(r'\[\[([^\]\#\|]+)', text):
        t = m.group(1).strip().lower().replace(' ', '-')
        if t not in slugs:
            broken.append((f, t))
print('broken links:', broken if broken else 'NONE')
index = open('index.md', encoding='utf-8').read()
orphans = [s for s in slugs if f'[[{s}]]' not in index]
print('pages missing from index.md:', orphans if orphans else 'NONE')
"
```

Expected: `broken links: NONE`, `pages missing from index.md: NONE`

- [ ] **Step 4: 웹 서버 스모크 테스트**

```powershell
$p = Start-Process python -ArgumentList 'web/server.py' -PassThru
Start-Sleep -Seconds 3
(Invoke-WebRequest http://localhost:8000/ -UseBasicParsing).StatusCode
(Invoke-WebRequest http://localhost:8000/wiki/python-3-13 -UseBasicParsing).StatusCode
(Invoke-WebRequest http://localhost:8000/wiki/dev-moc -UseBasicParsing).StatusCode
Stop-Process $p.Id
```

Expected: 세 번 모두 `200`. 사이드바에 6개 도메인이 보이는지 `/` 응답 본문에서 `geopolitics` 문자열 포함 여부로 확인해도 좋다.

- [ ] **Step 5: 커밋**

```powershell
git add log.md
git commit -m "chore: 위키 재구성 작업 로그 기록"
```

---

## 완료 기준 (스펙의 성공 기준 대응)

1. ✅ 6개 도메인 폴더 + 6개 MOC 페이지 — Task 2, 3
2. ✅ 기존 5개 페이지가 새 위치 + 새 스키마 — Task 2
3. ✅ index.md / SCHEMA.md / CLAUDE.md 일치 — Task 4, 5, 6
4. ✅ 깨진 링크·고아 페이지 0건 — Task 7 Step 3
5. ✅ Flask 웹 인터페이스 정상 동작 — Task 1(동적 탐색), Task 7 Step 4
