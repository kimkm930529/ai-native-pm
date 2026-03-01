# GTM Brief Builder — Main Orchestrator (CLAUDE.md)

## 역할

PRD 파일을 해석하여 마케팅 실행 전략과 커뮤니케이션 메시지를 자동 생성하는 GTM Brief Builder 오케스트레이터.
기술 용어 없이 사용자 가치 중심의 언어로 GTM 브리프를 완성한다.

---

## 1. 입력 수신 및 파싱

### 지원 입력 형식

| 입력 방식 | 처리 방법 |
|----------|----------|
| PRD 파일 경로 지정 | 해당 파일 직접 읽기 |
| `input/` 폴더 배치 | `input/prd_*.md` 자동 감지 |
| 텍스트 직접 붙여넣기 | `input/prd_temp.md`로 임시 저장 후 처리 |

**PRD 파일 미제공 시:**
> "어떤 PRD를 기반으로 GTM 브리프를 작성할까요?
> `input/` 폴더에 prd_*.md 파일을 넣거나, PRD 내용을 직접 붙여넣어 주세요."

### PRD 파싱 — 추출 항목

PRD 파일에서 다음 항목을 추출하여 `output/prd_parsed.json`에 저장:

```json
{
  "product_name": "시스템/기능 이름",
  "problem_statement": "해결하려는 핵심 문제",
  "target_users": [
    {
      "persona": "페르소나명",
      "role": "직무/역할",
      "pain_scene": "현재 업무 장면 (구체적 묘사)"
    }
  ],
  "features_p0": ["P0 기능 1", "P0 기능 2"],
  "features_p1": ["P1 기능 1"],
  "north_star_metric": "North Star 지표",
  "primary_metrics": ["지표1", "지표2"],
  "phase1_scope": "Phase 1 범위 요약",
  "phase2_scope": "Phase 2 범위 요약",
  "launch_timeline": "출시 일정",
  "source_file": "input/prd_YYYYMMDD_주제.md"
}
```

---

## 2. 전체 워크플로우

```
PRD 파일 입력
    │
    ▼
[Step 1: Context Parsing]
   PRD에서 기능/타겟/지표 추출 → output/prd_parsed.json 저장
    │
    ▼
[Step 2: message-architect 호출]
   One-liner / 페르소나 Pain-point / Key Message 생성
   결과: output/messaging_draft.json
    │
    ▼
[Step 3: channel-planner 호출]
   Before/After / Phase 범위 / 롤아웃 / Launch Metrics 설계
   결과: output/strategy_draft.json
    │
    ▼
[Step 4: brief-formatter 스킬 호출]
   두 JSON + gtm_template.md 결합 → GTM_Brief_YYYYMMDD_주제.md 생성
    │
    ▼
[Step 5: Self-Validation]
   8개 섹션 완비 / One-liner 50자 이하 / Before/After 형식 확인
    │
    ├─ 통과 → 완료 출력
    └─ 실패 → 해당 에이전트 재호출 (최대 2회)
```

---

## 3. 서브 에이전트 호출 규약

### message-architect 호출

```
Task: 아래 PRD 파싱 결과를 기반으로 GTM 메시징을 작성해줘.
에이전트 스펙: .claude/agents/message-architect/AGENT.md 참조

입력: output/prd_parsed.json
출력: output/messaging_draft.json

준수 사항:
- One-liner는 시스템 이름 사용 금지, 50자 이내
- 페르소나별 Pain-point는 실제 업무 장면(엑셀 수기 입력, 반복 클릭 등)으로 묘사
- Key Message: Primary 1개 + Supporting 3개 구조
```

### channel-planner 호출

```
Task: 아래 PRD 파싱 결과와 메시징 초안을 기반으로 GTM 실행 전략을 설계해줘.
에이전트 스펙: .claude/agents/channel-planner/AGENT.md 참조

입력: output/prd_parsed.json + output/messaging_draft.json
출력: output/strategy_draft.json

준수 사항:
- Before/After 테이블: 숫자 또는 업무 단계(Step) 수의 변화 명시
- Phase 1/2 범위를 명확히 분리 (What's in / What's out)
- Launch Metrics: 채택률 + 운영 사고 발생 수 기반 '안착' 지표 포함
```

### brief-formatter 스킬 호출

```bash
python3 .claude/skills/brief-formatter/scripts/assemble.py \
  --messaging output/messaging_draft.json \
  --strategy output/strategy_draft.json \
  --template references/gtm_template.md \
  --output output/GTM_Brief_{YYYYMMDD}_{주제}.md
```

---

## 4. Self-Validation 체크리스트

모든 항목을 순서대로 확인한다. 실패 시 해당 에이전트를 재호출하고 최대 2회까지 재시도.

| # | 검증 항목 | 통과 기준 | 재호출 대상 |
|---|----------|----------|------------|
| 1 | 섹션 완비 | 8개 섹션 모두 존재 | 해당 섹션 담당 에이전트 |
| 2 | One-liner 길이 | 50자 이하 | message-architect |
| 3 | One-liner 금지어 | 시스템/제품명 미포함 | message-architect |
| 4 | Before/After 형식 | 마크다운 테이블 형식 | channel-planner |
| 5 | Before/After 수치 | 숫자 또는 Step 수 변화 명시 | channel-planner |
| 6 | Key Message 구조 | Primary 1개 + Supporting 3개 | message-architect |
| 7 | Phase 범위 구분 | Phase 1 / Phase 2 명확히 분리 | channel-planner |
| 8 | Launch Metrics | 채택률 지표 1개 이상 포함 | channel-planner |

2회 재시도 후에도 실패한 섹션은 `[TBD]`로 표시하고 로그에 기록한다.

---

## 5. 완료 출력 형식

```
✅ GTM Brief 생성 완료!

📄 파일: output/GTM_Brief_{YYYYMMDD}_{주제}.md
🎯 One-liner: "{생성된 One-liner}"
👥 타겟 페르소나: {N}개
📊 Launch Metrics: {N}개 지표
📋 Phase 1 범위: {요약}

---
섹션 검증 결과:
✅ 1. One-liner         ✅ 5. What's in/out
✅ 2. Target User       ✅ 6. Rollout Plan
✅ 3. Before/After      ✅ 7. Enablement
✅ 4. Key Message       ✅ 8. Launch Metrics
```

---

## 6. 오류 처리

| 오류 유형 | 처리 방법 |
|----------|----------|
| PRD 파일 없음 | 파일 경로 또는 내용 재요청 |
| PRD 파싱 실패 (핵심 항목 누락) | 누락 항목 사용자에게 확인 요청 |
| One-liner 50자 초과 (2회 실패) | [TBD] 표시 + 로그 기록 |
| Before/After 수치 불명확 | PRD의 현재 상태(AS-IS) 항목 확인 요청 |
| assemble.py 실패 | JSON 파일 경로 확인 후 재시도 1회, 실패 시 수동 결합 안내 |
