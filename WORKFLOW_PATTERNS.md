# PM Studio — 복합 워크플로우 패턴

> 비서실장이 복합 요청 처리 시 참조하는 실행 순서 가이드.
> 자주 발생하는 패턴을 정의하여 일관된 실행을 보장한다.

---

## Pattern A: 기획 → 실행 파이프라인

```
[Discovery] → PRD 작성 → Red Team 검증 → Epic 분해 → Jira 등록
```

**트리거**: "TM-XXXX 기획 시작해줘", "PRD 써서 에픽 분해하고 Jira에 올려줘"

**실행 순서**:
1. `/discovery --initiative TM-XXXX` (선택: 배경 리서치)
2. `/prd TM-XXXX` → PRD 파일 생성
3. `/red {PRD 파일 경로}` → Red Team 검증
4. `/epic {PRD 파일 경로} TM-XXXX` → 목록 컨펌 후 Jira 등록

---

## Pattern B: 주간 성과 보고 파이프라인

```
/pgm --full → /report → (선택) /mail
```

**트리거**: "이번 주 성과 정리해줘", "주간 플래시 + 회의록 다 만들어줘"

**실행 순서**:
1. `/pgm --full [JIRA_KEY] [CONFLUENCE_URL]` → Flash Report + 회의록 + Weekly 코멘트
2. `/report {flash_md 경로}` → C레벨 검토 (선택)
3. `/mail {flash_md 경로} --to {수신자}` → 메일 발송 (선택, 컨펌 필수)

**단계별 단독 실행**:
- Flash Report만: `/pgm [JIRA_KEY]`
- 회의록 + Jira 코멘트만: `/pgm --weekly [CONFLUENCE_URL]`

---

## Pattern C: 지식 관리 파이프라인

```
Confluence 검색 → 인사이트 요약 → (선택) Confluence 저장
```

**트리거**: "~에 대해 알려줘", "찾아줘", "정리해서 올려줘"

**실행 순서**:
1. `confluence-reader` agent → 검색 및 요약
2. (선택) `confluence-writer` agent → Confluence 저장 (컨펌 필수)

---

## Pattern D: 런치 파이프라인

```
Discovery → PRD 작성 → GTM 브리프 → Confluence 저장
```

**트리거**: "~을 출시하려면 뭐가 필요해", "신기능 기획 처음부터 시작하자"

**실행 순서**:
1. `/discovery [주제]` → 시장/제품 분석
2. `/prd` → PRD 작성 (Discovery 결과 참조)
3. `/gtm {PRD 파일 경로}` → GTM 브리프
4. `confluence-writer` agent → 문서 저장 (컨펌 필수)

---

## Pattern E: 문서 공유 파이프라인

```
문서 조회 → 이메일 변환 → 발송 승인 → Gmail 발송
```

**트리거**: "이 문서 ~에게 메일로 보내줘", "Confluence 페이지 공유해줘"

**실행 순서**:
1. `confluence-reader` agent 또는 로컬 파일 확인
2. `/mail {문서 경로 또는 URL} --to {수신자}` → 제목·수신자·미리보기 컨펌 후 발송

---

## Pattern F: 과제 관리 파이프라인 (PGM 전용)

```
/ticket-review → (선택) /epic → Jira 등록
```

**트리거**: "이번 분기 MATCH 과제 정리해줘", "CSV 분석해서 에픽으로 올려줘"

**실행 순서**:
1. `/ticket-review` → CSV 또는 JQL로 과제 분류
2. 분류 결과 확인 후 선택적으로 `/epic` 실행

---

## Pattern G: 회의 관리 파이프라인

```
/meeting → (선택) /pgm --weekly {Confluence URL}
```

**트리거**: "회의록 써줘", "미팅 정리해줘", "회의 준비해줘", "캘린더에 올려줘"

**실행 순서**:
1. `/meeting --input {노트} --initiative TM-XXXX [--calendar]`
   → 회의록 초안 작성 → 미리보기 → Confluence 업로드 → (선택) 캘린더 등록
2. (선택) `/pgm --weekly {Confluence URL}` → 회의록 → Jira Initiative 코멘트 게시

**자주 쓰는 조합**:
```
# 회의록만
/meeting --input notes.txt --title "Auxia 정기 미팅"

# 회의록 + 캘린더
/meeting --input notes.txt --title "Auxia 정기 미팅" --calendar

# 회의록 + Jira 코멘트 (전체 미팅 사이클)
/meeting --input notes.txt --initiative TM-2055
→ (업로드 완료 후) /pgm --weekly {반환된 Confluence URL}
```

---

## 병렬 실행 가능 조합

| 병렬 가능 | 조건 |
|---------|------|
| `/pgm --full` 내 publisher + minutes-generator | analysed_report.json 생성 후 |
| `/pgm --full` 내 jira-parser + confluence 페이지 로드 | 독립적, 동시 실행 가능 |
| `confluence-reader` + 다른 검색 | 서로 독립 |

---

## TM-XXXX 이니셔티브 컨텍스트 로드

요청에 `TM-XXXX` 형식이 포함되면:

1. `input/initiatives/index.md`에서 매칭 이니셔티브 확인
2. 해당 폴더의 `context.md`·`meta.json`·`decisions.md` 로드
3. `meta.json`의 `confluence.primary_space`를 기본 Space로 사용
4. 산출물을 해당 이니셔티브의 `output/` 폴더에도 저장

```
input/initiatives/
├── index.md                   ← 전체 이니셔티브 목록
└── 2026Q1/
    └── {TICKET-ID}_{이름}/
        ├── meta.json          ← 티켓 메타 (Space, 기간, 상태)
        ├── context.md         ← 배경·목표·성공지표
        ├── decisions.md       ← 의사결정 로그
        └── output/            ← 생성 산출물
```
