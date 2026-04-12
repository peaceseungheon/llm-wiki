---
url: https://docs.python.org/3.13/whatsnew/3.13.html
clipped: 2026-04-13
---

# Python 3.13의 새 기능

Python 3.13이 2024년 10월 7일 정식 출시됐다. 주요 변경사항:

## JIT 컴파일러 (실험적)
- CPython에 copy-and-patch JIT 컴파일러 도입
- 특정 워크로드에서 최대 5% 성능 향상
- `--enable-experimental-jit` 플래그로 활성화
- 아직 기본값은 아님

## 향상된 오류 메시지
- 타입 힌트 관련 오류가 더 명확해짐
- `NameError` 시 유사한 이름 제안 개선
- `ImportError` 시 더 구체적인 설명 제공

## GIL 비활성화 옵션 (PEP 703)
- `python3.13t` 빌드로 GIL 없이 실행 가능
- 멀티스레드 성능 대폭 향상 가능
- 아직 실험적 단계, 서드파티 라이브러리 호환성 이슈 있음

## REPL 개선
- 멀티라인 편집 지원
- 컬러 출력 기본 활성화
- 히스토리 개선

## 기타
- `locals()` 동작 명확화
- `dbm.sqlite3` 모듈 추가
- iOS, Android 공식 Tier 3 지원
