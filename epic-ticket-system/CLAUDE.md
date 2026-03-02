# Epic Architect — 오케스트레이터 (CLAUDE.md)

## 역할

완성된 PRD를 기술 에픽으로 분해하고, Confluence 초안 문서를 자동 생성한 뒤,
개발자 컨펌을 거쳐 실제 Jira 에픽 티켓을 생성하는 개발 준비 자동화 시스템.

---

## 1. 입력 수신 및 분류

사용자 입력에서 아래 항목을 식별한다:

| 항목 | 형식 | 필수 여부 |
|------|------|----------|
| PRD 출처 | Confluence URL 또는 로컬 .md 파일 경로 | **필수** |
| Jira 이니셔티브 키 | 예: TM-2061 | **필수** |
| 참여 직무 | BE / FE / MLE / DS 중 해당 직무 | 선택 (기본: BE + FE) |
| 대상 Confluence Space | Space 키 | 선택 (기본: 이니셔티브 meta.json 참조) |

**PRD 출처가 없으면**:
> "어떤 PRD를 에픽으로 분해할까요? Confluence URL 또는 로컬 파일 경로를 알려주세요."

---

## 2. 전체 워크플로우

```
PRD (Confluence URL or .md)  +  Jira 이니셔티브 키
              │
              ▼
[Phase 1: Confluence 초안 작성]
  Step 1-A: PRD 콘텐츠 로드
    - Confluence URL → fetch_page.py로 마크다운 변환
    - 로컬 .md → 직접 읽기
              │
  Step 1-B: epic-architect 에이전트 호출
    - 직무별(BE/FE/MLE/DS) 에픽 분리
    - 각 에픽의 제목, 우선순위, AC, Start/Due 계산
    - output/epic_spec_{YYYYMMDD}_{주제}.json 저장
              │
  Step 1-C: Confluence 초안 페이지 생성
    - epic_template.md 기반 Storage XHTML 구성
    - upload.py 호출 → PRD 하위 [Draft] 페이지 생성
              │
  Step 1-D: 결과 요약 출력 + 사용자 컨펌 대기
    "Jira에 생성할까요? '실행'이라고 입력해주세요."
              │
              ▼ (사용자: "실행" 입력 시)
[Phase 2: Jira 티켓 동기화]
  Step 2-A: fetch_initiative.py → 공통 라벨·컴포넌트 추출
  Step 2-B: create_tickets.py → 에픽 티켓 생성
  Step 2-C: Confluence 초안 → [Done] 상태로 제목 업데이트
  Step 2-D: 결과 URL 목록 출력
```

---

## 3. Phase 1: Confluence 초안 작성

### Step 1-A: PRD 콘텐츠 로드

#### Confluence URL인 경우

URL에서 페이지 ID를 추출한 뒤 fetch_page.py 호출:

```bash
# URL 예시: https://musinsa-oneteam.atlassian.net/wiki/spaces/XXX/pages/216960895/...
# → 페이지 ID: 216960895

cd /Users/musinsa/Documents/agent_project/pm-studio && \
python3 .claude/skills/confluence-tool/scripts/fetch_page.py \
  --page-id {페이지_ID} \
  --output epic-ticket-system/output/prd_source.json \
  --json
```

#### 로컬 .md 파일인 경우

파일을 직접 읽어 분석에 활용한다.

### Step 1-B: epic-architect 에이전트 호출

```
Task: 아래 PRD를 분석하여 직무별 에픽 스펙을 생성해줘.
참여 직무: {BE / FE / MLE / DS 중 해당 직무}
이니셔티브 키: {TM-xxxx}
dependency_rules.md를 참조하여 Start/Due Date를 계산할 것.
결과를 output/epic_spec_{YYYYMMDD}_{주제}.json에 저장할 것.

--- PRD 내용 ---
{prd_source.json의 content 필드}
```

### Step 1-C: Confluence 초안 페이지 생성

epic-architect가 반환한 epic_spec.json을 기반으로 epic_template.md를 채워
`output/epic_draft.html`(Confluence Storage XHTML)을 생성한 뒤 업로드:

```bash
cd /Users/musinsa/Documents/agent_project/pm-studio && \
python3 .claude/skills/confluence-tool/scripts/upload.py \
  --title "[Draft] {주제} Epic Specification" \
  --space {Space_키} \
  --parent-id {PRD_페이지_ID} \
  --draft epic-ticket-system/output/epic_draft.html
```

### Step 1-D: 결과 요약 및 컨펌 요청

```
📋 Epic 초안 생성 완료!

📄 Confluence 초안: {draft_page_url}

┌─────────────────────────────────────────────────────────┐
│ 직무  │ 에픽 제목                    │ 우선순위 │ 예상 기간     │
├───────┼─────────────────────────────┼──────────┼───────────────┤
│ BE    │ [BE] {에픽명}               │ High     │ MM/DD ~ MM/DD │
│ FE    │ [FE] {에픽명}               │ High     │ MM/DD ~ MM/DD │
└─────────────────────────────────────────────────────────┘

총 {N}개 에픽 | 예상 전체 기간: {N}일

Jira에 실제 티켓을 생성할까요?
➡ "실행" 또는 "Jira 생성해줘"라고 입력하시면 진행합니다.
➡ 수정이 필요하면 수정 내용을 말씀해주세요.
```

---

## 4. Phase 2: Jira 티켓 동기화

**Phase 2는 사용자가 "실행" 또는 "Jira 생성해줘"라고 명시적으로 입력한 경우에만 시작한다.**

### Step 2-A: 이니셔티브 메타데이터 추출

```bash
cd /Users/musinsa/Documents/agent_project/pm-studio && \
python3 epic-ticket-system/.claude/skills/jira-skill/scripts/fetch_initiative.py \
  --issue-key {TM-xxxx} \
  --output epic-ticket-system/output/initiative_meta.json
```

### Step 2-B: 에픽 티켓 생성

```bash
cd /Users/musinsa/Documents/agent_project/pm-studio && \
python3 epic-ticket-system/.claude/skills/jira-skill/scripts/create_tickets.py \
  --spec epic-ticket-system/output/epic_spec_{YYYYMMDD}_{주제}.json \
  --meta epic-ticket-system/output/initiative_meta.json \
  --output epic-ticket-system/output/jira_result_{YYYYMMDD}_{주제}.json
```

### Step 2-C: Confluence 초안 제목 업데이트

Draft → Done 상태 반영을 위해 Confluence 페이지 제목을 변경한다:

```bash
python3 .claude/skills/confluence-tool/scripts/upload.py \
  --title "[Done] {주제} Epic Specification" \
  --space {Space_키} \
  --parent-id {PRD_페이지_ID} \
  --draft epic-ticket-system/output/epic_draft.html
```

### Step 2-D: 완료 출력

```
✅ Jira 에픽 생성 완료!

🔗 생성된 티켓:
  [BE] {에픽명}  →  {JIRA_URL}/browse/TM-xxxx
  [FE] {에픽명}  →  {JIRA_URL}/browse/TM-xxxx

📄 Confluence 문서: {confluence_url}
📁 결과 파일: epic-ticket-system/output/jira_result_{YYYYMMDD}_{주제}.json
```

---

## 5. epic-architect 에이전트 호출 규약

```
Task: 아래 PRD를 분석하여 직무별 에픽 스펙을 생성해줘.
에이전트 스펙: epic-ticket-system/.claude/agents/epic-architect/AGENT.md 참조

참여 직무: {BE / FE / MLE / DS}
이니셔티브 키: {TM-xxxx}
오늘 날짜: {YYYY-MM-DD}

--- PRD 내용 ---
{PRD 전문}
```

에이전트가 반환하는 JSON 구조:

```json
{
  "topic": "CampaignMetaEngine",
  "initiative_key": "TM-2061",
  "generated_at": "2026-03-02",
  "epics": [
    {
      "role": "BE",
      "title": "[BE] Campaign Asset API 개발",
      "priority": "High",
      "effort_days": 8,
      "start_date": "2026-03-10",
      "due_date": "2026-03-22",
      "dependencies": [],
      "description": "소재 등록 및 관리를 위한 핵심 백엔드 기능 구축",
      "acceptance_criteria": [
        "API 응답 속도 200ms 이내",
        "광고 코드 중복 생성 방지 로직 적용 확인"
      ]
    }
  ]
}
```

---

## 6. 이니셔티브 컨텍스트 우선 참조

`initiatives/index.md`에서 이니셔티브 키를 확인하고, 해당 `meta.json`의
`confluence.primary_space`를 Confluence 업로드 기본 Space로 사용한다.

---

## 7. 오류 처리

| 오류 유형 | 처리 방법 |
|----------|----------|
| PRD URL 접근 불가 | 로컬 파일 경로 또는 PRD 내용 직접 입력 요청 |
| 이니셔티브 키 없음 | Jira 이니셔티브 키 재입력 요청 |
| Confluence 업로드 실패 | `output/epic_draft.html` 경로 안내, Phase 2는 계속 가능 |
| Jira 생성 실패 (일부) | 성공한 티켓 URL 먼저 출력, 실패 항목 재시도 또는 수동 생성 안내 |
| 직무 판단 불가 | 사용자에게 직무 목록 확인 요청 |
