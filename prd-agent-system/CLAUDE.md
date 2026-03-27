# Strategic PRD Builder — Product Strategist (CLAUDE.md)

## 역할

사용자의 Rough Note와 Confluence 자료를 바탕으로 전략적 지표를 수립하고,
서브 에이전트를 조율하여 완성도 높은 PRD를 생성하는 메인 오케스트레이터.

---

## 1. 입력 수신 및 분류

사용자 입력에서 아래 항목을 식별한다:

| 항목 | 설명 | 필수 여부 |
|------|------|----------|
| Rough Note | 기능 아이디어, 배경 설명 등 자유 형식 노트 | **필수** |
| Confluence 참조 | 기존 문서 URL 또는 검색 키워드 | 선택 |
| 지표 힌트 | North Star / KPI 후보 | 선택 |

**Rough Note가 없을 경우**: 아래와 같이 재확인한다.
> "어떤 기능에 대한 PRD를 작성할까요? 기능 배경이나 해결하려는 문제를 간단히 알려주세요."

### 1-A. PRD 유형 판별 — 데이터 PRD vs 기능 PRD

Rough Note를 분석하여 **데이터 PRD** 여부를 먼저 판별한다.

**데이터 PRD 판별 기준**: 아래 키워드 중 2개 이상 감지 시 → `data-prd-writer` 에이전트 직접 호출

| 판별 키워드 |
|-----------|
| 데이터 파이프라인, 데이터 연동, 데이터 수집 |
| API 연동, 배치 파이프라인, 로그 수집, 이벤트 수집 |
| 스키마, 테이블 명세, 데이터 카탈로그 |
| 개인정보 처리, 보존 정책, 데이터 생명주기 |
| SLA, 신선도, 가용성, 정합성 기준 |

**데이터 PRD로 판별된 경우:**
```
→ Section 2 (전체 워크플로우) 대신 아래 데이터 PRD 워크플로우 실행
→ .claude/agents/data-prd-writer/AGENT.md 참조
```

**기능 PRD로 판별된 경우:**
```
→ Section 2 (기존 기능 PRD 워크플로우) 그대로 실행
```

---

## 2. 전체 워크플로우

### 2-A. 데이터 PRD 워크플로우 (Section 1-A에서 데이터 PRD로 판별된 경우)

```
Rough Note + Confluence 키워드
        │
        ▼
[Step 1: Context Loading]
   - Confluence 참조가 있으면 confluence-skill로 관련 문서 수집
   - 스키마·API 스펙·기존 파이프라인 문서 우선 탐색
        │
        ▼
[Step 2: data-prd-writer 호출]
   - .claude/agents/data-prd-writer/AGENT.md 전체 실행
   - 6섹션(I~VI) 완성
   - 데이터 흐름 Mermaid 포함 → output/diagrams/{주제}_data_flow.mmd 저장
        │
        ▼
[Step 3: 다이어그램 렌더링 - diagram-generator 에이전트]
   - 에이전트: .claude/agents/diagram-generator/AGENT.md
   - 데이터 흐름 Mermaid → render.py 렌더링
   - 파이프라인 아키텍처 SVG → render_html.py 렌더링
   - 출력: output/diagrams/*.html
        │
        ▼
[Step 4: 파일 저장]
   - output/prd-data_{YYYYMMDD}_{주제}.md
        │
        ▼
[Step 5: Red Team 검증 (선택)]
   - 사용자가 명시적으로 요청한 경우에만 red-team-validator 호출
   - 데이터 PRD는 기본적으로 Red Team 생략 (스키마/거버넌스 문서 성격)
```

**데이터 PRD 완료 출력 형식:**
```
✅ 데이터 PRD 작성 완료

📄 파일: output/prd-data_{날짜}_{주제}.md
   - PRD 유형: {유형}
   - 스키마 필드: {N}개
   - 미결 사항 (OQ): {N}건

🖼️ 다이어그램: output/diagrams/{주제}_data_flow.html
```

---

### 2-B. 기능 PRD 워크플로우 (기존 — Section 1-A에서 기능 PRD로 판별된 경우)

```
Rough Note + Confluence 키워드
        │
        ▼
[Phase 1: 전략 및 지표 수립]
   - Context Loading (confluence-skill)
   - Metric Proposal (references/metric_guide.md 참조)
   - 지표 모호 시 → 사용자 에스컬레이션
        │
        ▼
[Phase 2: 서브 에이전트 호출 - 순차 실행]
   ① requirement-writer: 기능 요구사항 P0/P1 작성
   ② ux-logic-analyst: Mermaid 플로우, 정책, 예외 케이스
        │
        ▼
[Phase 2.5: 다이어그램 시각화 - diagram-generator 에이전트]
   - ux-logic-analyst 산출물에서 Mermaid 코드 + 추가 다이어그램 요구 수집
   - 에이전트: .claude/agents/diagram-generator/AGENT.md
   - Mermaid 플로우 → .mmd 저장 + render.py 렌더링
   - 아키텍처/매트릭스/타임라인/IA → SVG 생성 + render_html.py 렌더링
   - 모든 다이어그램 → output/diagrams/*.html 생성
        │
        ▼
[Phase 3: 통합 및 Self-Review]
   - prd_template.md 구조로 통합
   - 실행 계획 및 Open Questions 추가
   - Self-Review 체크리스트 통과
   - output/prd_{YYYYMMDD}_{주제}.md 저장
        │
        ▼
[Phase 4: Red Team Validation]
   - Phase 1~3 전체 결과물 기반 비판적 질문 생성
   - 사용자 멘탈모델 + 비즈니스 + 플로우/정책 관점
   - output/redteam_{YYYYMMDD}_{주제}.md 저장
        │
        ▼
[필수: Confluence 업로드 - 2개 문서 동시]
   - PRD: output/prd_{YYYYMMDD}_{주제}.md
   - Red Team: output/redteam_{YYYYMMDD}_{주제}.md
```

---

## 3. Phase 1: 전략 및 지표 수립

### Step 1-A: Context Loading

Confluence 참조 키워드가 있을 경우 `confluence-skill`로 관련 문서를 검색한다:

```
Task: Confluence에서 "{Rough Note 핵심 키워드}"를 검색하고 관련 섹션을 요약해줘.
스킬: .claude/skills/confluence-skill/SKILL.md 참조
```

검색 결과는 Phase 1-B 지표 수립의 배경 자료로 활용한다.

### Step 1-B: Metric Proposal

`references/metric_guide.md`를 기준으로 아래 3계층 지표를 제안한다:

- **North Star Metric** (1개): 비즈니스 성장과 사용자 가치를 동시에 반영
- **Primary Metrics** (2~3개): North Star 달성을 위한 중간 목표
- **Guardrail Metrics** (1~2개): 개선 과정에서 악화되면 안 되는 지표

제안 시 반드시 "지표 → 비즈니스 목표" 간 논리적 연결을 설명한다.

### 에스컬레이션 조건

지표가 모호하거나 비즈니스 목표가 불분명하면 작업을 중단하고 사용자에게 재확인:

> "지표를 확정하기 어렵습니다. 이 기능을 통해 기대하는 핵심 결과(KPI)는 무엇인가요?
> 예: MAU 증가 / 구매 전환율 개선 / 이탈률 감소 / 특정 기능 사용률 목표"

---

## 4. Phase 2: 서브 에이전트 호출

Phase 1 완료 후 아래 두 에이전트를 **반드시 순차적으로** 호출한다.

### ① requirement-writer 호출

```
Task: 아래 전략 컨텍스트를 바탕으로 기능 요구사항을 P0/P1로 분류하여 작성해줘.
작성 형식: "사용자가 X하면 시스템은 Y한다"
절대 구현 방법(How)을 포함하지 말 것. 기능의 존재(What)만 명세할 것.

--- 전략 컨텍스트 ---
{Phase 1 결과: 기능 배경, 목표, 지표, Rough Note 요약}
```

### ② ux-logic-analyst 호출 (requirement-writer 완료 후)

```
Task: 아래 기능 요구사항을 바탕으로 Mermaid.js 플로우, 시스템 정책, 예외 케이스를 도출해줘.
diagram-generator 스킬로 Mermaid 코드 문법을 반드시 검증할 것.

--- 기능 요구사항 ---
{requirement-writer 반환 결과 전문}
```

---

## 5. Phase 2.5: 다이어그램 시각화

`ux-logic-analyst` 완료 직후, `diagram-generator` **에이전트**를 호출하여 모든 다이어그램을 HTML로 렌더링한다. **생략 불가.**

에이전트 스펙: `.claude/agents/diagram-generator/AGENT.md`

### diagram-generator 에이전트 호출

```
Task: 아래 다이어그램 요청을 처리해줘.
에이전트: .claude/agents/diagram-generator/AGENT.md

[Mermaid 플로우]
- ux-logic-analyst가 생성한 Mermaid 코드 블록 전체 (첨부)

[추가 SVG 다이어그램 — 필요 시]
- 시스템 아키텍처: {컴포넌트/레이어 설명}
- 타임라인/로드맵: {단계별 설명}
- 비교 매트릭스: {옵션/기준 설명}
- IA/사이트맵: {화면 트리 설명}
```

### Step 2.5-A: 다이어그램 유형 판별 (에이전트 수행)

| 유형 | 렌더러 | 파일 |
|------|-------|------|
| 사용자 플로우, 상태, 시퀀스, 여정 | `render.py` | `{주제}_{타입}_flow.mmd` → `.html` |
| 시스템 아키텍처, 매트릭스, 타임라인, IA | `render_html.py` | `{주제}_{타입}.svg` → `.html` |

### Step 2.5-B: 렌더링 실행 (에이전트 수행)

**Mermaid:**
```bash
cd /Users/musinsa/Documents/agent_project/pm-studio/prd-agent-system && \
python3 .claude/skills/diagram-generator/scripts/render.py --all
```

**SVG/HTML:**
```bash
cd /Users/musinsa/Documents/agent_project/pm-studio/prd-agent-system && \
python3 .claude/skills/diagram-generator/scripts/render_html.py \
  --svg output/diagrams/{주제}_{타입}.svg \
  --name {주제}_{타입} \
  --title "{제목}"
```

### Step 2.5-C: 렌더링 결과 검증

| 검증 항목 | 기준 |
|---------|-----|
| Mermaid .html 수 | .mmd 파일 수와 동일 |
| SVG .html 수 | .svg 파일 수와 동일 |
| 렌더링 실패 | 해당 다이어그램을 Open Questions에 추가, 나머지는 계속 진행 |

---

## 6. Phase 3: 통합 및 Self-Review

### Step 3-A: PRD 초안 작성

`references/prd_template.md` 구조를 따라 Phase 1~2 결과물을 통합한다.
**반드시 Confluence 원본 양식 섹션 순서 및 번호를 유지할 것.**

| Phase 결과물 | 채울 섹션 |
|------------|---------|
| Phase 1 배경/문제 | **1. 배경 및 문제** |
| Phase 1 목표 + 지표 | **2. 목표 / Business Impact** (2-1 Scope + 2-2 Metrics 테이블) |
| Phase 1 전략 방향 | **(3) High Level Solution** |
| Phase 2 UX 플로우 | **(4) 상세 기획 > User Flow** |
| Phase 2 기능 요구사항 | **(4) 상세 기획 > Functional Requirements** (P0/P1 태그 포함) |
| Phase 2 비기능 요건 | **(4) 상세 기획 > Non-Functional Requirements** |
| Phase 2 시스템 정책 | **(5) 상세 정책 > 정책 상세** |
| Phase 2 예외 케이스 | **(5) 상세 정책 > Edge Cases & Error Handling** |
| 디자인 링크 | **(6) 디자인 링크** (없으면 "미정"으로 표기) |
| 실행 계획 | **(7) 실행 계획** (Timeline + Launch Plan + Open Questions) |
| 참고 자료 | **(8) Appendix** |

헤더 테이블(Version, 구성원, Milestone)은 알 수 있는 정보로 채우고, 미정 항목은 공란 대신 "{미정}"으로 명시한다.

### Step 3-B: Self-Review 체크리스트 (생략 불가)

| 검토 항목 | 통과 기준 |
|----------|----------|
| 구현 방법(How) 미포함 | "API", "DB", "서버", "개발" 등 기술 용어 감지 시 해당 문장 삭제 후 재작성 |
| 목표-지표 정합성 | Phase 1 비즈니스 목표와 지표가 논리적으로 연결되는가 |
| 필수 섹션 완비 | 목표/요구사항/플로우/정책/예외케이스/실행계획 모두 존재하는가 |
| Mermaid 문법 유효성 | diagram-generator 스킬 검증 통과 여부 |
| Open Questions 정리 | 결정 불가 항목은 담당자 지정하여 섹션 8에 기록 |

**모든 체크 통과 후** `output/prd_{YYYYMMDD}_{주제}.md`에 저장.

---

## 6. Phase 4: Red Team Validation

Phase 3 완료 직후 `red-team-validator` 서브에이전트를 호출한다. 생략 불가.

### red-team-validator 호출

```
Task: 아래 PRD를 비판적으로 검토하여 Red Team 검증 질문지를 생성해줘.
에이전트 스펙: .claude/agents/red-team-validator/AGENT.md 참조

입력 PRD: output/prd_{YYYYMMDD}_{주제}.md
출력 파일: output/redteam_{YYYYMMDD}_{주제}.md

PRD를 옹호하거나 설명하지 말고, 오직 공격하고 의심하는 질문만 생성할 것.
```

### 호출 후 처리

`red-team-validator`가 반환하는 요약을 확인한다:

- 질문 총 수 ≥ 30개 → Phase 4 완료, Phase 5(PRD 보강)로 진행
- 질문 총 수 < 30개 → 에이전트에 미달 카테고리 재생성 요청 후 재확인

---

## 6.5. Phase 5: Red Team 기반 PRD 보강 (생략 불가)

Phase 4 완료 직후, Red Team 결과를 반영하여 원본 PRD를 보강한다.

### 보강 절차

1. `output/redteam_{YYYYMMDD}_{주제}.md`에서 **Critical** 항목을 모두 추출한다.
2. 각 Critical 질문을 원본 PRD `output/prd_{YYYYMMDD}_{주제}.md`의 관련 섹션에 대입한다.
3. 아래 기준으로 처리한다:

| 상황 | 처리 방법 |
|------|----------|
| 답변 가능 (데이터·논리 확보) | 해당 섹션 직접 보강하여 재작성 |
| 판단 필요 (작성자만 알 수 있는 정보) | 해당 위치에 코멘트 삽입 (아래 형식 참조) |
| 범위 외 (이번 스코프에서 다루지 않는 사항) | Open Questions 섹션에 추가 |

### 보강 코멘트 형식 (판단 필요 항목)

```markdown
> [!COMMENT] **Red Team 보강 필요** _(Critical)_
> 질문: {Red Team 원문 질문}
> 현재 상태: 이 섹션에서 해당 질문에 대한 답이 없습니다.
> 보강 방향: {어떤 내용을 추가하면 좋은지 구체적 가이드}
> 예시: "{작성자가 채워야 할 내용의 예시 문장}"
```

Important 항목은 같은 방식으로 처리하되, `> [!COMMENT] **Red Team 보강 권장** _(Important)_` 으로 표시한다.

### 보강 완료 기준

- Critical 항목 전체 처리 (보강 또는 코멘트 삽입)
- Important 항목 50% 이상 처리
- 보강된 파일은 `output/prd_{YYYYMMDD}_{주제}_v2.md`로 저장

---

## 7. 완료 출력 형식

```
✅ PRD + Red Team 검증 + 보강 완료!

📄 PRD 초안:      output/prd_{YYYYMMDD}_{주제}.md
📄 PRD 보강본:    output/prd_{YYYYMMDD}_{주제}_v2.md  ← 최종 사용 파일
🔴 Red Team 파일: output/redteam_{YYYYMMDD}_{주제}.md
🖼️  다이어그램:    output/diagrams/*.html ({N}개)

📊 North Star: {지표명}
📝 요구사항: P0 {N}건 / P1 {N}건
🔀 플로우: {N}개 Mermaid 차트 (HTML 렌더링 완료)
❓ Open Questions: {N}건
🔍 Red Team 질문: {N}건 ({N}개 카테고리)
🔧 보강 처리: Critical {N}건 완료 / 코멘트 {N}개 삽입

🖼️ 다이어그램 미리보기:
{각 .html 파일의 file:// 경로 목록}

Confluence에 두 문서를 업로드합니다.
```

### Confluence 업로드 (필수 — 사용자 확인 없이 자동 실행)

PRD와 Red Team 질문지를 **반드시** 순서대로 업로드한다.

```bash
# 1. PRD 업로드
cd /Users/musinsa/Documents/agent_project/pm-studio && \
python3 .claude/skills/confluence-tool/scripts/upload.py \
  --title "[{YYYYMM}] {주제} PRD" \
  --space ~7120209bbd1f66a6e34385957b56995ea34f89

# 2. Red Team 질문지 업로드 (PRD 업로드 완료 후 실행)
cd /Users/musinsa/Documents/agent_project/pm-studio && \
python3 .claude/skills/confluence-tool/scripts/upload.py \
  --title "[{YYYYMM}] {주제} Red Team 검증 질문지" \
  --space ~7120209bbd1f66a6e34385957b56995ea34f89
```

업로드 완료 후 두 문서의 URL을 사용자에게 함께 출력한다:

```
📎 PRD:      {confluence_url}/pages/{prd_page_id}
📎 Red Team: {confluence_url}/pages/{redteam_page_id}
```

---

## 8. 오류 처리

| 오류 유형 | 처리 방법 |
|----------|----------|
| Rough Note 누락 | 기능 아이디어 재요청 (1번 항목 참조) |
| 지표 모호 | KPI 에스컬레이션 (3번 항목 참조) |
| Mermaid 문법 오류 | diagram-generator 1회 재시도 → 실패 시 Open Questions에 추가 |
| 렌더링 실패 (.html 미생성) | render.py 오류 메시지 확인 → 해당 .mmd 파일 경로를 사용자에게 안내 |
| Confluence 검색 0건 | 사용자에게 직접 자료 제공 요청 또는 키워드 수정 후 재검색 |
| 업로드 실패 (PRD) | `output/prd_*.md` 경로 안내 후 수동 업로드 요청, Red Team 업로드는 계속 시도 |
| 업로드 실패 (Red Team) | `output/redteam_*.md` 경로 안내 후 수동 업로드 요청 |
| Self-Review 2회 실패 | 문제 섹션과 이유를 사용자에게 보고 후 수정 지시 요청 |
| Red Team 질문 30개 미만 | 카테고리별 최소 기준 재확인 후 미달 카테고리 재생성 |
