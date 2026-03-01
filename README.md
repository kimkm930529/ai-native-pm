# PM Studio

> **AI Native PM을 지향한다.**
> AI가 드래프트를 생성하고, PM은 판단을 내린다.

---

## AI Native PM이란 무엇인가

전통적인 PM은 도구를 *수동으로 조작*한다. 문서를 열고, 템플릿을 채우고, 검색하고, 정리한다.
AI Native PM은 다르게 일한다. **에이전트에게 문맥을 주고 초안을 위임한 뒤, 판단과 방향 결정에 집중한다.**

이 전환의 핵심은 단순한 자동화가 아니다. *PM의 인지 자원을 어디에 쓸 것인가*의 재배분이다.

```
전통적 PM        →    AI Native PM
──────────────────────────────────────────────
문서 작성 (2h)   →    에이전트 초안 → 검토·수정 (30m)
Confluence 검색  →    자연어 질문 → 인사이트 요약 수신
티켓 분해 (1h)   →    에픽 입력 → 티켓 목록 수신 → 우선순위 결정
GTM 브리프 (3h)  →    PRD 입력 → 브리프 생성 → 메시지 판단
```

---

## AI Native PM의 5가지 작동 원칙

### 1. Prompt-First Thinking — 빈 문서가 아닌 에이전트로 시작한다

작업을 시작할 때 새 문서를 열지 않는다.
에이전트에게 요청하면 초안이 나온다. PM의 역할은 그 초안을 *판단하고 방향을 잡는 것*이다.

### 2. Draft Fast, Judge Slow — AI가 빠르게, PM은 깊게

에이전트는 빠르다. 초안 생성, 대안 작성, 형식 변환은 에이전트에게 맡긴다.
PM은 *왜 이 방향인가*, *무엇을 빠뜨렸는가*, *고객에게 맞는가*를 판단하는 데 시간을 쓴다.

### 3. Context as Assets — 컨텍스트를 파일로 축적한다

에이전트의 품질은 컨텍스트의 품질에 비례한다.
이니셔티브 배경(`context.md`), 의사결정 로그(`decisions.md`), 참조 문서(`references.md`)를 구조화해서 쌓는다.
쌓인 컨텍스트가 다음 작업을 더 잘 지원한다 — **지식 플라이휠**.

### 4. Agents as Teammates — 에이전트는 팀원이다

에이전트는 버튼이 아니다. *역할이 있고, 기대 산출물이 있고, 검증 기준이 있는* 팀원으로 다룬다.
각 에이전트에게 명확한 역할을 주고, 결과물을 검토하고, 피드백 루프를 구성한다.

### 5. Human-in-the-Loop — 전략과 판단은 PM의 영역이다

AI가 빠른 초안을 만들더라도, 아래 영역은 반드시 PM이 직접 판단한다:
- 기회 우선순위 결정 (무엇을 만들 것인가)
- 고객 인터뷰 설계와 인사이트 해석
- 스테이크홀더 설득과 관계 관리
- 비즈니스 전략과 연계한 최종 방향 결정

---

## PM 워크플로우 × AI 분업 지도

PM의 일반적인 6단계 워크플로우에서 이 시스템이 어떤 역할을 하는지 정리한다.

```
┌─────────────────────────────────────────────────────────────────┐
│  PM 워크플로우                AI 처리 영역        인간 판단 영역  │
├──────────────┬───────────────────────────┬──────────────────────┤
│  1. Discover │ Confluence 검색·요약       │ 인터뷰 설계           │
│  (탐색)      │ 앱푸시 성과 분석           │ 인사이트 해석         │
│              │ 타 부서 문서 탐색          │ 기회 정의             │
├──────────────┼───────────────────────────┼──────────────────────┤
│  2. Define   │ North Star / KPI 초안 제안 │ 지표 최종 결정        │
│  (정의)      │ 이니셔티브 컨텍스트 로드   │ 성공 기준 합의        │
│              │                           │ 우선순위 판단         │
├──────────────┼───────────────────────────┼──────────────────────┤
│  3. Design   │ PRD 초안 생성             │ 방향 결정 및 수정     │
│  (설계)      │ UX 플로우 + 정책 작성     │ 엣지 케이스 검토      │
│              │ Red Team 검증 질문 생성    │ 기술 협의 및 조율     │
│              │ UX 카피 작성              │ 최종 PRD 승인         │
├──────────────┼───────────────────────────┼──────────────────────┤
│  4. Develop  │ 에픽 → 스토리 분해        │ 스프린트 우선순위     │
│  (개발)      │ Jira 티켓 포맷팅          │ 엔지니어링 협상       │
│              │ 요구사항 P0/P1 분류       │ 범위 조율             │
├──────────────┼───────────────────────────┼──────────────────────┤
│  5. Launch   │ GTM 브리프 생성           │ 출시 전략 결정        │
│  (출시)      │ Before/After 정리         │ 채널 우선순위         │
│              │ 롤아웃 플랜 설계           │ 스테이크홀더 커뮤니케이션│
│              │ Launch Metrics 설정        │ 타이밍 판단           │
├──────────────┼───────────────────────────┼──────────────────────┤
│  6. Learn    │ Confluence 문서 자동 저장  │ 회고 방향 설정        │
│  (학습)      │ 이니셔티브 decisions 기록  │ 다음 이니셔티브 연결  │
│              │ 성과 리포트 요약           │ 전략적 교훈 도출      │
└──────────────┴───────────────────────────┴──────────────────────┘
```

### AI 처리 비중 추정 (업무 유형별)

| 업무 유형 | AI 처리 비중 | PM 판단 비중 |
|----------|------------|------------|
| 문서 초안 작성 (PRD, GTM, 분석) | 70~80% | 20~30% |
| 지식 검색 및 요약 | 90% | 10% |
| 티켓 분해 및 포맷팅 | 80% | 20% |
| 지표 설계 초안 | 50% | 50% |
| 고객 인사이트 해석 | 10% | 90% |
| 전략 방향 결정 | 0% | 100% |

---

## AI Native PM으로 일하기 — 상황별 에이전트 활용 가이드

### 상황 1: "이 이슈, 우리 팀에서 다룬 적 있어?"

```
에이전트: Confluence Intelligence Agent (루트)
입력: "앱푸시 리텐션 관련 분석 찾아줘"
출력: 관련 문서 3건 + 핵심 인사이트 요약
소요: 1~2분
```

**활용 패턴:** 회의 전 사전 조사, 이슈 히스토리 파악, 타 팀 문서 탐색 시 사용.

---

### 상황 2: "아이디어가 있는데 PRD를 써야 해"

```
에이전트: Strategic PRD Builder (prd-agent-system/)
입력: Rough Note (자유 형식 아이디어 메모)
출력: PRD 초안 + Red Team 검증 질문지 + Confluence 자동 업로드
소요: 10~20분
```

**활용 패턴:**
1. 아이디어를 자유 형식으로 입력 (불완전해도 됨)
2. 에이전트가 North Star / KPI 초안을 제안 → PM이 지표 확정
3. 기능 요구사항 + 플로우 초안 수신 → 검토 및 수정
4. Red Team 질문 수신 → 빠뜨린 엣지 케이스 확인

---

### 상황 3: "PRD 승인났는데, 티켓을 써야 해"

```
에이전트: Epic Ticket System (epic-ticket-system/)
입력: PRD 또는 에픽 설명
출력: P0/P1 기준 분해된 Jira 티켓 목록 + 포맷팅
소요: 5~10분
```

**활용 패턴:** PRD의 기능 요구사항을 입력하면 스토리/태스크 단위로 분해. PM은 우선순위와 담당자 배정에 집중.

---

### 상황 4: "런칭 전, 마케터에게 줄 GTM 브리프가 필요해"

```
에이전트: GTM Agent System (gtm-agent-system/)
입력: PRD 파일 (prd_*.md)
출력: GTM_Brief_*.md (One-liner / Before-After / Key Message / 롤아웃 / Launch Metrics)
소요: 5~10분
```

**활용 패턴:**
1. `gtm-agent-system/input/`에 PRD 파일 배치
2. 에이전트가 마케팅 언어로 변환 (기술 용어 자동 제거)
3. PM이 One-liner와 Key Message 최종 검토 후 확정

---

### 상황 5: "이번 앱푸시 성과, 빠르게 정리해야 해"

```
도구: tools/app-push-analyzer/
입력: 성과 데이터 파일
출력: 분석 리포트 (채널별 성과, 인사이트, 시각화)
```

**활용 패턴:** 주간/월간 앱푸시 성과 리뷰, 채널 최적화 의사결정 시 사용.

---

### 상황 6: "오늘 회의 내용, Confluence에 남겨야 해"

```
에이전트: Confluence Intelligence Agent (루트)
입력: "오늘 대화 내용 정리해서 Confluence에 올려줘"
출력: XHTML 변환 → Confluence 자동 업로드 → 페이지 URL 반환
소요: 2~3분
```

**활용 패턴:** 회의 직후 대화 내용 입력 → 에이전트가 문서 구조화 + 업로드.

---

## 이니셔티브 컨텍스트 관리 — 지식 플라이휠 구성법

AI Native PM의 핵심 습관은 **컨텍스트를 파일로 남기는 것**이다.
에이전트는 `initiatives/` 폴더를 자동으로 참조하며, 축적된 컨텍스트일수록 더 정확한 초안을 생성한다.

### 이니셔티브 시작 시 해야 할 일

```bash
# 1. 템플릿 복사
cp -r initiatives/_template initiatives/2026Q1/TM-xxxx

# 2. meta.json — 티켓 ID, 상태, 기간, 관련 Confluence Space 입력
# 3. context.md — 배경, 목표, 핵심 가설, 성공 지표 작성
# 4. initiatives/index.md 테이블에 행 추가
```

### 이니셔티브 진행 중 유지할 파일

| 파일 | 업데이트 시점 | 내용 |
|------|-------------|------|
| `context.md` | 방향이 바뀔 때마다 | 배경·목표·핵심 가설 변경 이력 |
| `decisions.md` | 의사결정 직후 | 결정 내용, 배경, 대안, 결과 |
| `references.md` | 문서/슬랙 링크 생길 때마다 | Confluence URL, Jira 링크 |
| `output/` | 산출물 생성 시 | PRD, GTM 브리프, 분석 결과 |

**원칙:** 에이전트에게 "이번 TM-2061 관련해서 PRD 써줘"라고 하면, `context.md`를 읽고 배경을 이해한 상태에서 작업을 시작한다.

---

## 현재 이 시스템으로 할 수 있는 것

### 시스템 구성 전체 지도

```
pm-studio/
├── CLAUDE.md                     ← 루트 오케스트레이터 (Confluence Intelligence Agent)
├── config/
│   └── spaces.json               ← Confluence Space 키 매핑 및 토픽 라우팅
├── initiatives/
│   ├── index.md                  ← 분기별 이니셔티브 현황 인덱스
│   ├── _template/                ← 이니셔티브 추가용 템플릿
│   └── 2026Q1/                   ← Q1 이니셔티브 (TM-xxxx 폴더)
├── output/                       ← 공통 산출물 (context.json, draft.html, 로그)
├── tools/
│   └── app-push-analyzer/        ← 앱푸시 성과 분석 도구
├── prd-agent-system/             ← PRD 자동 생성 에이전트 시스템
├── epic-ticket-system/           ← 에픽 → 티켓 분해 에이전트 시스템
├── gtm-agent-system/             ← GTM 브리프 자동 생성 에이전트 시스템
└── ux-copywriter-system/         ← UX 카피라이팅 에이전트 시스템
```

---

### 에이전트 시스템 1: Confluence Intelligence Agent

**위치:** 루트 `CLAUDE.md`
**핵심 기능:** Confluence를 자연어로 검색하고, 대화 내용을 문서화한다.

| 입력 | 처리 | 출력 |
|------|------|------|
| "앱푸시 성과 찾아줘" | 토픽 감지 → Space 자동 선택 → 검색 | 관련 문서 + 인사이트 요약 |
| "오늘 대화 Confluence에 올려줘" | XHTML 변환 → 중복 체크 → 업로드 | Confluence 페이지 URL |

**서브 에이전트:**
- `confluence-reader` — 키워드 추출 → Space 라우팅 → 검색 → 상위 3건 요약
- `confluence-writer` — Storage Format 변환 → 포맷 검증 → 업로드 (2회 재시도)

**Space 자동 라우팅:** 질문 키워드에 따라 탐색 Space가 자동 결정된다.

| 질문 키워드 예시 | 추가 탐색 Space |
|----------------|--------------|
| 그로스, 리텐션, CRM, 캠페인 | `retentionmarketing` → `LTV` → `GP` |
| 추천, 개인화, 피드, 랭킹 | `29CMRec` |
| 29CM, 이구, 29씨엠 | `29PRODUCT` → `2CEE` → `29CMTECH` |
| (모든 질문 공통) | `membership` → `PE` → 개인 Space |

---

### 에이전트 시스템 2: Strategic PRD Builder

**위치:** `prd-agent-system/`
**핵심 기능:** Rough Note → 전략 지표 수립 → 기능 요구사항 → UX 플로우 → Red Team 검증 → Confluence 업로드.

```
Rough Note (자유 형식)
    ↓
Phase 1: North Star + KPI 초안 제안 → PM 확정
    ↓
Phase 2: 서브 에이전트 병렬 실행
    ├── requirement-writer: P0/P1 기능 요구사항
    └── ux-logic-analyst: Mermaid 플로우 + 정책 + 예외케이스
    ↓
Phase 3: 통합 + Self-Review (6개 항목 체크)
    ↓
Phase 4: Red Team Validation (30개 이상 비판 질문)
    ↓
Confluence 자동 업로드: PRD + Red Team 질문지 2개 문서
```

**주요 산출물:**
- `output/prd_{YYYYMMDD}_{주제}.md` — 완성된 PRD
- `output/redteam_{YYYYMMDD}_{주제}.md` — Red Team 검증 질문지
- Confluence 페이지 2개 (자동 업로드)

---

### 에이전트 시스템 3: Epic Ticket System

**위치:** `epic-ticket-system/`
**핵심 기능:** 에픽 설명 또는 PRD를 입력하면 Jira 티켓 단위로 분해하고 포맷팅한다.

**서브 에이전트:**
- `epic-decomposer` — 에픽을 P0/P1 기준 스토리/태스크로 분해
- `ticket-formatter` — Jira 티켓 형식(제목, 설명, AC, 예상 포인트)으로 정제

---

### 에이전트 시스템 4: GTM Agent System

**위치:** `gtm-agent-system/`
**핵심 기능:** PRD를 입력하면 마케터가 즉시 사용 가능한 GTM 브리프를 생성한다.

**데이터 흐름:**
```
input/prd_*.md
    → [메인 오케스트레이터] PRD 파싱 → prd_parsed.json
    → [message-architect]  One-liner / 페르소나 Pain-point / Key Message → messaging_draft.json
    → [channel-planner]    Before/After / 범위 / 롤아웃 / Launch Metrics → strategy_draft.json
    → [brief-formatter]    JSON 2개 + 템플릿 결합 → GTM_Brief_{YYYYMMDD}_{주제}.md
```

**산출물 8개 섹션:** One-liner · Target User · Before/After · Key Message · What's in/out · Rollout Plan · Enablement · Launch Metrics

**핵심 제약 (자동 검증):**
- One-liner 50자 이하 + 시스템명 금지
- Before/After에 수치 또는 Step 수 변화 필수
- Phase 1 / Phase 2 범위 명확히 분리

---

### 에이전트 시스템 5: UX Copywriter System

**위치:** `ux-copywriter-system/`
**핵심 기능:** 기능 설명을 입력하면 사용자 중심 UI 텍스트와 마이크로카피를 생성한다.

**서브 에이전트:**
- `message-architect` — 메시지 구조 설계 (톤, 계층, 맥락)
- `ui-text-writer` — 버튼 레이블, 안내문, 에러 메시지 등 실제 UI 텍스트 작성

---

### 도구: App Push Analyzer

**위치:** `tools/app-push-analyzer/`
**핵심 기능:** 앱푸시 채널 성과 데이터를 분석하고 인사이트 리포트를 생성한다.

---

## 환경 설정

### 필수 환경변수

```bash
export CONFLUENCE_URL="https://musinsa-oneteam.atlassian.net"
export CONFLUENCE_EMAIL="your-email@musinsa.com"
export CONFLUENCE_API_TOKEN="ATATT3x..."
export CONFLUENCE_SPACE_KEY="~your-personal-space-key"
```

API 토큰 발급: Atlassian 계정 → Security → API tokens

### 선택 환경변수

```bash
export CONFLUENCE_PARENT_PAGE_ID="123456"  # 하위 페이지 생성 시 부모 페이지 ID
```

---

## 스킬 스크립트 직접 사용

### search.py — Confluence 검색

```bash
python3 .claude/skills/confluence-tool/scripts/search.py \
  --query "앱푸시 성과" \
  --space retentionmarketing \
  --limit 10

# 접근 가능한 전체 Space 목록 확인
python3 .claude/skills/confluence-tool/scripts/search.py --list-spaces
```

### upload.py — Confluence 업로드

```bash
# 사전 조건: output/draft.html에 Confluence Storage Format(XHTML) 필요
python3 .claude/skills/confluence-tool/scripts/upload.py \
  --title "[202603] 앱푸시 월간 성과 분석" \
  --space membership \
  --parent-id 123456
```

### assemble.py — GTM 브리프 조립

```bash
python3 gtm-agent-system/.claude/skills/brief-formatter/scripts/assemble.py \
  --messaging gtm-agent-system/output/messaging_draft.json \
  --strategy  gtm-agent-system/output/strategy_draft.json \
  --template  gtm-agent-system/references/gtm_template.md \
  --output    gtm-agent-system/output/GTM_Brief_20260302_샘플.md
```

---

## 산출물 경로 전체 목록

| 경로 | 설명 |
|------|------|
| `output/context.json` | Confluence 검색 결과 캐시 |
| `output/draft.html` | Confluence 업로드용 XHTML 초안 |
| `output/upload_result.json` | 업로드 결과 (페이지 URL 포함) |
| `output/confluence_skill.log` | API 호출 전체 로그 |
| `prd-agent-system/output/prd_*.md` | 생성된 PRD 파일 |
| `prd-agent-system/output/redteam_*.md` | Red Team 검증 질문지 |
| `gtm-agent-system/output/GTM_Brief_*.md` | 생성된 GTM 브리프 |
| `gtm-agent-system/output/prd_parsed.json` | GTM용 PRD 파싱 결과 |
| `gtm-agent-system/output/messaging_draft.json` | 메시징 초안 |
| `gtm-agent-system/output/strategy_draft.json` | 전략 초안 |
| `initiatives/{분기}/{티켓}/output/` | 이니셔티브별 산출물 |

---

## 오류 처리

| 오류 | 원인 | 처리 |
|------|------|------|
| 401 Auth Error | API 토큰 만료 | 토큰 재발급 후 환경변수 업데이트 |
| 검색 결과 0건 | 대상 Space에 문서 없음 | 타 부서 Space 에스컬레이션 (에이전트가 자동 제안) |
| 업로드 실패 | 포맷 오류 또는 권한 없음 | `output/draft.html` 경로 안내 + 수동 업로드 가능 |
| 404 Not Found | Space 키 미존재 | `config/spaces.json` Space 키 확인 |
| One-liner 50자 초과 | 메시징 생성 오류 | message-architect 자동 재시도 (최대 3회) |

---

## 현재 이니셔티브 현황 (2026 Q1)

자세한 내용은 `initiatives/index.md` 참조.

| 티켓 | 이니셔티브 | 상태 | 마감 |
|------|-----------|------|------|
| TM-2061 | Campaign Meta Engine (Phase 1): CMS 연동 기반 캠페인·소재 관리 표준화 | In Progress | 2026-03-31 |

---

> **작성일**: 2026-03-02 | **구동 환경**: Claude Code (claude-sonnet-4-6) + Atlassian Confluence REST API
