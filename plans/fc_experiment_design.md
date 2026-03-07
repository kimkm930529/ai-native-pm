# Dynamic Frequency Capping 실험 설계서

> **작성일**: 2026-03-07
> **작성자**: 김경민
> **상태**: 초안 (내부 검토 전)
> **관련 이니셔티브**: Frequency Capping 정식 운영 (Q2)

---

## 목차

1. [배경 및 문제 정의](#1-배경-및-문제-정의)
2. [가설](#2-가설)
3. [실험 설계](#3-실험-설계)
4. [지표 정의](#4-지표-정의)
5. [타임라인](#5-타임라인)
6. [결과 해석 및 Next Action](#6-결과-해석-및-next-action)
7. [MATCH 시스템 요구사항](#7-match-시스템-요구사항)
8. [운영 준비사항](#8-운영-준비사항)
9. [Appendix — 지표 설계 논의 과정](#9-appendix--지표-설계-논의-과정)
10. [Open Questions](#10-open-questions)

---

## 1. 배경 및 문제 정의

### 현황

- **현재 Braze Global FC**: 주간 5회 (채널/카테고리 무관 전체 합산)
- Static cap 구조로 인해 고참여 유저와 저참여 유저에게 동일한 빈도를 적용 중
- **문제 1**: 저참여 유저에게 5회 발송은 수신거부 리스크를 높이고 있음
- **문제 2**: 고참여 유저에게는 오히려 cap이 기회를 제한하는 구조
- **문제 3**: Action-based CRM (구매 완료, 장바구니 이탈 등 행동 기반 메시지)과 Promo/Strategy 메시지가 동일한 cap 풀에서 경쟁 중 — 마케팅 개입 여지가 구조적으로 좁음

### 목표

참여도 기반 Dynamic Frequency Capping을 도입하여:
- 저참여 유저 수신거부율 감소
- 고참여 유저 전환 기회 확대
- MATCH가 Promo/Strategy 영역에서 개인화 최적화 효용을 발휘할 수 있는 구조 확보

---

## 2. 가설

> **핵심 가설**: "모든 유저에게 동일한 발송 횟수를 적용하는 것보다, 참여도 기반으로 발송 횟수를 차등 적용하면 전체 유저 레벨의 CRM 기여 세션이 증가하고 수신거부율은 감소한다."

| 세부 가설 | 방향 |
|---------|------|
| 고참여 유저(High Engager)에게 Promo 발송을 3회까지 허용하면 유저당 전환수가 증가한다 | Positive |
| 저참여 유저(Low Engager)에게 Promo 발송을 0~1회로 줄이면 수신거부율이 감소한다 | Positive |
| Action-based CRM을 별도 cap 풀로 분리하면 Promo 메시지 최적화 여지가 확대된다 | Positive |

---

## 3. 실험 설계

### 3-1. FC 구조 개편

현재의 단일 Global Cap을 두 카테고리로 분리한다.

```
[현재]
─────────────────────────────────────────────
Global FC: 주간 5회 (전 카테고리 합산)

[개편 후]
─────────────────────────────────────────────
Action-based CRM    : 주간 최대 3회  (고정)
Promo / Strategy    : 주간 0~3회     (MATCH 자동 결정, Engagement Tier 기반)
─────────────────────────────────────────────
Total               : 주간 최대 6회  (High Engager 기준)
```

**Action-based CRM 범위 (예시)**
- 장바구니 이탈 리마인드
- 찜 상품 가격 인하 알림
- 구매 완료 후 리뷰 유도
- 재입고 알림

**Promo/Strategy 범위 (예시)**
- 타임 세일 / 기획전
- 개인화 추천 푸시 (MATCH 생성)
- 라이브커머스 알림
- 세일즈푸시 (11시 발송)

### 3-2. Engagement Tier 정의

> ML팀과 협의하여 기준 확정 필요. 아래는 초안 기준.

| Tier | 기준 (안) | Promo 주간 Cap |
|------|---------|--------------|
| **High Engager** | 최근 30일 CTR ≥ X% 또는 구매 N회 이상 | 3회 |
| **Mid Engager** | 기본 (High/Low 미해당) | 2회 |
| **Low Engager** | 최근 30일 푸시 오픈 0회 또는 CTR < Y% | 0~1회 |

- 기준값 X%, Y%, N은 ML팀과 데이터 기반으로 확정
- Tier는 주 단위 재계산 (MATCH가 발송 시점에 최신 Tier 참조)
- Action-based CRM cap은 Tier와 무관하게 고정 3회 적용

### 3-3. 실험군 / 대조군 설계

단순 전후 비교가 아닌, **Tier 내 A/B 실험**으로 설계한다.
(Tier 간 비교는 참여도 차이가 confounding이 되므로 부적합)

```
각 Engagement Tier 내에서:

  Control   → 현재 방식 (Global FC 5회, 카테고리 미분리)
  Treatment → Dynamic FC (Action 3 + Promo 0~3, Tier 기반)

  High Engager:  Control vs Treatment(Promo 3회 허용)
  Mid Engager:   Control vs Treatment(Promo 2회)
  Low Engager:   Control vs Treatment(Promo 0~1회)
```

- 유저 단위 랜덤 배정 (User-level randomization)
- 배정은 실험 시작 시점 Tier 기준으로 고정 (실험 중 Tier 변동 시 배정 유지)
- 실험 기간: 최소 4주 (라이브커머스 사이클, 세일 이벤트 1회 이상 포함)

### 3-4. 실험 전제 조건

| 조건 | 기한 |
|------|------|
| Auxia PoC 종료 확인 | 4월 말 |
| Campaign Meta Engine Phase 2 안정화 | 5월 중순 이후 착수 권장 |
| ML팀 Engagement Tier 기준 확정 | 실험 착수 4주 전 |
| Braze 캠페인 태그 분리 완료 | 실험 착수 전 |
| Attribution 집계 파이프라인 준비 | 실험 착수 전 |

---

## 4. 지표 정의

### Primary

| 지표 | 정의 | 측정 단위 |
|------|------|---------|
| **유저당 CRM 기여 세션** | 푸시 클릭 → 30분 내 앱 세션 / 유저 | Tier별 Control vs Treatment 비교 |

> 단순 집계 비교가 아닌 **Tier 내 Control 대비 lift** 측정이 핵심

### Secondary

| 지표 | 정의 | 목적 |
|------|------|------|
| 메시지당 CTR (Promo/Strategy) | 클릭수 / 발송수 (캠페인 태그 기준) | 발송 효율 최적화 신호 |
| 메시지당 CTR (Action-based) | 클릭수 / 발송수 | Action cap 적정성 모니터링 |
| Tier별 유저당 전환수 | 구매 전환 / 유저 | 실질 매출 임팩트 |

### Guardrail

| 지표 | 기준 | 비고 |
|------|------|------|
| 수신거부율 | Control 대비 증가 없음 | Low Engager 집중 모니터링 |
| 앱 이탈율 (Low Engager) | Control 대비 증가 없음 | 0회 발송 그룹은 수신거부 이벤트 없으므로 앱 이탈율로 대체 |
| 전체 CRM 기여 세션 | 감소 없음 | 자동화 전환 안전망 |
| 발송 오류율 | 현 수준 유지 | 파이프라인 안정성 |

### 지표 간 Trade-off 시나리오

| 시나리오 | 해석 |
|---------|------|
| Primary ↑, Guardrail 수신거부율 ↑ | 고참여자 효과는 있으나 저참여자 피로 증가 → Tier 경계 조정 필요 |
| Primary ↔, Secondary CTR ↑ | 적은 메시지로 같은 성과 → 발송 비용 효율화 관점에서 긍정 |
| Low Engager 앱 이탈율 ↓ | Promo 감소가 앱 이탈 방어에 효과적 → Phase 2 설계에 반영 |

---

## 5. 타임라인

| 기간 | 내용 |
|------|------|
| **4월** | 실험 설계 확정 / ML팀 Tier 기준 협의 / Braze 태그 분리 준비 / Attribution 파이프라인 구축 |
| **5월 초** | Auxia PoC 종료 후 실험 환경 정비 |
| **5월 중순~말** | Phase 2 안정화 확인 후 실험 착수 |
| **6월 말** | 4주 이상 데이터 수집 완료 → 결과 분석 |
| **6월 말~7월 초** | 결과 리뷰 + 정식 운영 전환 또는 재설계 결정 |

---

## 6. 결과 해석 및 Next Action

### 판단 매트릭스

| Primary | Guardrail | 판단 | Next Action |
|---------|-----------|------|------------|
| Lift 유의 | 이상 없음 | **정식 전환** | Dynamic FC를 전체 유저 대상으로 롤아웃. Tier 기준 정교화 (Phase 2) |
| Lift 유의 | 수신거부 증가 | **Tier 경계 재조정** | Low Engager cap 추가 하향 또는 기준 재협의 후 재실험 |
| Lift 없음 | 이상 없음 | **Static cap 유지, 구조만 채택** | Action/Promo 분리 구조는 유지하되 cap 수치 재검토 |
| Lift 없음 | 수신거부 증가 | **실험 중단, 원인 분석** | Tier 정의 오류 또는 콘텐츠 품질 문제 가능성 검토 |

### Phase 2 고려 사항 (Next Phase)

1. **구매 사이클 기반 Dynamic FC**: 구매 직후 N일간 Promo cap 자동 하향 (구매 직후 수신거부 방지)
2. **채널별 FC 분리**: 앱푸시 / 카카오 / 이메일 채널별 독립 cap
3. **실시간 Tier 업데이트**: 주 단위 → 행동 이벤트 기반 즉시 재계산

---

## 7. MATCH 시스템 요구사항

Dynamic FC를 MATCH가 자율 결정하려면 아래 기능이 필요하다.

### 7-1. 유저별 메시지 수신 이력 관리 (Per-user Inbox)

MATCH가 "이 유저에게 이번 주 Promo를 몇 회 보냈는가"를 실시간으로 알아야 한다.

| 기능 | 설명 |
|------|------|
| Per-user 발송 카운터 | 카테고리(Action-based / Promo)별, 주간 단위 발송 횟수 저장 |
| 실시간 조회 API | 발송 전 현재 카운터 확인 → cap 초과 시 발송 블로킹 |
| 이력 보존 기간 | 최소 90일 (실험 분석 및 Tier 재계산용) |
| 저장 구조 (안) | `user_id`, `campaign_category`, `sent_at`, `campaign_id` |

> 이 기능이 실질적으로 "유저 Inbox 시스템"의 기반이 된다.
> 향후 유저에게 수신 메시지 히스토리를 노출하는 인앱 Inbox로 확장 가능.

### 7-2. Engagement Tier 실시간 참조

| 기능 | 설명 |
|------|------|
| Tier 스코어 저장소 | ML팀이 계산한 유저별 Tier를 MATCH가 읽을 수 있는 형태로 제공 |
| 발송 시점 Tier 조회 | 캠페인 실행 시 최신 Tier 값 참조 |
| Tier 갱신 주기 | 주 1회 배치 (초기), 이후 이벤트 기반 실시간으로 고도화 |

### 7-3. 캠페인 카테고리 태깅 시스템

Braze 캠페인에 카테고리 태그를 부착하여 MATCH와 Attribution 파이프라인이 식별할 수 있도록 한다.

| 태그 | 적용 대상 | FC 풀 |
|------|---------|------|
| `action_based` | 장바구니 이탈, 가격 인하, 재입고 등 | Action-based 3회 풀 |
| `promo_strategy` | 기획전, MATCH 생성 개인화 푸시, 세일즈푸시 | MATCH 관리 0~3회 풀 |

- Braze 캠페인 생성 시 태그 필수 입력 규칙 수립 필요
- 태그 누락 캠페인은 `promo_strategy` 기본값 처리 (안전 방향)

### 7-4. MATCH 발송 의사결정 로직

```
캠페인 발송 요청
    │
    ▼
[1] 유저 Engagement Tier 조회
    │
    ▼
[2] 해당 주 Promo 발송 카운터 조회
    │
    ├── 카운터 < Tier 허용 횟수  → 발송 진행
    │
    └── 카운터 >= Tier 허용 횟수 → 발송 블로킹
                                    (다음 주 초기화까지 보류 또는 폐기)
```

### 7-5. 향후 확장: 인앱 Inbox

Per-user 발송 이력 시스템이 구축되면 다음 단계로 확장 가능:

| 기능 | 설명 |
|------|------|
| 인앱 메시지 보관함 | 수신한 Promo/개인화 메시지를 앱 내에서 재열람 가능 |
| 메시지 유효기간 관리 | 세일 종료 후 만료 처리 |
| 개인화 추천 히스토리 | MATCH가 생성한 추천의 클릭/전환 이력 유저에게 노출 |

> Q2 MVP 범위 외. Per-user Inbox 인프라 구축 이후 Q3~Q4 검토.

---

## 8. 운영 준비사항

### Attribution 집계 파이프라인

| 항목 | 내용 |
|------|------|
| 태그 기준 집계 | `action_based` / `promo_strategy` 태그별 CTR, 전환, 수신거부 분리 집계 |
| Tier 기준 집계 | High / Mid / Low Engager별 지표 분리 |
| Control/Treatment 분리 | 실험 기간 중 배정 그룹 기준 분리 집계 |
| 리포팅 주기 | 주 1회 (실험 중 이상 감지 시 일별 모니터링) |

### 실험 착수 체크리스트

- [ ] ML팀 Engagement Tier 기준 확정
- [ ] Braze 캠페인 태그 분리 및 태깅 규칙 적용
- [ ] MATCH Per-user 발송 카운터 기능 개발 완료
- [ ] Attribution 파이프라인 태그 기준 집계 적용
- [ ] Auxia PoC 공식 종료 확인
- [ ] Campaign Meta Engine Phase 2 안정화 확인
- [ ] 실험 기간 내 주요 이벤트 일정 확인 (세일, 라이브커머스 등)

---

## 참조

| 항목 | 내용 |
|------|------|
| 관련 Q2 계획 | `plans/2026Q2_plan.md` — 3-2. Frequency Capping 정식 운영 |
| 담당 협력팀 | 그로스마케팅1 (권민용), ML팀 (Tier 정의), MATCH 개발팀 |

---

## 9. Appendix — 지표 설계 논의 과정

> 이 섹션은 실험 설계 과정에서 지표 선택과 관련해 검토하고 기각한 대안들, 그리고 그 근거를 기록한다.

### A. 메시지당 CTR을 Primary로 쓰지 않은 이유

초기에는 메시지당 CTR (`클릭수 / 발송수`)을 Primary 지표로 고려했으나 아래 구조적 문제로 Secondary로 내렸다.

**문제: 발송량 차이로 인한 비교 왜곡**

Dynamic FC는 Tier별로 발송량 자체가 다르다. High Engager는 주간 Promo 3회, Low Engager는 0~1회를 받는다. 이 상태에서 메시지당 CTR을 비교하면:

- High Engager의 CTR이 높은 것이 "Dynamic FC의 효과"인지 "원래 참여도가 높은 유저이기 때문"인지 분리 불가
- Tier 내 Control/Treatment 비교도 발송량이 달라지면 분모 자체가 바뀌어 단순 비교가 왜곡됨

**메시지당 CTR이 여전히 유용한 영역**

메시지당 CTR은 "어떤 콘텐츠/시간대/유형이 효과적인가"를 최적화하는 데는 유효하다. 단, "FC를 늘리는 것이 좋은가"라는 이번 실험의 핵심 질문에는 부적합하다.

---

### B. Primary 지표로 유저당 CRM 기여 세션을 선택한 근거

유저당 CRM 기여 세션 (`푸시 클릭 → 30분 내 앱 세션 / 유저`)은 발송량과 무관하게 유저 레벨에서 "실제로 CRM이 얼마나 기여했는가"를 측정한다.

| 조건 | 메시지당 CTR | 유저당 CRM 기여 세션 |
|------|------------|------------------|
| Tier별 발송량이 다를 때 | 왜곡 발생 | 유저 단위이므로 공정 비교 가능 |
| 한 유저가 3회 받고 1번 클릭 | CTR = 33% | 기여 세션 = 1 (실제 임팩트) |
| 한 유저가 1회 받고 1번 클릭 | CTR = 100% | 기여 세션 = 1 (동일) |

**측정 방식**: Tier별로 Control 그룹 대비 Treatment 그룹의 유저당 기여 세션 lift를 측정. 절대값 비교가 아닌 **Tier 내 상대적 변화**가 핵심이다.

---

### C. Low Engager Guardrail 지표 설계 과정

**문제**: Low Engager에게 Promo 0회를 보내는 경우, 수신거부 이벤트 자체가 발생하지 않는다. 따라서 수신거부율만으로는 "덜 보내서 이탈이 줄었다"는 효과를 측정할 수 없다.

**해결**: 수신거부율 대신 **앱 이탈율 (Low Engager 한정)** 을 Guardrail로 추가.

- 수신거부율: 발송된 메시지 기준 → 0회 발송 그룹에서 발생 불가
- 앱 이탈율: 발송 여부와 무관하게 측정 가능 → Low Engager의 잔존 효과 간접 측정

---

### D. Tier 내 A/B 설계를 선택한 근거

단순히 High/Mid/Low Engager의 지표를 비교하는 방식(Tier 간 비교)은 **참여도 차이 자체가 confounding**이 되어 Dynamic FC의 순수 효과를 측정할 수 없다.

```
[잘못된 비교]
High Engager Treatment vs Low Engager Treatment
→ 참여도 차이 + FC 차이가 혼재 → 인과 관계 불명확

[올바른 비교]
High Engager Control vs High Engager Treatment  ← 동일 참여도, FC만 다름
Low Engager Control  vs Low Engager Treatment   ← 동일 참여도, FC만 다름
```

Tier 내 A/B로 설계하면 각 Tier에서 FC 변화의 순수 효과를 분리할 수 있다.

---

## 10. Open Questions

> 현재 미결 상태로, 추가 논의 또는 데이터 확인이 필요한 항목들.

| # | 질문 | 중요도 | 담당/기한 |
|---|------|--------|---------|
| OQ-1 | **Engagement Tier 기준값 확정**: CTR X%, Y%, 구매 N회의 구체적 임계값. 현재 데이터 분포 확인 필요 | 높음 | ML팀 협의 / 4월 |
| OQ-2 | **Primary 지표 심화 검토**: 유저당 CRM 기여 세션 외 유저당 전환수(구매) 또는 Revenue per user를 Primary로 올려야 하는지 | 높음 | 지표 딥다이브 세션 예정 |
| OQ-3 | **Tier 고정 vs 유동**: 실험 중 Tier가 변동되는 유저 처리 방법 — 배정 시점 Tier로 고정할 경우 4주 뒤 실제 Tier와 괴리 발생 가능 | 중간 | 실험 설계 확정 시 |
| OQ-4 | **Action-based 3회 cap 적정성**: 현재 Action-based 메시지가 실제로 주간 몇 회 발생하는지 데이터 확인 필요. 3회가 현실적으로 도달 가능한 수치인지 | 중간 | 데이터 확인 / 4월 |
| OQ-5 | **Promo cap 0회의 범위**: Low Engager에게 Promo 0회 적용 시, 전체 메시지(Action-based 포함)도 0인 유저가 발생하는가. 완전 무발송 유저 처리 정책 필요 | 중간 | 정책 결정 / 4월 |
| OQ-6 | **실험 기간 최소화 vs 충분한 데이터**: 4주 실험 기간이 통계적 유의성을 확보하기에 충분한가. 세일 이벤트 포함 여부에 따라 결과 편향 가능성 | 낮음 | 실험 설계 확정 시 |

---

*최초 작성: 2026-03-07 | 다음 검토: 실험 착수 전 (예정: 2026-05)*
