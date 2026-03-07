# PM Studio — Skill Reference

이 저장소에서 사용할 수 있는 모든 기술(스킬)을 정리한 레퍼런스입니다.

---

## 슬래시 커맨드 스킬 (/ Skills)

Claude Code에서 `/커맨드` 형태로 직접 호출하는 에이전트 스킬.

| 커맨드 | 위치 | 핵심 기능 | 주요 입력 | 주요 출력 |
|--------|------|----------|---------|---------|
| `/discovery` | `.claude/skills/discovery/` | 시장 탐색 + 가상 인터뷰 + 디스커버리 보고서 | 탐색 주제 + `--ref` 옵션 | `output/FINAL-DISCOVERY-REPORT.md` |
| `/prd` | `.claude/skills/prd/` | Rough Note → PRD + Red Team + Confluence 업로드 | Rough Note 또는 이니셔티브 ID | `prd-agent-system/output/prd_*.md` |
| `/red` | `.claude/skills/red/` | PRD 단독 Red Team 검증 | PRD 파일 경로 | `prd-agent-system/output/redteam_*.md` |
| `/epic` | `.claude/skills/epic/` | PRD → 직무별 에픽 분해 + Jira 티켓 자동 생성 | PRD URL 또는 .md + Jira 이니셔티브 키 | Confluence Draft + Jira 에픽 티켓 N개 |
| `/jira` | `.claude/skills/jira/` | 자연어 → Jira 티켓 일괄 생성 | 요청 내용 + 참조 티켓 (선택) | `output/created_{이니셔티브}_tickets.json` |
| `/gtm` | `.claude/skills/gtm/` | PRD → GTM 브리프 생성 | `gtm-agent-system/input/prd_*.md` | `gtm-agent-system/output/GTM_Brief_*.md` |
| `/report` | `.claude/skills/report/` | C레벨 보고서 품질 검토 + 종합 판정 | 보고서 파일 또는 Confluence URL | `report-agent-system/output/report_review_*.md` |
| `/pgm` | `.claude/skills/pgm/` | Jira + 메모 → 주간 보고서 + 회의록 + Slack 요약 | Jira 프로젝트 키 + 메모 텍스트 | `pgm-agent-system/output/flash_*.md` 외 5종 |
| `/mail` | `.claude/skills/mail/` | Confluence / MD → Gmail 발송 | Confluence URL 또는 .md 파일 경로 + 수신자 | `output/send_log.json` |

---

## 유틸리티 스킬 (Utility Skills)

슬래시 커맨드 없이 에이전트가 내부적으로 호출하는 스크립트 기반 스킬.

### confluence-tool
**위치:** `.claude/skills/confluence-tool/`
**역할:** Confluence REST API 공통 클라이언트

| 스크립트 | 기능 | 주요 옵션 |
|---------|------|---------|
| `scripts/search.py` | Confluence 검색 | `--query`, `--space`, `--limit`, `--list-spaces` |
| `scripts/upload.py` | 페이지 생성/업데이트 | `--title`, `--space`, `--parent-id`, `--draft` |
| `scripts/fetch_page.py` | 페이지 전체 내용 조회 | `--page-id`, `--format (storage|markdown)` |

**필수 환경변수:**
```bash
CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, CONFLUENCE_SPACE_KEY
```

---

### gmail-tool
**위치:** `.claude/skills/gmail-tool/`
**역할:** Gmail SMTP 발송 + HTML 변환

| 스크립트 | 기능 | 입력 |
|---------|------|------|
| `scripts/xhtml_to_email_html.py` | Confluence XHTML → 이메일 HTML | `--input source_page.xhtml` (우선) |
| `scripts/md_to_html.py` | 마크다운 → 이메일 HTML | `--input *.md` (fallback) |
| `scripts/send_email.py` | Gmail SMTP 발송 | `--to`, `--subject`, `--html-file` |

**필수 환경변수:**
```bash
GMAIL_USER="your@gmail.com"
GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"   # Gmail 앱 비밀번호
```

---

### jira-parser (pgm-agent-system)
**위치:** `pgm-agent-system/.claude/skills/jira-parser/`
**역할:** Jira API에서 이번 주 티켓 수집

```bash
python3 .claude/skills/jira-parser/scripts/parse_jira.py \
  --project {PROJECT_KEY} \
  --week-offset 0 \
  --output output/jira_raw_{YYYYMMDD}.json
```

**필수 환경변수:** `JIRA_API_TOKEN`, `CONFLUENCE_EMAIL`

---

### google-api-handler (pgm-agent-system)
**위치:** `pgm-agent-system/.claude/skills/google-api-handler/`
**역할:** Google Docs 생성/업데이트 + Gmail 초안 생성

```bash
python3 .claude/skills/google-api-handler/scripts/upsert_google_doc.py \
  --title "문서 제목" \
  --content output/flash_{YYYYMMDD}.md \
  --folder-id ${GOOGLE_DRIVE_FOLDER_ID}
```

**필수 환경변수:** `GOOGLE_CREDENTIALS_JSON`

---

### slack-notifier (pgm-agent-system)
**위치:** `pgm-agent-system/.claude/skills/slack-notifier/`
**역할:** Slack Webhook 전송 또는 터미널 출력 (dry-run)

```bash
python3 .claude/skills/slack-notifier/scripts/send_slack.py \
  --input output/slack_summary_{YYYYMMDD}.txt \
  [--dry-run]
```

**선택 환경변수:** `SLACK_WEBHOOK_URL` (미설정 시 터미널 출력 모드)

---

### file-generator (pgm-agent-system)
**위치:** `pgm-agent-system/.claude/skills/file-generator/`
**역할:** Markdown 파일 생성 (flash, minutes 등)

---

## 시스템별 스킬 연계 구조

```
/discovery ─────────────────── (자체 완결)
/prd ──────────────────────── confluence-tool (업로드)
/red ──────────────────────── (자체 완결)
/epic ─────────────────────── confluence-tool + Jira REST API
/jira ─────────────────────── Jira REST API (직접 스크립트)
/gtm ──────────────────────── (자체 완결)
/report ───────────────────── confluence-tool (업로드)
/pgm ──────────────────────── jira-parser + google-api-handler + slack-notifier + file-generator
/mail ─────────────────────── confluence-tool (fetch) + gmail-tool (변환·발송)
자연어 조회/업로드 ────────── confluence-tool
```

---

## 환경변수 전체 목록

| 변수명 | 용도 | 필수 여부 |
|--------|------|---------|
| `CONFLUENCE_URL` | Confluence 베이스 URL | 필수 |
| `CONFLUENCE_EMAIL` | Atlassian 계정 이메일 | 필수 |
| `CONFLUENCE_API_TOKEN` | Atlassian API 토큰 | 필수 |
| `CONFLUENCE_SPACE_KEY` | 기본 업로드 Space 키 | 필수 |
| `CONFLUENCE_PARENT_PAGE_ID` | 하위 페이지 생성 시 부모 페이지 ID | 선택 |
| `GITHUB_TOKEN` | PDIS 외부 레퍼런스 수집 Rate Limit 방지 | 선택 |
| `JIRA_API_TOKEN` | Jira API 인증 | /pgm, /epic, /jira 사용 시 필수 |
| `JIRA_PROJECT_KEY` | 기본 Jira 프로젝트 키 | 선택 |
| `GOOGLE_CREDENTIALS_JSON` | Google Docs·Gmail OAuth 인증 | /pgm 사용 시 필수 |
| `GOOGLE_DRIVE_FOLDER_ID` | Google Docs 저장 폴더 | 선택 |
| `GMAIL_USER` | 발신 Gmail 주소 | /mail 사용 시 필수 |
| `GMAIL_APP_PASSWORD` | Gmail 앱 비밀번호 (16자리) | /mail 사용 시 필수 |
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL | /pgm Slack 전송 시 필수 |

---

> 스킬 추가 방법: `.claude/skills/{스킬명}/SKILL.md` 생성 후 Claude Code 재시작 시 자동 등록
