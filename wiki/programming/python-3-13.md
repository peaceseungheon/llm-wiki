---
title: "Python 3.13 새 기능"
tags: [programming, python, release-notes]
updated: 2026-04-13
sources:
  - https://docs.python.org/3.13/whatsnew/3.13.html
---

# Python 3.13 새 기능

2024년 10월 7일 정식 출시.

## JIT 컴파일러 (실험적)

- CPython에 copy-and-patch JIT 컴파일러 도입
- 특정 워크로드에서 최대 5% 성능 향상
- `--enable-experimental-jit` 플래그로 활성화
- 기본값 아님

## GIL 비활성화 옵션 (PEP 703)

- `python3.13t` 빌드로 GIL 없이 실행 가능
- 멀티스레드 성능 대폭 향상 가능성
- 실험적 단계, 서드파티 라이브러리 호환성 이슈 존재

## 향상된 오류 메시지

- 타입 힌트 관련 오류 메시지 개선
- `NameError` 시 유사한 이름 제안 강화
- `ImportError` 시 더 구체적인 설명 제공

## REPL 개선

- 멀티라인 편집 지원
- 컬러 출력 기본 활성화
- 히스토리 개선

## 기타

- `locals()` 동작 명확화
- `dbm.sqlite3` 모듈 추가
- iOS, Android 공식 Tier 3 플랫폼 지원
