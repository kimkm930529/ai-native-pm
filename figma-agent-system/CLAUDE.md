# Figma 화면 분석 · 디자인 스펙 시스템

## 역할
Figma REST API를 통해 디자인 파일을 분석하고, 화면 설계서·UX 스펙·PRD 초안을 생성하는 시스템.
`/figma` 스킬로 호출된다.

> 공통 규약: `../CONVENTIONS.md` | 역량 맵: `../CAPABILITY_MAP.md`

---

## 실행 모드

| 모드 | 트리거 | 출력 |
|------|--------|------|
| **analyze** | URL만 입력 | 화면 구조 분석 리포트 |
| **spec** | `--spec` | 화면 설계서 (스펙 문서) |
| **prd** | `--prd` | 화면 기반 PRD 초안 |
| **compare** | `--compare [URL2]` | 디자인 비교 분석 |
| **copy** | `--copy` | UX 카피 텍스트 추출 |

---

## Step 0: 연결 확인 + URL 파싱

```bash
python3 scripts/client.py --check
```

### URL 파싱
```
https://www.figma.com/design/{file_key}/{title}?node-id={node_id}
→ file_key 추출: 파일 전체 분석
→ node-id 추출 (있으면): 특정 프레임/컴포넌트만 분석
```

### 연결 설정 가이드 (연동 필요)
```
1. Figma 로그인 → figma.com/settings
2. Security 탭 → Personal access tokens → Generate new token
3. .env에 추가:
   FIGMA_ACCESS_TOKEN=figd_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Step 1: analyze 모드 — 화면 구조 분석

**목적**: Figma 파일의 페이지·프레임·컴포넌트 구조를 파악하고 PM 관점으로 정리

**처리 흐름**:

#### 1-A. figma-reader 에이전트 호출 (Haiku)
```
Agent(
  subagent_type="general-purpose",
  model="haiku",
  prompt="""
  figma-agent-system/.claude/agents/figma-reader/AGENT.md 를 읽고 실행해줘.
  file_key: {file_key}
  node_id: {node_id or "전체"}
  mode: analyze
  작업 디렉토리: /Users/musinsa/Documents/agent_project/pm-studio/figma-agent-system
  """
)
```

#### 1-B. screen-analyst 에이전트 호출 (Sonnet) — figma-reader 완료 후
```
Agent(
  subagent_type="general-purpose",
  prompt="""
  figma-agent-system/.claude/agents/screen-analyst/AGENT.md 를 읽고 실행해줘.
  figma-reader 결과: {figma-reader 출력 전문}
  mode: analyze
  """
)
```

**출력 파일**: `output/figma_analyze_{YYYYMMDD}_{주제}.md`

**분석 리포트 구조**:
```
## 파일 정보
- 파일명, 최종 수정일, 페이지 수

## 화면 목록
| 페이지 | 프레임명 | 디바이스 | 설명 |

## 화면 플로우
(주요 사용자 여정 요약)

## 컴포넌트 현황
(주요 재사용 컴포넌트 목록)

## PM 관점 노트
- 구현 판단이 필요한 UI 패턴
- 엣지케이스로 보이는 화면
- 명확하지 않은 인터랙션
```

---

## Step 2: spec 모드 — 화면 설계서 생성

**목적**: Figma 화면을 기반으로 개발팀 전달용 화면 설계서 작성

**처리 흐름**:

#### 2-A. figma-reader 에이전트 호출 (Haiku)
```
Agent(
  subagent_type="general-purpose",
  model="haiku",
  prompt="""
  figma-agent-system/.claude/agents/figma-reader/AGENT.md 를 읽고 실행해줘.
  file_key: {file_key}
  node_id: {node_id or "전체"}
  mode: spec
  작업 디렉토리: /Users/musinsa/Documents/agent_project/pm-studio/figma-agent-system
  """
)
```

#### 2-B. screen-analyst 에이전트 호출 (Sonnet) — figma-reader 완료 후
```
Agent(
  subagent_type="general-purpose",
  prompt="""
  figma-agent-system/.claude/agents/screen-analyst/AGENT.md 를 읽고 실행해줘.
  figma-reader 결과: {figma-reader 출력 전문}
  mode: spec_prep
  """
)
```

#### 2-C. spec-writer 에이전트 호출 (Sonnet) — screen-analyst 완료 후
```
Agent(
  subagent_type="general-purpose",
  prompt="""
  figma-agent-system/.claude/agents/spec-writer/AGENT.md 를 읽고 실행해줘.
  screen-analyst 결과: {screen-analyst 출력 전문}
  figma-reader 결과: {figma-reader 출력 전문}
  output_path: figma-agent-system/output/figma_spec_{YYYYMMDD}_{주제}.md
  Figma 원본 URL: {입력 URL}
  """
)
```

#### 2-D. Confluence 저장 제안
spec-writer 완료 후 사용자에게 Confluence 업로드 여부 확인.
승인 시 `confluence-writer` 에이전트 호출.

**출력 파일**: `output/figma_spec_{YYYYMMDD}_{주제}.md`

**화면 설계서 구조**:
```
## {화면명} 설계서

### 화면 목적
### 진입 경로
### 화면 요소
| 요소 | 타입 | 설명 | 조건 |
### 인터랙션
| 이벤트 | 반응 | 조건 |
### 상태별 화면
(정상 / 로딩 / 에러 / 빈 상태)
### 엣지케이스
### 개발 참고사항
```

---

## Step 3: prd 모드 — 화면 기반 PRD 초안 생성

**목적**: Figma 화면을 분석하여 기능 요구사항과 PRD 초안 자동 생성

**처리 흐름**:
1. analyze 모드 → 화면 구조 파악
2. `screen-analyst` → 화면에서 기능 요구사항 추출
3. `../prd-agent-system/CLAUDE.md` 워크플로우 연계
   - 화면 분석 결과를 Rough Note로 전달
   - 일반 PRD 생성 파이프라인 실행

**출력**: `prd-agent-system/output/prd_{YYYYMMDD}_{주제}.md`

---

## Step 4: compare 모드 — 디자인 비교

**목적**: 두 버전의 디자인(Before/After)을 비교하여 변경사항 정리

**처리 흐름**:
1. URL1, URL2 각각 analyze
2. `screen-analyst` → 차이점 비교
3. 변경 요약 리포트 생성

**출력 파일**: `output/figma_compare_{YYYYMMDD}_{주제}.md`

---

## Step 5: copy 모드 — UX 카피 추출

**목적**: Figma 파일의 모든 텍스트 레이어를 수집하여 카피 시트 생성

```bash
python3 scripts/client.py --extract-text {file_key} [--node {node_id}]
```

**출력 파일**: `output/figma_copy_{YYYYMMDD}_{주제}.md`

---

## 오류 처리

| 오류 | 처리 |
|------|------|
| 환경변수 미설정 | 연결 가이드 출력 후 중단 |
| 파일 접근 불가 (403) | 파일 공유 설정 확인 요청 |
| 노드 없음 (404) | 파일 전체 analyze 모드로 전환 |
| 이미지 내보내기 실패 | 텍스트 기반 분석만 진행 |

---

## 출력 파일 명명 규칙

| 모드 | 파일명 |
|------|--------|
| analyze | `output/figma_analyze_{YYYYMMDD}_{주제}.md` |
| spec | `output/figma_spec_{YYYYMMDD}_{주제}.md` |
| prd (연계) | `prd-agent-system/output/prd_{YYYYMMDD}_{주제}.md` |
| compare | `output/figma_compare_{YYYYMMDD}_{주제}.md` |
| copy | `output/figma_copy_{YYYYMMDD}_{주제}.md` |

이니셔티브 연결 시 → `../input/initiatives/{TM-XXXX}/output/` 에도 저장.
