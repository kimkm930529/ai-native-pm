# Slack 대화 조회 · 챗봇 시스템

## 역할
Slack Web API를 통해 채널 대화를 수집·요약하고, AI 챗봇 인터페이스를 제공하는 시스템.
`/slack` 스킬로 호출된다.

> 공통 규약: `../CONVENTIONS.md` | 역량 맵: `../CAPABILITY_MAP.md`

---

## 실행 모드

| 모드 | 트리거 | 출력 |
|------|--------|------|
| **read** | `--today` / `--week` / `--date` | 대화 요약 리포트 |
| **search** | `--search "[키워드]"` | 검색 결과 목록 |
| **send** | `--send "[메시지]"` | Slack 발송 (컨펌 필수) |

---

## Step 0: 연결 확인

```bash
python3 scripts/client.py --check
```

- `SLACK_BOT_TOKEN` 없으면 → 설정 가이드 출력 후 중단

### 연결 설정 가이드 (연동 필요)
```
1. https://api.slack.com/apps → Create New App → From Scratch
2. OAuth & Permissions → Bot Token Scopes 추가:
   - channels:history   (채널 메시지 읽기)
   - channels:read      (채널 목록 조회)
   - users:read         (사용자 이름 조회)
   - chat:write         (메시지 발송, --send 옵션 사용 시)
3. Install App to Workspace → Bot User OAuth Token 복사
4. .env에 추가:
   SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxx
   SLACK_DEFAULT_CHANNEL=general
5. Bot을 읽고 싶은 채널에 /invite @봇이름 으로 초대

6. (선택) MCP 서버 방식:
   - Composio, Zapier MCP 등 Slack MCP 서버 연결 시
   - Claude가 자연어로 Slack 채널 직접 조회 가능
```

---

## Step 1: read 모드 — 대화 수집 + 요약

**목적**: 지정한 채널의 특정 기간 대화를 수집하고 PM 관점으로 요약

**처리 흐름**:
1. 채널 ID 확인 (`python3 scripts/client.py --channel-id {channel_name}`)
2. 메시지 수집 (`python3 scripts/client.py --fetch --channel {channel_id} --oldest {ts} --latest {ts}`)
3. 사용자 이름 해석 (user_id → display_name)
4. `conversation-summarizer` 에이전트 → 대화 요약
5. 이니셔티브 연결 시 → 관련 의사결정 항목 추출

**날짜 변환**:
- `--today` → 오늘 00:00:00 ~ 현재
- `--week` → 이번 주 월요일 00:00:00 ~ 현재
- `--date YYYY-MM-DD` → 해당 날 00:00:00 ~ 23:59:59

**서브에이전트**: `.claude/agents/slack-reader/AGENT.md` → `.claude/agents/conversation-summarizer/AGENT.md`

**출력 파일**: `output/slack_{YYYYMMDD}_{channel}_{mode}.md`

**요약 구조**:
```
## Slack 요약: #{채널} — {날짜/기간}
## 대화 개요
(참여자 N명, 메시지 N건, 주요 스레드 N개)
## 핵심 논의 주제
### 1. {주제}
(대화 흐름 요약 + 결론)
## 결정 사항
- [명시적 합의 또는 결정]
## Action Item
- [@담당자] [할 일] (기한 있으면 포함)
## 미해결 항목
- [답변 없이 끝난 질문 또는 논쟁]
```

---

## Step 2: search 모드 — 키워드 검색

**목적**: 채널 내 특정 키워드 포함 메시지 검색

```bash
python3 scripts/client.py --search "[키워드]" --channel {channel_id} [--limit 50]
```

**출력**: 검색 결과 목록 (날짜, 작성자, 메시지 미리보기, 스레드 링크)

---

## Step 3: send 모드 — 메시지 발송

**주의**: 발송 전 반드시 사용자 컨펌 (되돌리기 불가)

**처리 흐름**:
1. 발송 내용 미리보기 출력 (채널, 메시지 내용)
2. 사용자 승인 후 실행
3. `python3 scripts/client.py --send --channel {channel_id} --message "[내용]"`

**컨펌 형식**:
```
📤 발송 예정:
- 채널: #{channel}
- 메시지: {message}

발송하시겠습니까? (Y/N)
```

---

## /pgm 파이프라인 연동

`/pgm --full` 실행 시 Slack 요약이 자동으로 포함될 수 있음:
- `pgm-agent-system/.claude/skills/slack-notifier/` → Flash Report 발송
- `/slack --week #match-pm` → `pgm-agent-system/output/slack_summary_{YYYYMMDD}.txt` 보완

---

## 오류 처리

| 오류 | 처리 |
|------|------|
| 환경변수 미설정 | 연결 가이드 출력 후 중단 |
| Bot 미초대 채널 | 해당 채널 skip + 초대 방법 안내 |
| API Rate Limit (429) | 1초 대기 후 자동 재시도 (최대 3회) |
| 채널 없음 | 유사 채널명 제안 |
| 발송 미승인 | 즉시 중단, 발송하지 않음 |

---

## 출력 파일 명명 규칙

| 모드 | 파일명 |
|------|--------|
| read (today) | `output/slack_{YYYYMMDD}_{channel}_today.md` |
| read (week) | `output/slack_{YYYYMMDD}_{channel}_week.md` |
| search | `output/slack_{YYYYMMDD}_{channel}_search_{keyword}.md` |
