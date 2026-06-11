# LLM Wiki 구조 재설계 — 설계 문서

- 날짜: 2026-06-11
- 상태: 사용자 승인 완료
- 대상: D:\side-projects\llm-wiki

## 배경과 목적

사용자는 Java/Spring 개발자이자 정치외교학 전공자로, 다음 세 가지 용도를 동등한 비중으로 포괄하는 개인 지식 위키가 필요하다:

1. **학습 지식 정리** — Java/Spring, CS, 국제정치 이론 등 공부한 내용의 체계적 정리
2. **뉴스/아티클 수집** — Web Clipper 기반 inbox 처리 (기존 워크플로우)
3. **지식 맵** — 무엇을 알고 무엇을 모르는지 추적

Karpathy의 LLM Wiki 패턴(RAG 대신 점진적으로 축적·합성되는 마크다운 위키)을 유지하면서, 사용자 프로필에 맞게 도메인 분류·스키마·지식 맵 장치를 재설계한다.

## 결정 사항 요약

| 항목 | 결정 |
|---|---|
| 분류 깊이 | 얕은 톱레벨 6개 도메인 + 태그/MOC (하위 폴더 없음) |
| 지식 맵 | 도메인별 MOC 허브 + 페이지별 maturity 필드 |
| 페이지 유형 | 4종: concept / moc / event / entity |

## 1. 디렉터리 구조

```
llm-wiki/
├── wiki/
│   ├── dev/          # Java, Spring, 도구, 패턴, 라이브러리
│   ├── cs/           # 자료구조, OS, 컴파일러, 분산시스템, SW공학
│   ├── ai/           # LLM, 에이전트, 연구 동향
│   ├── geopolitics/  # 국제정치, 외교, 지역 분석
│   ├── military/     # 군사전략, 무기체계, 분쟁
│   └── _concepts/    # 도메인 횡단 인물·기업·개념
├── sources/inbox/        # 유지
├── sources/processed/    # 유지
├── index.md              # 유지 — 전체 한 줄 요약 색인
├── log.md                # 유지 — 추가 전용 작업 이력
└── SCHEMA.md             # 내용 갱신
```

- 기존 `programming/`, `politics/` 폴더는 마이그레이션 후 제거한다.
- 세부 분류는 하위 폴더를 만들지 않고 태그와 MOC로 처리한다.

## 2. 프론트매터 스키마

```yaml
---
title: "스프링 트랜잭션 전파"
type: concept          # concept | moc | event | entity
tags: [dev, spring, transaction]
maturity: growing      # seed | growing | solid
updated: 2026-06-11
sources:
  - https://...
---
```

### type 정의

| type | 의미 | 예 |
|---|---|---|
| `concept` | 지식 본문 (개념, 이론, 기법) | spring-transaction-propagation |
| `moc` | 도메인 허브 (Map of Content) | dev-moc |
| `event` | 날짜가 있는 시사·사건 | trump-hormuz-blockade-2026 |
| `entity` | 인물·기업·기관·무기체계 | sam-altman, f-35 |

### maturity 정의

| 값 | 의미 |
|---|---|
| `seed` | 스크랩만 한 수준, 아직 소화 못 함 |
| `growing` | 이해하고 정리함 |
| `solid` | 남에게 설명 가능, 실무 적용 가능 |

- `moc`, `event` 타입은 maturity 생략 가능 (사건 기록에는 숙련도 개념이 무의미)
- 첫 번째 태그는 반드시 도메인명 (dev/cs/ai/geopolitics/military)

## 3. MOC 허브 시스템

각 도메인 루트에 허브 페이지 6개를 둔다: `dev-moc.md`, `cs-moc.md`, `ai-moc.md`, `geopolitics-moc.md`, `military-moc.md`, `concepts-moc.md`

MOC 형식:

```markdown
## Spring
- [[spring-transaction-propagation]] 🟢solid
- [[spring-bean-lifecycle]] 🟡growing
- [[spring-webflux]] 🌱seed
- 스프링 시큐리티 — *아직 페이지 없음 (알아야 할 영역)*
```

- 하위 주제를 트리(헤딩 + 리스트)로 정리하고 각 링크 옆에 숙련도 이모지+텍스트 표시: 🌱seed / 🟡growing / 🟢solid
- **페이지가 없는 주제도 기록한다** — "모르는 것의 지도"로서 학습 우선순위를 드러냄
- `index.md`는 전체 한 줄 요약 색인(검색용), MOC는 도메인 내부의 구조적 지도(브라우징·지식 맵용)로 역할 분담

## 4. 기존 페이지 마이그레이션

| 현재 | 이동 후 | type | 비고 |
|---|---|---|---|
| programming/python-3-13.md | dev/ | concept | |
| programming/compiler-writing-intro.md | cs/ | concept | |
| programming/artemis-ii-fault-tolerant-computer.md | cs/ | concept | |
| ai/java-vs-python-agent-frameworks.md | ai/ (유지) | concept | |
| politics/trump-hormuz-blockade-2026.md | geopolitics/ | event | maturity 생략 |

- 모든 페이지에 type 필드 추가, concept에는 maturity 추가 (초기값은 내용 보고 판단)
- 본문 [[WikiLinks]]는 파일명 기준이므로 폴더 이동에 영향 없음
- `index.md` 섹션 헤더를 새 도메인명으로 갱신
- 마이그레이션 후 `log.md`에 기록

## 5. 운영 문서 갱신

### SCHEMA.md
- 도메인 표를 6개 도메인으로 교체
- type / maturity 필드 정의 추가
- MOC 작성 규칙 추가
- 첫 태그 = 도메인명 규칙 추가

### CLAUDE.md
- 위키 구조 설명을 새 6개 도메인으로 갱신
- "inbox 처리해줘" 워크플로우에 **MOC 갱신 단계** 추가 (페이지 추가/갱신 시 해당 도메인 MOC에도 반영)
- **"공부한 내용 정리해줘" 워크플로우 신설**: 대화에서 배운/논의한 내용 → concept 페이지 생성 + maturity 지정 + MOC 등록 + index.md 갱신
- "위키 점검해줘"에 추가 항목: maturity 분포 통계, MOC와 실제 파일의 불일치(MOC에 없는 페이지 / MOC에만 있고 파일 없는 링크) 검사

### Flask 웹 인터페이스
- 서버가 `wiki/` 하위 폴더를 동적으로 읽으면 수정 불필요
- 폴더명이 하드코딩돼 있으면 새 도메인 목록으로 수정 (구현 단계에서 코드 확인 후 결정)

## 범위 제외 (YAGNI)

- 하위 폴더 세분화 (태그/MOC로 충분)
- source-digest 등 추가 페이지 타입
- 자동화된 maturity 갱신 (수동 판단)
- RAG/임베딩 검색 (Karpathy 패턴 원칙 유지)

## 성공 기준

1. 6개 도메인 폴더 + 6개 MOC 페이지 존재
2. 기존 5개 페이지가 새 위치에서 새 스키마(type, maturity)를 갖춤
3. index.md / SCHEMA.md / CLAUDE.md가 새 구조와 일치
4. "위키 점검해줘" 실행 시 깨진 링크·고아 페이지 0건
5. Flask 웹 인터페이스가 새 구조에서 정상 동작
