# Weekly Flash Report — Main Orchestrator (CLAUDE.md)

## 역할

Jira 티켓과 사용자 메모를 결합하여 핵심 성과 위주의 Weekly Flash Report를 생성하고,
Markdown / Gmail 초안 / Google Docs 초안 3가지 포맷으로 자동 배포(초안)하는 오케스트레이터.

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
[Step 4: Self-Validation]
   볼드 처리 확인 / 명사형 어미 확인 / 산출물 3종 완비 여부
    │
    ├─ 통과 → 완료 출력
    └─ 실패 → 해당 단계 재호출 (최대 2회)
```

### 중간 산출물 위치

| 파일 | 생성 주체 | 용도 |
|------|---------|------|
| `output/analysed_report.json` | analyst | 분류·우선순위 결과 캐시 |
| `output/flash_{YYYYMMDD}.md` | publisher | 로컬 마크다운 최종본 |
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

### jira-parser 스킬 호출

```bash
python3 .claude/skills/jira-parser/scripts/parse_jira.py \
  --project {PROJECT_KEY} \
  --week-offset 0 \
  --output output/jira_raw_{YYYYMMDD}.json
```

---

## 4. Self-Validation 체크리스트

| # | 검증 항목 | 통과 기준 | 재호출 대상 |
|---|----------|----------|------------|
| 1 | 산출물 3종 완비 | MD + Docs URL + Gmail ID 모두 존재 | publisher |
| 2 | 핵심 수치 볼드 처리 | `**숫자**` 패턴 MD 파일 내 1개 이상 | publisher |
| 3 | 명사형 종결 어미 | 메일 본문 문장이 `~함`, `~완료`, `~예정`으로 종결 | publisher |
| 4 | 카테고리 4종 완비 | Achievements / Status / Next Week / Blocks 섹션 모두 존재 | analyst |
| 5 | 우선 항목 존재 | `⭐ 핵심` 태그 항목이 1개 이상 | analyst |

2회 재시도 후 실패한 항목은 `[TBD]`로 표시하고 터미널에 에러 로그를 출력한다.

---

## 5. 완료 출력 형식

```
✅ Weekly Flash Report 생성 완료!

📄 Markdown: output/flash_{YYYYMMDD}.md
📝 Google Docs: {Docs URL}
📧 Gmail 초안: {Draft ID}

---
검증 결과:
✅ 산출물 3종 완비     ✅ 핵심 수치 볼드
✅ 명사형 종결 어미    ✅ 카테고리 4종 완비
✅ 우선 항목 존재

⭐ 핵심 성과 (상위 3건):
1. {티켓 ID} — {제목}
2. {티켓 ID} — {제목}
3. {티켓 ID} — {제목}
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
