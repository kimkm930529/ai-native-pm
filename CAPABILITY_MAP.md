# CAPABILITY_MAP — 팀별 역량 맵

> 비서실장이 역량 점검 시 참조하는 문서.
> 각 팀의 역할, 트리거, 입력/출력, 호출 방법을 정의한다.
> 마지막 업데이트: 2026-03-08

---

## 팀 구성 개요

```
pm-studio
├── [기획팀]        PRD 작성 · Red Team 검증 · Epic 분해
├── [마케팅팀]      GTM 브리프 작성
├── [PGM팀]        Weekly Flash · C레벨 보고서 검토
├── [디스커버리팀]  시장/제품 Discovery 분석
├── [지식팀]        Confluence & Notion 조회/저장
├── [커뮤니케이션팀] 이메일 발송 · Jira 티켓
└── [회고팀]        주간 작업 로그
```

---

## [기획팀] PRD / 검증 / 에픽

### 역할
기능 기획서 작성부터 Jira 실행 준비까지의 전체 기획 파이프라인을 담당한다.

### 팀원 구성
| 역할 | 호출 방법 | 모델 |
|------|----------|------|
| PRD 작성 | Skill: `/prd` | claude-sonnet-4-6 |
| Red Team 검증 | Skill: `/red` | claude-sonnet-4-6 |
| Epic 분해 + Jira 등록 | Skill: `/epic` | claude-sonnet-4-6 |

### 트리거 키워드
PRD, 기능 기획, 요구사항, 제품 명세, Red Team, 가정 검증, 반론, Epic, 에픽, 티켓 분해, 스코프

### 세부 역량

#### PRD 작성 (`/prd`)
- **입력**: 이니셔티브 ID(TM-XXXX) 또는 rough note 텍스트
- **출력**: `prd-agent-system/output/prd_{YYYYMMDD}_{주제}.md`
- **특징**: TM-XXXX 입력 시 이니셔티브 KB 자동 로드, 이니셔티브 output/ 폴더에도 저장
- **실행**: `prd-agent-system/CLAUDE.md` 워크플로우 따름

#### Red Team 검증 (`/red`)
- **입력**: PRD 파일 경로 또는 Confluence URL
- **출력**: `prd-agent-system/output/redteam_{YYYYMMDD}_{주제}.md`
- **특징**: 9카테고리 반론 질문 생성, Critical/Important/Minor 우선순위 태깅
- **의존**: PRD 파일 필요 (없으면 confluence-reader로 검색)

#### Epic 분해 + Jira 등록 (`/epic`)
- **입력**: PRD 파일 경로 또는 Confluence URL + 이니셔티브 키(TM-XXXX)
- **출력**: Jira 에픽·태스크 티켓 (PSN 프로젝트)
- **특징**: 계층 구조 자동 설계, 반드시 사용자 컨펌 후 실행
- **실행**: `epic-ticket-system/CLAUDE.md` 워크플로우 따름

### 팀 내 표준 파이프라인
```
/prd → /red → /epic
```

---

## [마케팅팀] GTM

### 역할
PRD를 받아 마케팅 실행 전략과 커뮤니케이션 메시지를 담은 GTM 브리프를 생성한다.

### 팀원 구성
| 역할 | 호출 방법 | 모델 |
|------|----------|------|
| GTM 오케스트레이터 | Skill: `/gtm` | claude-sonnet-4-6 |
| 메시지 설계 | Agent: `message-architect` (gtm-agent-system 내) | claude-haiku-4-5 |
| 채널 전략 | Agent: `channel-planner` (gtm-agent-system 내) | claude-haiku-4-5 |

### 트리거 키워드
GTM, Go-to-Market, 출시 전략, 마케팅 브리프, 커뮤니케이션 메시지, 런치, One-liner, 채널 전략, 스테이크홀더 맵

### 세부 역량

#### GTM 브리프 작성 (`/gtm`)
- **입력**: PRD 파일 경로 (없으면 `gtm-agent-system/input/` 자동 탐지)
- **출력**: `gtm-agent-system/output/GTM_Brief_{YYYYMMDD}_{주제}.md`
- **특징**: Internal(사내 시스템) / External(출시 제품) 자동 감지 후 맞춤 섹션 생성
  - Internal: 8개 섹션 (One-liner, Target User, Before/After, Key Message, Scope, Stakeholder Map, Rollout, Metrics)
  - External: 9개 섹션 (+ Competitive Positioning, Pricing & Distribution, Promotion Plan)
- **검증**: 섹션 완비 자동 검증, 실패 시 2회 재시도

### 의존 관계
PRD가 있어야 실행 가능. PRD 없으면 기획팀 먼저 호출.

---

## [PGM팀] PM Command Center

### 역할
PM의 주간 업무 전반을 담당하는 통합 허브.
Jira 성과 분석, 회의록 처리, Initiative 코멘트 게시, 보고서 배포, 과제 분류를 단일 파이프라인으로 연결한다.

### 팀원 구성
| 역할 | 호출 방법 | 모델 |
|------|----------|------|
| PGM Command Center (통합) | Skill: `/pgm` | claude-sonnet-4-6 |
| Weekly Flash 생성 | Skill: `/pgm [JIRA_KEY]` | claude-sonnet-4-6 |
| 회의록 → Jira 코멘트 | Skill: `/pgm --weekly [URL]` | claude-sonnet-4-6 |
| Flash + 회의록 + 코멘트 통합 | Skill: `/pgm --full [KEY] [URL]` | claude-sonnet-4-6 |
| C레벨 보고서 검토 | Skill: `/report` | claude-sonnet-4-6 |
| 과제 검토 (MATCH 분류) | Skill: `/ticket-review` | claude-sonnet-4-6 |

### 트리거 키워드
Weekly Flash, 주간 보고, 성과 정리, KPI, 이번 주 결과, 회의록, 미팅 정리, Jira 업데이트,
보고서 검토, C레벨, 결재, 과제 검토, 티켓 분류, MATCH 과제

### 세부 역량

#### PGM 통합 실행 (`/pgm --full`)
- **입력**: Jira 프로젝트 키 + Confluence 회의록 URL + 선택적 메모
- **출력**:
  - `pgm-agent-system/output/flash_{YYYYMMDD}.md` + Google Docs + Gmail
  - `pgm-agent-system/output/meeting_minutes_{YYYYMMDD}.md` + Google Docs
  - `pgm-agent-system/output/slack_summary_{YYYYMMDD}.txt`
  - `pgm-agent-system/output/weekly_draft_{YYYYMMDD}.json`
  - Jira Initiative별 Weekly 코멘트 게시
  - `pgm-agent-system/output/_artifacts.json` 갱신
- **특징**: 체크포인트 기반 파이프라인 — 재실행 시 완료 단계 스킵
- **실행**: `pgm-agent-system/CLAUDE.md` `full` 모드

#### Weekly Flash Report (`/pgm [JIRA_KEY]`)
- **입력**: Jira 프로젝트 키 + 선택적 메모
- **출력**: Flash Report 3종 (MD + Docs + Gmail)
- **특징**: WoW 트렌드 포함 (이전 주 데이터 있을 때), 체크포인트 지원
- **실행**: `pgm-agent-system/CLAUDE.md` `flash` 모드

#### 회의록 → Jira 코멘트 (`/pgm --weekly [URL]` 또는 `/weekly`)
- **입력**: Confluence 회의록 URL
- **출력**: TM-XXXX 티켓별 `N주차 Weekly 공유사항` 코멘트
- **특징**: AI 파싱 → 마크다운 미리보기 → 사용자 승인 → 게시
- **섹션**: `지난주 진행상황` + `Action Item (이번주)`
- **주의**: 게시 전 반드시 사용자 승인 (되돌리기 어려움)

#### C레벨 보고서 품질 검토 (`/report`)
- **입력**: 보고서 파일 경로 (없으면 `_artifacts.json`에서 이번 주 Flash 자동 선택)
- **출력**: `report-agent-system/output/report_review_{YYYYMMDD}_{주제}.md`
- **특징**: 즉시 결재 가능 / 질문 후 결재 / 반려 가능성 3단계 판정
- **의존**: `report-agent-system/.claude/agents/red-team-validator` 내부 호출

#### 과제 검토 (`/ticket-review`)
- **입력**: Jira 내보내기 CSV (`pgm-agent-system/input/ticket-review/*.csv`) 또는 JQL
- **출력**: `pgm-agent-system/output/ticket_review_{YYYYMMDD}.md`
- **특징**:
  - MATCH 팀 과제 자동 식별 (명시적 지표 + 도메인 키워드)
  - 유사 과제 에픽·레이블·의미 기반 클러스터링
  - 판단 경계 과제는 `판단 필요` 별도 분류
- **실행**: `pgm-agent-system/.claude/agents/ticket-reviewer/AGENT.md`

### 팀 내 표준 파이프라인

```
# 주간 전체 실행 (권장)
/pgm --full MATCH {CONFLUENCE_URL}

# 단계별 실행
/pgm MATCH              → Flash만
/pgm --weekly {URL}     → 회의록 코멘트만

# 성과 보고 전달
/pgm → /report → /mail

# 과제 분류 후 Jira 등록
/ticket-review → /epic
```

### Artifact Bus 참조

`pgm-agent-system/output/_artifacts.json`에서 이번 주 산출물 경로 확인:
- `/report` 호출 시 → `flash_md` 필드에서 입력 파일 자동 선택
- `/mail` 호출 시 → `flash_md` 또는 `meeting_minutes_md` 참조

---

## [디스커버리팀] 시장/제품 분석

### 역할
시장 조사, 경쟁사 분석, 사용자 인터뷰 시뮬레이션, 화이트스페이스 발굴을 수행한다.

### 팀원 구성
| 역할 | 호출 방법 | 모델 |
|------|----------|------|
| Discovery 분석 | Skill: `/discovery` | claude-sonnet-4-6 |
| 웹 화면 분석 | Skill: `/discovery --mode web-analysis` | claude-sonnet-4-6 |

### 트리거 키워드
Discovery, 시장 분석, 경쟁사, 화이트스페이스, 사용자 인터뷰, 벤치마크, 트렌드, Amplitude, Braze, Shopify, 외부 레퍼런스, 화면 분석, UI 분석, 화면 설계서, 서비스 분석

### 세부 역량

#### Product Discovery (`/discovery`)
- **입력**: 탐색 주제 텍스트 + 선택적 옵션
  - `--ref all/amplitude/braze/shopify`: 외부 벤더 레퍼런스 수집
  - `--initiative TM-XXXX`: 이니셔티브 컨텍스트 로드
- **출력**: `discovery-intelligence-system/output/` 내 분석 보고서
- **특징**: 외부 레퍼런스 수집(Phase 0) → 시장 분석 → 가상 인터뷰 → 인사이트 합성 → 보고서 5단계
- **실행**: `discovery-intelligence-system/CLAUDE.md` 워크플로우 따름

#### 웹 화면 분석 (`/discovery --mode web-analysis`)
- **입력**: 대상 서비스 URL + 선택적 옵션
  - `--depth gnb`: 기능 중심 탐색 — GNB 항목 순회 (기본값)
  - `--depth scenario "{목적}"`: 시나리오 중심 탐색
  - `--menu "{메뉴명}"`: 특정 메뉴만 분석
  - `--initiative TM-XXXX`: 이니셔티브 연결
- **출력**: `discovery-intelligence-system/web-analyzer-agent/output/screen_spec.md` + `screenshots/`
- **특징**: Playwright 브라우저 자동화 + Claude Vision 분석. Google OAuth 감지 시 Semi-Auto 로그인
- **사전 조건**: `pip install playwright && playwright install chromium`
- **실행**: `discovery-intelligence-system/web-analyzer-agent/CLAUDE.md` 워크플로우 따름
- **연계**: Reference 분석과 연결 가능 (`--mode reference --input screenshots/`)

---

## [지식팀] Confluence & Notion

### 역할
사내 지식 저장소(Confluence, Notion)에서 정보를 검색·조회하고, 새 문서를 생성·저장한다.

### 팀원 구성
| 역할 | 호출 방법 | 모델 |
|------|----------|------|
| Confluence 검색/조회 | Agent: `confluence-reader` | claude-haiku-4-5 |
| Confluence 페이지 저장 | Agent: `confluence-writer` | claude-haiku-4-5 |
| Notion 검색/조회/저장 | Skill: `notion-tool` 직접 사용 | — |

### 트리거 키워드
찾아줘, 알려줘, 어디에, 검색, Confluence, Notion, 저장해줘, 올려줘, 문서화, 위키

### 세부 역량

#### Confluence 검색/조회 (`confluence-reader` agent)
- **입력**: 검색 키워드 또는 질문 텍스트
- **출력**: `output/context.json` + 마크다운 요약
- **Space 결정 로직**:
  - always_include: `membership`, `PE`, 개인 Space (항상 검색)
  - 토픽 라우팅 (키워드 감지 시 추가):
    - 마케팅/그로스: `retentionmarketing` → `LTV` → `GP`
    - 추천: `29CMRec`
    - 29CM: `29PRODUCT` → `2CEE` → 등
- **에스컬레이션**: 전체 Space 검색 후 0건 → `escalate: true` 반환 → 사용자에게 `--space ALL` 재검색 제안

#### Confluence 페이지 저장 (`confluence-writer` agent)
- **입력**: 대화 내용 또는 분석 결과 + 대상 Space
- **출력**: Confluence 페이지 URL + `output/draft.html`
- **제목 규칙**: `[YYYYMM] {주제} 분석` (50자 이하)
- **중복 처리**: 동일 제목 존재 시 업데이트 여부 사용자 확인
- **이니셔티브 우선**: `meta.json.confluence.primary_space`가 있으면 spaces.json보다 우선

#### Notion API (`notion-tool` skill)
- **스크립트**: `.claude/skills/notion-tool/scripts/`
  - `search.py` — Notion 검색
  - `fetch_page.py` — 페이지 읽기
  - `write_page.py` — 페이지 생성/업데이트
  - `query_db.py` — DB 조회/업데이트
- **환경변수**: `NOTION_API_TOKEN` 필수

### 팀 내 표준 패턴
```
# 조회
confluence-reader → 요약 → 사용자 답변

# 저장
(선택) confluence-reader로 중복 확인 → confluence-writer

# 조회 후 저장
confluence-reader → 분석 → confluence-writer
```

---

## [커뮤니케이션팀] 이메일 & Jira

### 역할
문서를 이메일로 변환·발송하고, Jira 티켓을 개별 생성한다.

### 팀원 구성
| 역할 | 호출 방법 | 모델 |
|------|----------|------|
| 이메일 발송 오케스트레이터 | Skill: `/mail` | claude-sonnet-4-6 |
| 문서 추출 전문가 | Agent: `doc-specialist` | claude-haiku-4-5 |
| 이메일 HTML 변환·발송 | Agent: `mail-specialist` | claude-haiku-4-5 |
| Jira 티켓 생성 | Agent: `jira-creator` | claude-sonnet-4-6 |
| MEMB Task 티켓 생성 | Skill: `/task-ticket` + Agent: `task-ticket-creator` | claude-sonnet-4-6 |

### 트리거 키워드
메일, 이메일, 발송, 보내줘, Gmail, 공유해줘, Jira, 티켓, 이슈, 등록, 만들어줘, MEMB, Task 티켓

### 세부 역량

#### 이메일 발송 (`/mail`)
- **입력**: Confluence URL 또는 마크다운 파일 경로 + `--to 수신자이메일`
- **처리 흐름**: `doc-specialist`(Confluence 내용 추출) → `mail-specialist`(HTML 변환 + 발송)
- **환경변수**: `GMAIL_USER`, `GMAIL_APP_PASSWORD`
- **출력**: `output/final_email.html` + `output/send_log.json`
- **주의**: 발송 전 반드시 제목·수신자·미리보기 사용자 승인

#### Jira 티켓 개별 생성 (`/jira` 또는 `jira-creator` agent)
- **입력**: 자연어 티켓 요청 (참조 티켓 TM-XXXX/PSN-XXX 언급 가능)
- **처리**: 생성 목록 표 → 사용자 컨펌 → Python 스크립트 생성·실행
- **출력**: `scripts/create_jira_{이니셔티브명}_{YYYYMMDD}.py` + Jira 티켓 URL 목록
- **주의**: 티켓 생성은 되돌리기 어려우므로 반드시 사전 컨펌

#### MEMB Task 티켓 생성 (`/task-ticket` 또는 `task-ticket-creator` agent)
- **입력**: 대화 내용(슬랙/회의 내용 붙여넣기) 또는 작업 설명 텍스트
- **처리**: 내용 분석 → 제목·본문·기한·우선순위 제안 → 사용자 컨펌 → 생성
- **출력**: `scripts/create_memb_task_{YYYYMMDD}_{slug}.py` + MEMB 티켓 URL
- **프로젝트**: MEMB 고정
- **이슈 유형**: Task (단건 또는 복수 지원)
- **특징**: 배경·작업내용·AC 구조화, 날짜 힌트 자동 변환, 컨펌 전 절대 생성하지 않음

> **Epic 분해 + 일괄 Jira 등록**이 필요하면 기획팀 `/epic`을 사용할 것.
> 이 팀의 Jira는 소규모 개별 티켓 생성에 특화.

---

## [미팅팀] 회의 관리

### 역할
회의 전·후 관리를 담당. 회의 맥락을 수집하고, Confluence 회의록을 작성·업로드하며, Google Calendar에 요약을 등록한다.

### 팀원 구성
| 역할 | 호출 방법 | 모델 |
|------|----------|------|
| 회의록 작성 + Confluence 업로드 | Skill: `/meeting` | claude-sonnet-4-6 |
| 회의록 + 캘린더 등록 | Skill: `/meeting --calendar` | claude-sonnet-4-6 |
| 회의록 AI 작성 | Agent: `minutes-writer` (meeting-agent-system 내) | claude-sonnet-4-6 |

### 트리거 키워드
회의록, 미팅, 미팅 정리, 회의 준비, 회의 기록, 회의 요약, 캘린더 등록, 일정 업데이트

### 세부 역량

#### 회의록 작성 (`/meeting`)
- **입력**: 회의 노트 파일(`--input`) / Confluence URL(`--confluence`) / Initiative(`--initiative`)
- **출력**: `meeting-agent-system/output/meeting_draft_{YYYYMMDD}_{slug}.md` + Confluence 페이지
- **업로드 대상**: Core Customer Space / `[MATCH 미팅 회의록]` 하위
- **페이지 제목 형식**: `{YYYY년 MM월 DD일} {회의 제목}`
- **주의**: 업로드 전 반드시 미리보기 + 사용자 승인
- **실행**: `meeting-agent-system/CLAUDE.md` `write` 모드

#### Google Calendar 등록 (`/meeting --calendar`)
- **조건**: 위 회의록 작성 후 자동 연계 또는 `--calendar-only`로 단독 실행
- **이벤트 탐색**: 날짜 + 키워드 검색 → 복수 매칭 시 목록 선택
- **삽입 포맷**:
  ```
  [회의 요약 — PM Studio]
  📋 목적 / ✅ 결정 사항 / 📌 Action Item / 🔗 Confluence URL
  ```
- **환경변수**: `GOOGLE_CLIENT_SECRETS_PATH`, `GOOGLE_CALENDAR_ID`
- **미설정 시**: STUB 모드 (요약 텍스트만 출력)

### 팀 내 표준 파이프라인

```
# 회의록 작성 + Confluence 업로드
/meeting --input notes.txt --initiative TM-2055

# 회의록 + 캘린더 등록 한 번에
/meeting --input notes.txt --title "Auxia 정기 미팅" --calendar

# 회의록 업로드 후 Jira 코멘트 반영 (PGM 연동)
/meeting → /pgm --weekly {Confluence URL}
```

### 설정 필요 항목

`config/spaces.json`의 `core_customer` 섹션:
- `space_key`: Core Customer Space의 실제 키
- `meeting_parent_id`: `[MATCH 미팅 회의록]` 페이지 ID

---

## [회고팀] 작업 로그

### 역할
주간 Claude 대화 내역과 Jira/Confluence 활동 데이터를 결합하여 PM 관점의 회고 문서를 생성한다.

### 팀원 구성
| 역할 | 호출 방법 | 모델 |
|------|----------|------|
| 주간 작업 로그 | Skill: `/work-log` | claude-sonnet-4-6 |

### 트리거 키워드
작업 로그, 주간 회고, 이번 주 한 일, 활동 정리, work-log

### 세부 역량

#### 주간 작업 로그 (`/work-log`)
- **입력**: 없음 (이번 주 자동 수집) 또는 `--week-offset -1` (지난 주), `--no-jira`
- **수집**: `~/.claude/projects/*pm-studio*/*.jsonl` + `scripts/weekly_digest.py`
- **출력**: `output/work_log_{YYYYMMDD}.md`
- **특징**: 작업 테마별 분류, 회고 & 인사이트, 다음 주 예상 작업 포함

---

## 팀간 의존 관계

```
디스커버리팀
    └──► 기획팀 (Discovery 결과 → PRD 입력)
              └──► 마케팅팀 (PRD → GTM 브리프)
              └──► 기획팀 (PRD → Red Team 검증)
              └──► 기획팀 (PRD → Epic 분해 → Jira 등록)

PGM팀
    └──► 커뮤니케이션팀 (Flash 보고서 → 이메일 발송)

지식팀
    ├──► 기획팀 (Confluence 검색 → PRD 입력)
    ├──► 커뮤니케이션팀 (Confluence 페이지 → 이메일 발송)
    └──► (모든 팀의 산출물 → Confluence 저장)
```

---

## 새 팀 추가 방법

현재 CAPABILITY_MAP에 없는 역량이 필요할 때:

1. `.claude/agents/{팀명}/AGENT.md` 생성 (서브에이전트)
   또는 `.claude/skills/{스킬명}/SKILL.md` 생성 (스킬)
2. 이 파일 해당 섹션에 팀 추가
3. `CLAUDE.md`의 라우팅 테이블에 행 추가

**참조 템플릿**: `input/initiatives/_template/` 구조 참고
