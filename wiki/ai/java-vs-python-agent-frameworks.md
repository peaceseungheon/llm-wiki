---
title: "자바 vs 파이썬 에이전트 프레임워크 비교"
tags: [ai, agent, java, python, langgraph, embabel]
updated: 2026-04-16
sources:
  - https://yozm.wishket.com/magazine/detail/3708/
  - https://medium.com/@springrod/build-better-agents-in-java-vs-python-embabel-vs-langgraph-f7951a0d855c
---

## 배경

파이썬이 AI 에이전트 개발의 기본 언어로 여겨지지만, JVM 생태계도 강력한 대안이 될 수 있다는 주장이 있다. Rod Johnson(Spring Framework 창시자)이 만든 [Embabel](https://github.com/embabel/embabel-agent) 프레임워크와 파이썬 기반 [[langgraph|LangGraph]]를 6가지 에이전트 디자인 패턴으로 비교한 분석이다.

> Rod Johnson은 Embabel 창시자이므로, 이 비교는 Embabel에 유리한 관점에서 작성되었음을 감안해야 한다.

## LangGraph

- [LangChain](https://www.langchain.com/) 기반 확장 프레임워크
- **유한 상태 기계(FSM)** 로 에이전트 워크플로를 정의
- 노드 = 함수, 엣지 = 전이(자동 또는 동적 결정)
- 워크플로를 문자열 기반으로 정의하므로 컴파일 타임 유효성 검사가 거의 없음
- LangChain은 시리즈 B에서 11억 달러 평가액으로 투자 유치 (2026년 기준)

## Embabel

- Rod Johnson이 만든 **Java/Spring 기반** 에이전트 프레임워크
- **목표 지향 행동 계획(GOAP)** 기반 접근법
- 타입 시스템을 활용해 실행 경로를 자동 추론 — 개발자가 워크플로를 명시적으로 정의할 필요 없음
- `@Agent`, `@Action` 애노테이션으로 단계 정의
- Spring 생태계(DI, application.yml 외부화 등) 활용

## 6가지 에이전트 디자인 패턴 비교

### 1. 프롬프트 체이닝 (Prompt Chaining)

한 모델의 출력이 다른 모델의 입력이 되는 구조.

- **LangGraph**: State 클래스 + 노드/엣지로 흐름 정의. 모든 필드가 문자열로 모델링되어 구조 부족
- **Embabel**: Java 레코드로 도메인 객체를 정의하여 타입 안전성 확보. 프레임워크가 타입 흐름에서 실행 순서를 자동 추론

### 2. 라우팅 (Routing)

워크플로 내 조건부 분기.

- **LangGraph**: 함수 출력을 다음 상태 이름(문자열)에 매핑. 오류 발생 가능성 높음
- **Embabel**: 다형성(하위 타입)을 활용해 경로를 자동 계획. 타입 시스템이 분기를 결정

### 3. 병렬화 (Parallelization)

LLM 호출 지연을 줄이기 위한 동시 실행.

- **LangGraph**: "평행 엣지"로 병렬화
- **Embabel**: `parallelMap` 메서드 또는 `CONCURRENT` 설정으로 자동 병렬화

### 4. 리플렉션 (Reflection)

LLM 출력을 다른 LLM이 평가하고 만족할 때까지 반복하는 패턴. Anthropic은 이를 "Evaluator-optimizer"라 부른다.

- **LangGraph**: 상태 머신 루프로 구현. 종료 보장 없음
- **Embabel**: `RepeatUntilAcceptableBuilder` API 제공. `maxIterations` 초과 시 최고 점수 결과 반환

### 5. 도구 사용 (Tool Use)

- **LangGraph**: Python 함수를 도구로 정의하고 LLM에 바인딩
- **Embabel**: MCP 지원, Java 객체를 도구로 직접 사용 가능. `LlmReference`로 도구 그룹화 및 프롬프트 결합

### 6. 계획 수립 (Planning)

- **LangGraph**: 이전 단계 결과에 따라 최종 단계가 달라지는 흐름을 워크플로로 정의
- **Embabel**: 두 데이터 타입을 모두 사용하는 메서드를 정의하면 프레임워크가 자동으로 계획

## Embabel이 주장하는 장점

- **타입 안전성**: 문자열 기반 워크플로 대신 Java 타입 시스템 활용
- **도메인 모델링**: 구조화된 도메인 객체로 비즈니스 요구사항 정확히 반영
- **자동 실행 계획**: GOAP 기반으로 프레임워크가 실행 순서를 추론
- **Spring 생태계**: DI, 설정 외부화, 엔터프라이즈 인프라 활용
- **병렬화 자동 지원**: 독립적 작업을 자동으로 병렬 실행

## 핵심 논점

JVM 생태계는 타입 안전성, 도메인 모델링, 엔터프라이즈 견고성에서 파이썬 대비 구조적 이점을 가진다. 파이썬이 AI/ML 생태계에서 지배적이지만, 에이전트 개발은 데이터 과학보다 소프트웨어 엔지니어링에 가까우므로 JVM의 강점이 더 부각될 수 있다는 주장이다.
