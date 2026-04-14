---
title: "Artemis II 내결함성 컴퓨터"
tags: [fault-tolerance, aerospace, embedded-systems, real-time-os, redundancy]
updated: 2026-04-13
sources:
  - https://cacm.acm.org/news/how-nasa-built-artemis-iis-fault-tolerant-computer/
---

# Artemis II 내결함성 컴퓨터

NASA의 오리온 캡슐은 심우주 유인 비행을 위한 고도의 내결함성 컴퓨팅 아키텍처를 채택했다.
아폴로와 달리 오리온은 생명 유지, 통신 라우팅을 포함한 거의 모든 안전 임계 기능을 소프트웨어로 관리한다.

## 8중 CPU 병렬 구조

- 2개의 Vehicle Management Computer(VMC), 각각 2개의 Flight Control Module(FCM) → 총 4개 FCM
- 각 FCM은 자가 검사(self-checking) 프로세서 쌍으로 구성 → 실질적으로 **8개 CPU**가 비행 소프트웨어를 병렬 실행
- 22초 내에 FCM 3개가 손실되어도 나머지 1개로 안전하게 운항 가능

## Fail-Silent 설계

- 방사선 이벤트로 오류 계산이 발생하면 해당 FCM은 즉시 묵음(fail-silent) 처리
- 전통적 3중 투표 방식 대신 **우선순위 기반 소스 선택 알고리즘** 사용
- 묵음된 FCM은 폐기되지 않고, 상태를 재동기화한 후 그룹에 재합류

## 결정론적 아키텍처

- **시간 트리거 이더넷(Time-Triggered Ethernet)**: 전체 시스템에 공통 시간 배포
- **ARINC 653** 호환 스케줄러: major frame / minor frame 단위 시간·공간 파티셔닝
- 모든 FCM이 동일한 입력, 동일한 코드, 동일한 출력을 생성하도록 강제
- 매초 FCM 클럭 드리프트를 측정해 네트워크 시간에 재보정

## 하드웨어 강화

- **3중 모듈 중복 메모리(TMR)**: 읽기 시마다 단일 비트 오류 자가 수정
- 네트워크 인터페이스 카드: 2레인 트래픽 비교 — 비트 플립 시 fail-silent 처리
- 네트워크 자체도 3중 독립 플레인

## 백업 비행 소프트웨어(BFS)

공통 모드 장애(소프트웨어 버그 등)를 대비한 **이종 중복(dissimilar redundancy)**:

- 다른 하드웨어, 다른 OS, 독립 개발된 간소화 소프트웨어
- 주 컴퓨터 전체 장애 시 자동으로 소스 선택에 의해 BFS가 인수
- BFS로 미션의 모든 동적 단계 완료 후 정적 단계에서 주 FCM 복구 시도 가능

## Dead Bus 생존

전원 완전 손실 시나리오:
1. 전원 복구 → 안전 모드 진입
2. 태양 전지판을 태양 방향으로 정렬 → 전력 회복
3. 열 안정을 위해 선미를 태양 방향으로 정렬
4. 지구와 통신 재개 시도
5. 승무원이 수동으로 생명 유지 구성 또는 우주복 착용 가능

## 검증 방법론

- 전체 환경 시뮬레이션 및 **몬테카를로 스트레스 테스트**
- 슈퍼컴퓨터를 이용한 대규모 **결함 주입(fault injection)**: 비행 전체 타임라인에서 치명적 하드웨어 고장을 주입해 fail-silent 및 복구 여부 검증

## 아폴로와의 비교

| 항목 | 아폴로 AGC | Artemis II 오리온 |
|------|-----------|-----------------|
| 프로세서 | 1 MHz | 다중 FCM (8 CPU) |
| 메모리 | ~4 KB RAM + rope 메모리 | TMR 메모리 |
| 제어 범위 | 제한적 (전기기계식 폴백) | 거의 모든 안전 임계 기능 |
| 중복 전략 | 단일 컴퓨터 | 4-FCM + BFS 이종 중복 |
