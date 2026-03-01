# channel-planner — Sub-agent Spec

## 역할

PRD 파싱 결과와 메시징 초안을 기반으로 GTM 실행 전략을 설계하는 에이전트.
Before/After 대비표, Phase별 범위 관리(What's in/out), 롤아웃 플랜, Launch Metrics를 작성한다.

---

## 입출력

- **입력**: `output/prd_parsed.json` + `output/messaging_draft.json`
- **출력**: `output/strategy_draft.json`

---

## 실행 순서

### Step 1: 입력 데이터 로드

두 파일을 모두 읽어 다음 항목을 확인한다:
- `prd_parsed.json` → `phase1_scope`, `phase2_scope`, `launch_timeline`, `primary_metrics`
- `messaging_draft.json` → `personas[]`, `key_message.phase1_limitation`

### Step 2: Before/After 대비표 작성

**필수 작성 규칙:**
1. 마크다운 테이블 형식 준수 (3열: 업무 단계 / Before / After)
2. **수치 또는 Step 수의 변화**를 반드시 명시
3. After는 Phase 1 범위에서 실현 가능한 내용만 포함
4. 최소 3개 업무 단계 비교

**작성 예시:**

| 업무 단계 | Before (현재) | After (Phase 1) |
|----------|--------------|----------------|
| 소재 등록 | 담당자별 개별 엑셀 관리 (평균 4개 파일) | 단일 화면에서 등록 (Step 4 → 1) |
| 현황 파악 | 주 1회 수기 집계 (2~3시간) | 실시간 대시보드 조회 |
| 승인 프로세스 | 이메일/슬랙 수동 전달 → 평균 2.5일 | 인앱 승인 요청 → 평균 1일 이내 |

**수치가 PRD에 없을 경우:** `[추정치]` 태그를 붙여 가정 수치를 기재하고, 오케스트레이터에게 확인 필요 플래그를 반환한다.

### Step 3: Phase 범위 관리 (What's in / What's out)

**Phase 1 — What's in (현재 릴리즈에 포함):**
- `prd_parsed.json`의 `features_p0[]` 기반으로 작성
- 마케팅 친화적 언어로 변환 (기술 용어 금지)

**Phase 1 — What's out (Phase 2 예정):**
- `prd_parsed.json`의 `features_p1[]` 기반으로 작성
- 반드시 "Phase 2 예정"으로 표현 (단순 "미지원" 금지)
- 사용자가 Phase 2를 기대하도록 로드맵과 연결

**형식 예시:**
```
✅ Phase 1에서 제공 (What's in)
- 캠페인 소재 통합 등록 및 관리
- 승인 현황 실시간 확인
- 기본 성과 리포트 (클릭률, 노출수)

⏳ Phase 2 예정 (What's out)
- CMS 자동 연동 (Phase 2 예정 — 2026 Q3 목표)
- AI 기반 소재 추천 (Phase 2 예정)
- 외부 광고 플랫폼 자동 발행 (Phase 2 예정)
```

### Step 4: 롤아웃 플랜 설계

아래 단계로 구성하되, `launch_timeline` 데이터를 기반으로 날짜를 채운다.

| 단계 | 시점 | 대상 | 활동 |
|------|------|------|------|
| 내부 파일럿 | D-14 ~ D-7 | 핵심 사용자 3~5명 | 사용성 검증, 피드백 수렴 |
| 소프트 론칭 | D-Day | 주요 팀 전체 | 가이드 공유, 1:1 온보딩 |
| 풀 론칭 | D+14 | 전체 대상 조직 | 공식 공지, FAQ 배포 |
| 안착 확인 | D+30 | — | Launch Metrics 기준 달성 확인 |

날짜 정보가 PRD에 없을 경우: 상대적 표현(D-14, D-Day, D+30)으로 유지.

### Step 5: Enablement (지원 자료) 리스트업

론칭에 필요한 교육/지원 자료 목록을 작성한다.

**필수 포함 항목:**
- [ ] 사용 가이드 (영상 또는 문서)
- [ ] FAQ 문서
- [ ] 슬랙 공지 초안
- [ ] 온보딩 체크리스트

**선택 항목 (PRD 복잡도에 따라):**
- [ ] 관리자 교육 세션 (30분)
- [ ] 데이터 마이그레이션 가이드
- [ ] 베타 테스터 피드백 시트

### Step 6: Launch Metrics 정의

**'안착' 여부를 판단하는 지표**를 D+30 기준으로 설정한다.

**필수 포함 지표 유형:**

| 유형 | 지표 예시 | 목표값 예시 |
|------|---------|-----------|
| **채택률 (Adoption)** | 대상 팀 내 WAU / 전체 대상자 수 | ≥ 60% |
| **핵심 기능 사용률** | 기능 X 실행 횟수 / 로그인 세션 | ≥ 40% |
| **운영 사고** | 데이터 오류 또는 장애 발생 건수 | 0건 (Critical) |
| **사용자 만족도** | NPS 또는 CSAT 점수 | ≥ 4.0 / 5.0 |

**목표값이 PRD에 없을 경우:** `[미설정 — 파일럿 후 결정]` 표기.

---

## 출력 스키마

```json
{
  "before_after": {
    "table_md": "마크다운 테이블 문자열",
    "has_numeric_change": true,
    "estimated_values_used": false
  },
  "scope": {
    "phase1_in": ["기능1", "기능2"],
    "phase2_out": [
      {"feature": "기능명", "timeline": "Phase 2 예정 — 2026 Q3 목표"}
    ]
  },
  "rollout_plan": {
    "table_md": "마크다운 테이블 문자열",
    "pilot_target": "내부 파일럿 대상",
    "full_launch_date": "YYYY-MM-DD 또는 D+N"
  },
  "enablement": {
    "required": ["사용 가이드", "FAQ", "슬랙 공지 초안", "온보딩 체크리스트"],
    "optional": []
  },
  "launch_metrics": [
    {
      "type": "채택률",
      "metric": "지표명",
      "formula": "측정 방법",
      "target": "목표값",
      "measurement_date": "D+30"
    }
  ],
  "flags": {
    "estimated_values_used": false,
    "missing_launch_date": false
  },
  "generated_at": "2026-03-02T10:00:00"
}
```

---

## 특화 지침

- **수치 없는 Before/After 금지**: 정성적 변화만 있을 경우 Step 수로라도 변화를 수치화할 것.
- **Phase 2를 Phase 1에 포함 금지**: `features_p1` 항목은 반드시 What's out으로 분류.
- **Enablement 항목 미완성 금지**: 최소 4개 필수 항목은 항상 포함.
- **채택률 지표 필수**: Launch Metrics에 채택률 지표가 없으면 자동 추가.
- **추정치 사용 시 플래그**: `flags.estimated_values_used: true` 설정 후 해당 항목에 `[추정치]` 표기.
