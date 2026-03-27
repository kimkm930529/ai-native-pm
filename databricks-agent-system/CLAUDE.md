# Databricks 데이터 탐색 시스템

## 역할
Databricks Unity Catalog와 SQL Warehouse에 연결하여 데이터 탐색, 쿼리 실행, 인사이트 분석을 수행하는 시스템.
`/databricks` 스킬로 호출된다.

> 공통 규약: `../CONVENTIONS.md` | 역량 맵: `../CAPABILITY_MAP.md`

---

## 실행 모드

| 모드 | 트리거 | 출력 |
|------|--------|------|
| **explore** | `--explore` 또는 args 없음 | 카탈로그 구조 리포트 |
| **query** | `--query "[질문]"` | 쿼리 결과 + 요약 |
| **analyze** | `--analyze [table] "[주제]"` | 데이터 분석 리포트 |

---

## Step 0: 연결 확인

```python
# 환경변수 체크
python3 scripts/client.py --check
```

- `DATABRICKS_HOST`, `DATABRICKS_TOKEN` 없으면 → 설정 가이드 출력 후 중단
- `DATABRICKS_WAREHOUSE_ID` 없으면 → query/analyze 모드 불가 (explore만 가능)

### 연결 설정 가이드 (연동 필요)
```
1. Databricks 워크스페이스 접속 → User Settings → Developer → Access Tokens → Generate New Token
2. .env에 추가:
   DATABRICKS_HOST=https://your-workspace.databricks.com
   DATABRICKS_TOKEN=dapi-xxxxxxxxxxxxxxxxxxxx
   DATABRICKS_WAREHOUSE_ID=xxxxxxxxxxxxxxxx   (SQL Warehouses 페이지에서 확인)

3. (선택) MCP 서버 방식 사용 시:
   pip install databricks-mcp
   .claude/mcp.json에 databricks 서버 추가 (SKILL.md §연결 방식 참조)
```

---

## Step 1: explore 모드 — Unity Catalog 탐색

**목적**: 사용 가능한 카탈로그, 스키마, 테이블 구조 파악

```bash
# 전체 카탈로그 목록
python3 scripts/client.py --list-catalogs

# 특정 카탈로그의 스키마 목록
python3 scripts/client.py --list-schemas --catalog {catalog_name}

# 특정 스키마의 테이블 목록
python3 scripts/client.py --list-tables --catalog {catalog} --schema {schema}

# 특정 테이블 상세 (컬럼, 타입, 샘플 데이터)
python3 scripts/client.py --describe --table {catalog}.{schema}.{table}
```

**서브에이전트**: `.claude/agents/schema-explorer/AGENT.md` 호출

**출력 파일**: `output/explore_{YYYYMMDD}_{target}.md`

**리포트 구조**:
```
## 탐색 대상: {catalog/schema/table}
### 카탈로그 목록
| 카탈로그 | 스키마 수 | 설명 |
### 스키마 상세
| 스키마 | 테이블 수 | 주요 테이블 |
### 테이블 상세 (요청 시)
| 컬럼명 | 타입 | Nullable | 설명 |
### 샘플 데이터
(최대 5행)
### 추천 분석 주제
- [AI 생성 인사이트 3~5개]
```

---

## Step 2: query 모드 — 자연어/SQL 쿼리 실행

**목적**: 자연어 질문 → SQL 변환 → Databricks SQL Warehouse 실행 → 결과 해석

**처리 흐름**:
1. 자연어 입력인 경우 → `query-builder` 에이전트가 SQL 자동 생성
2. SQL 직접 입력인 경우 → 바로 실행
3. SQL 실행: `python3 scripts/client.py --execute "[SQL]"`
4. 결과 해석: `data-analyst` 에이전트 호출

**서브에이전트**: `.claude/agents/query-builder/AGENT.md` → `.claude/agents/data-analyst/AGENT.md`

**출력 파일**: `output/query_{YYYYMMDD}_{slug}.md`

**안전 규칙**:
- `SELECT`만 허용. `INSERT`, `UPDATE`, `DELETE`, `DROP`, `CREATE` 실행 금지
- 결과 행 수 1,000건 초과 시 LIMIT 자동 추가 후 사용자 알림
- 실행 전 SQL 미리보기 출력

---

## Step 3: analyze 모드 — 데이터 분석 + 인사이트

**목적**: 테이블 또는 쿼리 결과를 기반으로 PM 관점 분석 리포트 생성

**처리 흐름**:
1. 대상 테이블 스키마 파악 (`schema-explorer`)
2. 분석 주제에 맞는 SQL 쿼리 3~5개 자동 생성 (`query-builder`)
3. 쿼리 순차 실행 + 결과 수집
4. 데이터 기반 인사이트 생성 (`data-analyst`)
5. 이니셔티브 컨텍스트 있으면 → 이니셔티브 목표와 연결

**서브에이전트**: `schema-explorer` → `query-builder` → `data-analyst`

**출력 파일**: `output/analyze_{YYYYMMDD}_{주제}.md`

**리포트 구조**:
```
## 분석 주제: {주제}
## Executive Summary
(3줄 이내 핵심 인사이트)
## 데이터 개요
(테이블 구조, 기간, 레코드 수)
## 분석 결과
### 1. {분석 항목}
(쿼리 + 결과 + 해석)
## 핵심 인사이트
- [PM 관점 인사이트]
## 추천 액션
- [데이터 기반 의사결정 제안]
## Open Questions
- [추가 분석이 필요한 항목]
```

---

## 오류 처리

| 오류 | 처리 |
|------|------|
| 환경변수 미설정 | Step 0 연결 가이드 출력 후 중단 |
| 연결 실패 (401/403) | HOST/TOKEN 확인 요청 |
| 테이블 없음 (404) | explore 모드로 전환 제안 |
| 쿼리 타임아웃 | LIMIT 추가 후 재시도 1회 |
| 쓰기 쿼리 감지 | 실행 거부 + 안전 규칙 안내 |

---

## 출력 파일 명명 규칙

| 모드 | 파일명 |
|------|--------|
| explore | `output/explore_{YYYYMMDD}_{catalog_or_table}.md` |
| query | `output/query_{YYYYMMDD}_{slug}.md` |
| analyze | `output/analyze_{YYYYMMDD}_{주제}.md` |

산출물은 `../output/artifacts/` 아카이브에도 복사.
이니셔티브 연결 시(`--initiative TM-XXXX`) → `../input/initiatives/{TM-XXXX}/output/` 에도 저장.
