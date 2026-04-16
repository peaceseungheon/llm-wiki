---
title: "컴파일러 작성 입문"
tags: [programming, compiler, education]
updated: 2026-04-16
sources:
  - https://prog21.dadgum.com/30.html
---

## 컴파일러는 어렵다는 신화

컴파일러 교과서(Dragon Book 등)는 범위가 너무 넓다. 정규 표현식을 실행 가능한 상태 기계로 변환하는 법, 다양한 문법 유형 등을 다루지만, 이를 모두 읽어도 실제로 동작하는 컴파일러를 만들기에는 막막하다. 이런 교과서의 난해함이 "컴파일러는 어렵다"는 신화를 만들었다.

## 추천 자료 1: Let's Build a Compiler!

[Jack Crenshaw의 시리즈](http://compilers.iecc.com/crenshaw/) (1988~)

- **Turbo Pascal급 컴파일러**를 단계별로 구현하는 튜토리얼
- 단일 패스, 파싱과 코드 생성을 동시에 수행
- 최소한의 최적화만 적용
- 원본은 Pascal, C 버전과 [Forth 번역](http://home.iae.nl/users/mhx/crenshaw/tiny.html)도 존재
- 복잡한 주제를 1학년 프로그래밍 수업 수준으로 풀어냄

**한계**: 추상 구문 트리(AST)를 사용하지 않는다. Pascal에서 트리 조작이 복잡하기 때문인데, Python, Lisp, Haskell 같은 고수준 언어에서는 이 제약이 사라진다.

## 추천 자료 2: A Nanopass Framework for Compiler Education

[Sarkar, Waddell, Dybvig의 논문](http://www.cs.indiana.edu/~dyb/pubs/nano-jfp.pdf) (PDF)

- 컴파일러를 **수십~수백 개의 단순한 변환 패스**로 분해하는 접근법
- 각 패스는 최대한 단순하게 유지 — 변환을 합치지 말고 분리할 것
- 프레임워크가 각 패스의 입력/출력 형식을 명세
- Scheme으로 작성, 런타임에 데이터 유효성 검증

## 핵심 통찰

**컴파일러는 프로그램 내부 표현(AST)의 연속적 변환에 불과하다.** 이 두 자료를 통해 실제 동작하는 컴파일러를 만든 후에, 필요하다면 Dragon Book 같은 정석 교과서로 넘어가면 된다. 혹은 아예 필요 없을 수도 있다.
