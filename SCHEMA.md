# 위키 스키마

## 도메인 분류

| 폴더 | 다루는 내용 |
|------|------------|
| `wiki/programming/` | 언어, 프레임워크, 도구, 패턴, 라이브러리 |
| `wiki/ai/` | 모델, 연구, AI 회사, 기술, 벤치마크 |
| `wiki/politics/` | 정책, 정치인, 이슈, 국가별 동향 |
| `wiki/_concepts/` | 여러 도메인에 걸치는 인물·기업·개념 |

## 프론트매터 형식

모든 위키 페이지는 반드시 아래 YAML 프론트매터로 시작해야 한다:

```yaml
---
title: "페이지 제목"
tags: [도메인, 세부태그1, 세부태그2]
updated: YYYY-MM-DD
sources:
  - https://원본-url-1
  - https://원본-url-2
---
```

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
