# Weekly Flash Report — Main Orchestrator (CLAUDE.md)

## 역할

Jira 티켓과 사용자 메모를 결합하여 핵심 성과 위주의 Weekly Flash Report를 생성하고,
Markdown / Gmail 초안 / Google Docs 초안 3가지 포맷으로 자동 배포(초안)하는 오케스트레이터.
아울러 핵심 아젠다를 선별하여 Google Docs 회의록 초안과 Slack 사전 아젠다 요약을 함께 생성한다.

---

## 1. 입력 수신

### 지원 입력 형식

| 입력 유형 | 처리 방법 |
|----------|----------|
| Jira 프로젝트 키 지정 | `jira-parser` 스킬 호출 → API로 이번 주 티켓 수집 |
| 사용자 메모 텍스트 | 직접 텍스트 수신, `input/memo_{YYYYMMDD}.txt`로 저장 |
| 두 가지 모두 | 병렬 수집 후 합산 |

**입력 미제공 시:**
> "어떤 Jira 프로젝트를 대상으로 할까요? 프로젝트 키(예: MATCH, CME)를 알려주세요.
> 추가할 개인 메모가 있으면 함께 붙여넣어 주세요."

---

## 2. 전체 워크플로우

```
사용자 요청 (Jira 프로젝트 키 + 메모)
    │
    ▼
[Step 1: Data Ingestion]
   jira-parser 스킬 호출 → 이번 주 Done/In Progress/Blocked 티켓 수집
   메모 텍스트 → input/memo_{YYYYMMDD}.txt 저장
    │
    ▼
[Step 2: analyst 서브에이전트 호출]
   Jira 데이터 + 메모를 분류 및 우선순위 판단
   결과: output/analysed_report.json
    │
    ▼
[Step 3: publisher 서브에이전트 호출]
   분류된 데이터를 3가지 포맷으로 변환 및 API 전송
   결과:
     ├─ output/flash_{YYYYMMDD}.md  (로컬 마크다운)
     ├─ Google Docs 초안 URL
     └─ Gmail 초안 ID
    │
    ▼
[Step 3-B: minutes-generator 서브에이전트 호출] ← publisher와 병렬 실행 가능
   핵심 아젠다 선별 → 회의록 초안 + Slack 요약 생성
   결과:
     ├─ output/meeting_minutes_{YYYYMMDD}.md  (회의록 마크다운)
     ├─ Google Docs 회의록 초안 URL
     └─ output/slack_summary_{YYYYMMDD}.txt  (Slack 공유용 텍스트)
    │
    ▼
[Step 4: Self-Validation]
   Flash Report + 회의록 + Slack 요약 산출물 완비 여부 확인
    │
    ├─ 통과 → 완료 출력
    └─ 실패 → 해당 단계 재호출 (최대 2회)
```

### 중간 산출물 위치

| 파일 | 생성 주체 | 용도 |
|------|---------|------|
| `output/analysed_report.json` | analyst | 분류·우선순위 결과 캐시 (agenda_items·slack_short_summary 포함) |
| `output/flash_{YYYYMMDD}.md` | publisher | 로컬 Flash Report 마크다운 최종본 |
| `output/meeting_minutes_{YYYYMMDD}.md` | minutes-generator | 회의록 초안 마크다운 |
| `output/slack_summary_{YYYYMMDD}.txt` | minutes-generator | Slack 사전 아젠다 요약 텍스트 |
| `input/memo_{YYYYMMDD}.txt` | orchestrator | 사용자 메모 임시 저장 |

---

## 3. 서브에이전트 호출 규약

### analyst 호출

```
Task: 아래 Jira 데이터와 사용자 메모를 분석하여 Weekly Flash 항목으로 분류하고 우선순위를 판단해줘.
에이전트 스펙: .claude/agents/analyst/AGENT.md 참조

입력:
  - Jira 원시 데이터: [jira-parser 스킬 반환값 또는 파일 경로]
  - 사용자 메모: input/memo_{YYYYMMDD}.txt

출력: output/analysed_report.json
```

### publisher 호출

```
Task: 아래 분석 결과를 3가지 포맷(Markdown, Google Docs, Gmail)으로 변환하고
각 채널의 API 초안을 생성해줘.
에이전트 스펙: .claude/agents/publisher/AGENT.md 참조

입력: output/analysed_report.json
출력:
  - output/flash_{YYYYMMDD}.md
  - Google Docs 초안 URL
  - Gmail 초안 ID
```

### minutes-generator 호출

```
Task: 아래 분석 결과에서 핵심 아젠다를 선별하고
Google Docs 회의록 초안과 Slack 사전 아젠다 요약을 생성해줘.
에이전트 스펙: .claude/agents/minutes-generator/AGENT.md 참조

입력: output/analysed_report.json
출력:
  - output/meeting_minutes_{YYYYMMDD}.md
  - Google Docs 회의록 초안 URL
  - output/slack_summary_{YYYYMMDD}.txt
```

> **병렬 실행 허용**: publisher와 minutes-generator는 동일한 `analysed_report.json`을 읽으므로
> analyst 완료 후 두 에이전트를 동시에 호출할 수 있다.

### jira-parser 스킬 호출

```bash
python3 .claude/skills/jira-parser/scripts/parse_jira.py \
  --project {PROJECT_KEY} \
  --week-offset 0 \
  --output output/jira_raw_{YYYYMMDD}.json
```

---

## 4. 문서 작성 원칙 (Writing Rules)

Flash Report 작성 시 아래 원칙을 반드시 준수한다.

### WR-1: 문서 최상단에 Health Status 표기

Executive Summary 바로 위 또는 안에 전체 프로젝트 상태를 한 줄로 표시한다.

```
| 전체 상태 | 🟢 정상 진행 | 계획 대비 차질 없음 |
| 전체 상태 | 🟡 주의 필요 | {1줄 이유} |
| 전체 상태 | 🔴 긴급 대응 필요 | {1줄 이유} |
```

판단 기준:
- 🟢 Green: 계획 일정 내 진행 중, 블로커 없음
- 🟡 Yellow: 일정 지연 위험 또는 해결 중인 이슈 존재
- 🔴 Red: 블로커로 인해 일정 영향 확실, 즉각 의사결정 필요

### WR-2: Task 완료율은 반드시 맥락과 함께 표기

단순 퍼센트만 쓰지 않는다. 현재 완료 수 + 차주 예상 완료 수를 함께 표기한다:

```
현재: {N}개 중 {n}개 완료 ({%}) — {현재 Phase 기준 진행 상태 한 줄}
차주 예상: {n+x}개 완료 (+{x}개) — {완료 예정 Task 목록 간략 서술}
```

차주 예상 완료 수 산출 방법:
1. "진행 중" Task 중 Due가 차주 내인 것 → 완료로 카운트
2. "Next Week" 계획 중 완료가 확정적인 마일스톤 Task → 완료로 카운트
3. "Not Started"였으나 이미 실행된 Task → 완료로 카운트

예시:
> 현재: 38개 중 24개 완료 (63.2%) — Phase 3까지 예정 Task 모두 완료, 현재 지연 없음
> 차주 예상: 28개 완료 (+4개) — 대시보드 설정 완료, Phase 3.5 런칭 Task 3건(1% 런칭·기대치 정렬·Full Ramp) 완료 예정

### WR-3: 이슈·블로커는 "누가 / 언제까지 / 무엇을" 형식으로 작성

- 섹션명은 "Blocks/리스크" 대신 **"이슈 & 조치 사항"** 으로 표기
- "영향도 중/고/저" 같은 내부 용어 사용 금지
- 각 항목은 반드시 담당자 + 기한 + 구체적 액션을 명시

```
| 이슈 | 현재 상태 | 필요 조치 | 담당 | 기한 |
```

예시:
> | 프로모션 일정 미공유 | Auxia가 향후 프로모 일정을 모름 → 모델 최적화 불가 | 주간 미팅 전 프로모 캘린더 공유 | 무신사 마케팅팀 | 매주 월요일 |

### WR-5: 진행 중 Task에 차주 예상 진척률 표기

"진행 중" 항목은 예상 Due를 기반으로 차주 말 기준 진척률을 함께 표시한다.

```
| 항목 | 담당 | 예상 Due | 차주 예상 진척 |
|------|------|---------|--------------|
| {Task명} | {담당} | {날짜 또는 "TBD"} | {%} — {한 줄 근거} |
```

진척률 판단 기준:
- Due가 차주 내: 완료 예상 → **100%**
- Due가 2주 이후: 착수 또는 일부 완료 → Due까지 남은 기간 대비 비율로 추정
- Due 불명확: "착수 예정" 또는 "진행 중 (Due TBD)"으로 표기

예시:
> | 대시보드 설정 | Charles/Jae | 3/7 (EOW) | **100%** — 이번 주 내 완료 예정, 차주 Walk-through 진행 |
> | In-App SDK 통합 개발 | Kyungmin | 3/9 시작 → 3/20 테스트 | **20%** — 차주 개발 착수, 테스트는 3/20까지 |

---

### WR-4: 맥락 없이 등장하는 섹션 금지

새로운 섹션(채널 전략, 실험 설계 등)을 추가할 때는 반드시 첫 줄에 **왜 이 내용이 이 문서에 있는지** 한 문장으로 설명한다.

예시:
> *(이번 주 정기 미팅에서 채널별 역할이 처음 정의됨. 향후 운영 기준으로 활용할 내용이므로 기록함.)*

---

## 5. Self-Validation 체크리스트

| # | 검증 항목 | 통과 기준 | 재호출 대상 |
|---|----------|----------|------------|
| 1 | 산출물 3종 완비 (Flash) | MD + Docs URL + Gmail ID 모두 존재 | publisher |
| 2 | 핵심 수치 볼드 처리 | `**숫자**` 패턴 MD 파일 내 1개 이상 | publisher |
| 3 | 명사형 종결 어미 | 메일 본문 문장이 `~함`, `~완료`, `~예정`으로 종결 | publisher |
| 4 | 카테고리 4종 완비 | Achievements / Status / Next Week / 이슈&조치 섹션 모두 존재 | analyst |
| 5 | 우선 항목 존재 | `⭐ 핵심` 태그 항목이 1개 이상 | analyst |
| 6 | Health Status 표기 | 🟢/🟡/🔴 + 판단 근거 1줄 존재 | publisher |
| 7 | Task 완료 현황 — 현재+차주 형식 | "현재 N개 완료 / 차주 예상 N+x개" 양식으로 표기됨 | analyst |
| 8 | 진행 중 Task — 차주 진척률 표기 | 진행 중 항목에 예상 Due + 차주 예상 % 존재 | analyst |
| 9 | 이슈 섹션 — 담당/기한/액션 완비 | 이슈 항목마다 담당자·기한·구체 액션 3개 필드 존재 | analyst |
| 10 | 회의록 산출물 완비 | meeting_minutes MD + Docs URL 존재 | minutes-generator |
| 11 | Slack 요약 완비 | slack_summary txt 파일 존재 + 200자 이내 | minutes-generator |
| 12 | 아젠다 항목 존재 | agenda_items 배열에 1개 이상 존재 | minutes-generator |

2회 재시도 후 실패한 항목은 `[TBD]`로 표시하고 터미널에 에러 로그를 출력한다.

---

## 5. 완료 출력 형식

```
✅ Weekly Flash Report + 회의록 생성 완료!

[Flash Report]
📄 Markdown: output/flash_{YYYYMMDD}.md
📝 Google Docs: {Flash Docs URL}
📧 Gmail 초안: {Draft ID}

[Meeting Minutes]
📋 Markdown: output/meeting_minutes_{YYYYMMDD}.md
📝 Google Docs (회의록): {Minutes Docs URL}
💬 Slack 요약: output/slack_summary_{YYYYMMDD}.txt

---
검증 결과:
✅ Flash 산출물 3종 완비   ✅ 핵심 수치 볼드
✅ 명사형 종결 어미        ✅ 카테고리 4종 완비
✅ 우선 항목 존재          ✅ 회의록 산출물 완비
✅ Slack 요약 완비         ✅ 아젠다 항목 존재

⭐ 핵심 성과 (상위 3건):
1. {티켓 ID} — {제목}
2. {티켓 ID} — {제목}
3. {티켓 ID} — {제목}

📢 Slack 아젠다 미리보기:
{slack_summary 첫 4줄}
```

---

## 6. 오류 처리

| 오류 유형 | 처리 방법 |
|----------|----------|
| Jira API 인증 실패 (401) | "JIRA_API_TOKEN 환경변수를 확인해주세요." 후 중단 |
| Jira 티켓 0건 | "이번 주 처리된 티켓이 없습니다. 날짜 범위를 확인할까요?" |
| Google Docs API 실패 | 해당 단계 스킵, MD 파일 경로 안내 후 계속 진행 |
| Gmail API 실패 | 해당 단계 스킵, 본문 텍스트를 터미널에 출력 |
| publisher 2회 실패 | `output/flash_{YYYYMMDD}.md` 경로 안내 + 수동 복사 안내 |
| Google Docs API 실패 (회의록) | 해당 단계 스킵, MD 파일 경로 안내 후 계속 진행 |
| Slack Webhook 실패 | 터미널에 요약 텍스트 출력 + `output/slack_summary_{YYYYMMDD}.txt` 경로 안내 |
| minutes-generator 2회 실패 | `output/meeting_minutes_{YYYYMMDD}.md` 경로 안내 + 수동 업로드 안내 |
