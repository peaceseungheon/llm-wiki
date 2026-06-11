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
