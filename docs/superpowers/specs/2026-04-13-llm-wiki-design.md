# LLM Wiki 시스템 디자인

**날짜:** 2026-04-13  
**기반:** Karpathy의 LLM Wiki 패턴 (https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)  
**도구:** Obsidian + Claude Code (API 키 불필요)

---

## 개요

RAG(검색 증강 생성) 대신 **지식을 컴파일하는 영구 위키**를 유지한다. LLM이 매번 원본 문서를 재탐색하는 대신, 시간이 지남에 따라 진화하고 상호 연결된 마크다운 위키가 지식을 축적·합성한다.

핵심 원칙: "지식 베이스 유지의 지루한 부분은 읽거나 생각하는 것이 아니라 관리(bookkeeping)다." Claude Code가 관리 부담을 처리하고, 사람은 큐레이션과 전략적 판단을 담당한다.

---

## 아키텍처 (3계층)

| 계층 | 위치 | 역할 |
|------|------|------|
| Raw Sources | `sources/inbox/`, `sources/processed/` | 불변 원본. Claude가 읽지만 수정하지 않음 |
| Wiki | `wiki/` | Claude가 생성·유지하는 컴파일된 지식 |
| Schema | `CLAUDE.md`, `SCHEMA.md` | 운영 규칙. 사람이 큐레이션 |

---

## 폴더 구조

```
llm-wiki/
├── CLAUDE.md              # Claude Code 운영 지침서 (핵심 파일)
├── SCHEMA.md              # 위키 규칙: 네이밍, 프론트매터, 분류체계
├── index.md               # 모든 위키 페이지 한 줄 요약
├── log.md                 # 작업 로그 (날짜 | 작업 | 변경 내용)
├── sources/
│   ├── inbox/             # Obsidian Web Clipper 저장 대상
│   └── processed/         # 처리 완료된 클리핑
├── wiki/
│   ├── programming/
│   ├── ai/
│   ├── politics/
│   └── _concepts/         # 교차 항목: 인물, 기업, 개념
├── docs/
│   └── superpowers/specs/ # 설계 문서
└── .gitignore
```

Obsidian 볼트는 `llm-wiki/` **루트 전체**를 가리키도록 설정. 이렇게 해야 Web Clipper가 `sources/inbox/`에 저장 가능. 그래프 뷰, 백링크, `[[WikiLinks]]` 네이티브 동작. wiki/ 하위 폴더만 페이지로 활성화하려면 Obsidian 설정에서 `sources/`, `docs/` 폴더를 제외(excluded files)로 지정.

---

## 데이터 흐름

### Ingest (주요 작업)

1. 글 발견 → Obsidian Web Clipper로 `sources/inbox/`에 저장
2. Claude Code에서 `"inbox 처리해줘"` 명령
3. Claude Code가 inbox 파일 읽기 → `index.md`로 관련 페이지 파악
4. 편집 제안: 기존 페이지 업데이트 또는 새 페이지 생성
5. 변경사항 파일별 표시 → 사용자 승인/거절
6. 승인된 변경사항 적용 → 파일을 `processed/`로 이동
7. `index.md`, `log.md` 자동 업데이트

### Query (검색)

- `"~에 대해 알려줘"` → index.md 기반 관련 페이지 로드 → 답변 합성
- `"~관련 페이지 찾아줘"` → 관련 페이지 목록 출력
- `"~업데이트됐나?"` → 특정 주제의 최신 정보 확인
- 답변 후 위키 저장 여부 확인

### Lint (상태 점검)

- `"위키 점검해줘"` → 전체 위키 분석
- 출력: 모순된 정보, 고아 페이지, 오래된 주장, 빈 지식 영역

---

## CLAUDE.md 명세

```markdown
# LLM Wiki 운영 지침

## 위키 구조
- 위키 페이지: wiki/programming/, wiki/ai/, wiki/politics/, wiki/_concepts/
- 원본 소스: sources/inbox/ (미처리), sources/processed/ (처리완료)
- 색인: index.md | 로그: log.md

## "inbox 처리해줘" 명령 시
1. sources/inbox/의 모든 파일 읽기
2. index.md로 관련 기존 페이지 파악
3. 파일당 제안 작성:
   - 기존 페이지 업데이트 or 새 페이지 생성
   - [[WikiLinks]]로 관련 페이지 연결
4. 변경사항을 파일별로 보여주고 사용자 승인 대기
5. 승인 후: 파일을 processed/로 이동, index.md·log.md 업데이트

## "~에 대해 알려줘" / "~찾아줘" 명령 시
1. index.md에서 관련 키워드로 페이지 목록 파악
2. 해당 페이지들 읽기
3. 답변 합성 후 출력
4. "이 답변을 위키 페이지로 저장할까요? [y/n]" 확인

## "위키 점검해줘" 명령 시
전체 위키 로드 → 모순된 정보, 고아 페이지, 오래된 주장, 빈 지식 영역 찾아 리포트 출력

## 검색 명령어
- "~에 대해 알려줘"       → 위키 내용 합성 후 답변
- "~관련 페이지 찾아줘"   → 관련 페이지 목록 출력
- "~업데이트됐나?"        → 특정 주제의 최신 정보 확인
- "inbox 처리해줘"        → 새 클리핑 수집 및 위키 업데이트
- "위키 점검해줘"         → lint 실행

## 위키 페이지 규칙
- 파일명: kebab-case (예: llm-reasoning-costs.md)
- 반드시 YAML 프론트매터 포함 (title, tags, updated, sources)
- Obsidian [[WikiLinks]] 사용
- 사실만 기록, 의견은 > 인용 블록으로 별도 표시
- 각 페이지는 단일 주제에 집중
```

---

## SCHEMA.md 명세

```markdown
# 위키 스키마

## 도메인 분류
- programming/: 언어, 프레임워크, 도구, 패턴
- ai/: 모델, 연구, 회사, 기술
- politics/: 정책, 인물, 이슈, 국가별
- _concepts/: 여러 도메인에 걸치는 인물·기업·개념

## 프론트매터 형식
---
title: "페이지 제목"
tags: [도메인, 세부태그]
updated: YYYY-MM-DD
sources:
  - https://...
---

## 네이밍 규칙
- 파일명: 소문자 kebab-case
- 고유명사도 소문자 (예: openai-gpt4.md)
- 날짜 포함 시: YYYY-MM-DD-제목.md

## 교차 참조
- 같은 위키 내 페이지: [[페이지명]]
- 외부 링크: [텍스트](URL)
```

---

## index.md 형식

```markdown
# Wiki Index

## ai
- [[llm-reasoning-costs]] — LLM 추론 비용 트렌드 및 주요 벤치마크 (2026-04-13)
- [[openai-o3]] — OpenAI o3 모델 분석 및 성능 비교

## programming
- [[rust-async-patterns]] — Rust 비동기 프로그래밍 패턴 모음

## politics
- [[korea-ai-policy]] — 한국 AI 정책 동향
```

---

## log.md 형식

```markdown
## [2026-04-13] ingest | openai-o3.md 생성, index.md 업데이트
## [2026-04-13] ingest | llm-reasoning-costs.md 업데이트 (새 데이터 추가)
## [2026-04-14] lint | 고아 페이지 2개 발견: xxx.md, yyy.md
```

---

## Obsidian Web Clipper 설정

- 볼트 루트: `llm-wiki/` (전체 프로젝트 폴더)
- 저장 경로: `sources/inbox/` (볼트 내부 상대 경로)
- 파일명 형식: `YYYY-MM-DD-{title}.md`
- 프론트매터에 원본 URL 포함
- Obsidian 설정 → Files & Links → Excluded files: `sources/`, `docs/`, `scripts/` 추가

---

## 사용하지 않는 것

- Python 스크립트 없음
- Anthropic API 키 없음
- 별도 데이터베이스 없음
- 외부 서비스 없음

Claude Code 자체가 LLM이다.
