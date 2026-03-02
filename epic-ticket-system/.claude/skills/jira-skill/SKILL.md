# Jira Skill — 이슈 조회 및 에픽 생성 규약

## 개요

Jira REST API v3를 통해 이니셔티브 메타데이터를 조회하고,
에픽 티켓을 자동 생성하는 스킬.

**모든 Jira API 호출은 이 스킬의 스크립트를 통해서만 수행한다.**

---

## 환경변수 요구사항

| 변수 | 설명 | 공유 여부 |
|------|------|---------|
| `CONFLUENCE_URL` | Atlassian 도메인 (Jira 공용) | Confluence와 동일 |
| `CONFLUENCE_EMAIL` | Atlassian 계정 이메일 | Confluence와 동일 |
| `CONFLUENCE_API_TOKEN` | Atlassian API 토큰 | Confluence와 동일 |
| `JIRA_PROJECT_KEY` | 에픽 생성 대상 프로젝트 키 (예: TM) | **별도 설정 필요** |

```bash
export JIRA_PROJECT_KEY="TM"
```

> Jira와 Confluence는 동일한 Atlassian 계정/토큰을 공유하므로
> 추가 인증 설정 없이 기존 Confluence 환경변수를 사용한다.

---

## 스크립트 목록

| 스크립트 | 역할 |
|---------|------|
| `scripts/client.py` | Jira REST API 공통 클라이언트 (인증, HTTP, 재시도) |
| `scripts/fetch_initiative.py` | 이니셔티브 이슈에서 라벨·컴포넌트·프로젝트 추출 |
| `scripts/create_tickets.py` | epic_spec.json 기반 에픽 티켓 일괄 생성 |

---

## 1. fetch_initiative.py 사용법

```bash
cd /Users/musinsa/Documents/agent_project/pm-studio && \
python3 epic-ticket-system/.claude/skills/jira-skill/scripts/fetch_initiative.py \
  --issue-key TM-2061 \
  --output epic-ticket-system/output/initiative_meta.json
```

출력 (initiative_meta.json):
```json
{
  "issue_key": "TM-2061",
  "project_key": "TM",
  "summary": "Campaign Meta Engine Phase 1",
  "labels": ["membership", "campaign", "2026Q1"],
  "components": ["Backend", "Frontend"],
  "fix_versions": ["2026 Q1"],
  "priority": "High"
}
```

---

## 2. create_tickets.py 사용법

```bash
cd /Users/musinsa/Documents/agent_project/pm-studio && \
python3 epic-ticket-system/.claude/skills/jira-skill/scripts/create_tickets.py \
  --spec epic-ticket-system/output/epic_spec_{YYYYMMDD}_{주제}.json \
  --meta epic-ticket-system/output/initiative_meta.json \
  --output epic-ticket-system/output/jira_result_{YYYYMMDD}_{주제}.json
```

출력 (jira_result.json):
```json
{
  "created": [
    {
      "role": "BE",
      "title": "[BE] Campaign Asset API 개발",
      "issue_key": "TM-2135",
      "url": "https://musinsa-oneteam.atlassian.net/browse/TM-2135"
    }
  ],
  "failed": []
}
```

---

## 3. Jira 티켓 생성 규칙

### 라벨 상속 정책

```
최종 라벨 = 부모 이니셔티브 라벨 (100% 상속) + 직무 라벨 추가
예) 이니셔티브 라벨: ["membership", "campaign"]
    BE 에픽 라벨:    ["membership", "campaign", "backend"]
    FE 에픽 라벨:    ["membership", "campaign", "frontend"]
    MLE 에픽 라벨:   ["membership", "campaign", "mle"]
    DS 에픽 라벨:    ["membership", "campaign", "data-science"]
```

### 우선순위 매핑

| epic_spec.json 값 | Jira 우선순위 |
|-----------------|-------------|
| Highest | Highest |
| High | High |
| Medium | Medium |
| Low | Low |

### 날짜 필드

| 필드 | Jira 필드명 |
|------|-----------|
| Start Date | `customfield_10015` (Start date) |
| Due Date | `duedate` |

---

## 4. 오류 처리

| 오류 | 처리 방법 |
|------|---------|
| 401 Unauthorized | "Atlassian API 토큰을 확인해주세요." 출력 후 중단 |
| 404 이슈 없음 | "이니셔티브 키가 올바른지 확인해주세요." 출력 후 중단 |
| 티켓 생성 실패 (일부) | 성공 티켓 먼저 출력, 실패 항목 jira_result.json의 failed에 기록 |
| JIRA_PROJECT_KEY 미설정 | 명확한 오류 메시지 출력 후 중단 |
