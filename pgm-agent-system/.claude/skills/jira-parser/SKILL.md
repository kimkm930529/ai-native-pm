# jira-parser — Skill Spec

## 역할

Jira REST API를 호출하여 지정된 프로젝트의 이번 주 티켓을 수집하고
구조화된 JSON으로 변환하여 저장한다.

## 환경변수 (필수)

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `JIRA_BASE_URL` | Jira 인스턴스 URL | `https://yourcompany.atlassian.net` |
| `JIRA_USER_EMAIL` | Jira 계정 이메일 | `user@company.com` |
| `JIRA_API_TOKEN` | Jira API Token | Atlassian → 계정 → API Token에서 발급 |

## 호출 방법

```bash
python3 .claude/skills/jira-parser/scripts/parse_jira.py \
  --project {PROJECT_KEY} \
  --week-offset 0 \
  --output output/jira_raw_{YYYYMMDD}.json
```

### 파라미터

| 파라미터 | 기본값 | 설명 |
|---------|-------|------|
| `--project` | 필수 | Jira 프로젝트 키 (예: MATCH, CME) |
| `--week-offset` | `0` | 0=이번 주, -1=지난 주 |
| `--output` | `output/jira_raw_{today}.json` | 저장 경로 |
| `--include-status` | `Done,In Progress,In Review,Testing,Blocked` | 포함할 상태 필터 |

## 출력 스키마

`output/jira_raw_{YYYYMMDD}.json`:

```json
{
  "fetched_at": "2026-03-05T10:00:00",
  "project": "MATCH",
  "week_range": { "start": "2026-03-02", "end": "2026-03-05" },
  "issues": [
    {
      "key": "MATCH-123",
      "summary": "티켓 제목",
      "status": { "name": "Done" },
      "priority": { "name": "High" },
      "story_points": 5,
      "assignee": "홍길동",
      "resolved": "2026-03-04T15:00:00",
      "labels": ["weekly-flash", "okr"],
      "flagged": false,
      "linked_issues": [
        { "key": "MATCH-100", "type": "is blocked by" }
      ],
      "sprint": {
        "name": "Sprint 12",
        "start_date": "2026-02-23",
        "end_date": "2026-03-08"
      }
    }
  ],
  "total": 12
}
```
