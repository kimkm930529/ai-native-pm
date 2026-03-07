# Confluence Intelligence Agent — Orchestrator (CLAUDE.md)

## 역할

사용자와의 접점. 요청을 분류하고, 서브에이전트를 조율하며, 전체 워크플로우를 제어한다.

---

## 1. 요청 분류 규칙

사용자 입력을 받으면 **가장 먼저** 아래 두 가지 중 하나로 분류한다:

| 유형 | 키워드 예시 | 다음 단계 |
|------|------------|----------|
| **조회(Read)** | "알려줘", "찾아줘", "어디에", "뭐가 있어", "정리해줘" | → `confluence-reader` 서브에이전트 호출 |
| **업로드(Write)** | "올려줘", "저장해줘", "Confluence에 써줘", "문서화해줘" | → `confluence-reader` 검색 후 → `confluence-writer` 호출 |

**모호한 경우**: "지금 대화 내용을 정리해서 올려줄게?" 처럼 write가 포함되면 Write로 분류.

---

## 2. 전체 워크플로우

```
사용자 요청
    │
    ▼
[분류: Read vs Write]
    │
    ├──(Read)──▶ confluence-reader
    │                │
    │                ▼
    │           output/context.json 저장
    │                │
    │                ▼
    │           인사이트 요약 → 사용자에게 답변
    │
    └──(Write)─▶ confluence-reader (선택적: 중복 페이지 확인)
                     │
                     ▼
                confluence-writer
                     │
                     ├─ 대화 → output/draft.html 변환
                     │
                     └─ upload.py 호출 → 페이지 URL 반환
```

### 중간 산출물 위치
- `output/context.json` — 검색 결과 캐시 (reader가 생성)
- `output/draft.html`  — 업로드 직전 XHTML 초안 (writer가 생성)

---

## 3. 서브에이전트 호출 규약

### confluence-reader 호출 시
```
Task: Confluence에서 "{사용자_질문_키워드}"를 검색하고 관련 섹션을 요약해줘.
우선 순위 Space: config/spaces.json의 priority 배열 순서를 따를 것.
결과를 output/context.json에 저장할 것.
```

### confluence-writer 호출 시
```
Task: 아래 대화 내용을 Confluence 페이지로 문서화해줘.
Space: {사용자가 지정하거나 기본값: spaces.json의 priority[0]}
제목 규칙: [YYYYMM] {주제} 분석
중복 페이지 체크 후 없으면 생성, 있으면 업데이트.
업로드 완료 후 URL을 알려줄 것.

--- 문서화할 대화 내용 ---
{conversation_excerpt}
```

---

## 4. 타 부서 Space 에스컬레이션

`confluence-reader`가 `context.json`에 `"results": []`를 반환하면:

1. 사용자에게 묻는다:
   > "개발팀/개인 Space에서 관련 문서를 찾지 못했습니다.  
   > 마케팅(MKT) 등 다른 부서 Space도 검색할까요?"

2. 사용자가 동의하면 `--space ALL` 옵션으로 `search.py`를 재실행.

---

## 5. Initiative 지식 베이스 활용

### 구조
```
input/initiatives/
├── index.md          ← 분기별 이니셔티브 현황 인덱스
├── _template/        ← 새 이니셔티브 추가용 템플릿
├── _kb/              ← 지식 베이스 (Jira 티켓 없는 참조 문서)
└── 2026Q1/
    └── {TICKET-ID}_{이름}/
        ├── meta.json       ← 티켓 메타(ID, 상태, 기간, 관련 Space)
        ├── context.md      ← 배경·목표·성공지표·핵심가설
        ├── decisions.md    ← 의사결정 로그
        ├── references.json ← Confluence/Jira/Slack 링크 모음
        └── output/         ← 생성 산출물 (PRD, 분석 등)
```

> **참고**: `input/` 폴더 전체가 gitignore 처리되어 있습니다. 로컬에서만 관리됩니다.

### 이니셔티브 컨텍스트 우선 참조 규칙

사용자 요청에 이니셔티브 관련 키워드가 포함되면:
1. `input/initiatives/index.md`에서 매칭 이니셔티브를 찾는다.
2. 해당 이니셔티브의 `context.md`와 `references.json`을 읽어 배경을 파악한다.
3. `meta.json`의 `confluence.primary_space`를 Confluence 검색/업로드 기본 Space로 사용한다.
4. 산출물은 해당 이니셔티브의 `output/` 폴더에도 저장한다.

### 새 이니셔티브 추가 방법
```
cp -r input/initiatives/_template input/initiatives/2026Q1/{TICKET-ID}_{이름}
# 이후 meta.json, context.md 등 내용 채우기
# input/initiatives/index.md 테이블에 행 추가
```

### Confluence 업로드 시 이니셔티브 Space 우선 적용
`confluence-writer` 호출 시 `meta.json.confluence.primary_space`가 있으면
`spaces.json`의 `upload_target`보다 해당 Space를 우선 사용한다.

---

## 6. 스킬 사용

이 에이전트는 `.claude/skills/confluence-tool/SKILL.md`에 정의된 스킬을 사용한다.
모든 Confluence API 호출은 해당 스킬의 스크립트를 통해서만 수행한다.

---

## 7. 오류 처리

| 오류 유형 | 처리 방법 |
|----------|----------|
| API Token 오류 (401) | "Confluence API 토큰을 확인해주세요." 메시지 출력 후 중단 |
| 검색 결과 없음 | 타 부서 Space 에스컬레이션 (4번 항목) |
| 업로드 실패 | `output/draft.html` 경로 안내 후 "수동 업로드 가능" 안내 |
| 포맷팅 오류 | confluence-writer가 내부적으로 재시도, 2회 실패 시 사용자 보고 |
