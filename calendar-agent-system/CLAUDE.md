# Calendar Agent — 작업 캘린더 생성기 (CLAUDE.md)

## 역할

`staff_sessions.jsonl` 로그와 Confluence 최근 수정 문서를 조합하여,
특정 날짜의 시간대별 작업 내역을 정리하고 Google Calendar CSV + ICS 파일로 출력한다.

---

## 1. 입력 수신

| 파라미터 | 설명 | 기본값 |
|---------|------|-------|
| `--date` | 정리할 날짜 (YYYY-MM-DD) | 어제 (today - 1day) |
| `--output-dir` | 출력 디렉토리 | `calendar-agent-system/output/` |
| `--no-confluence` | Confluence 조회 생략 플래그 | False |

**호출 예시:**
```
/calendar --date 2026-03-23
/calendar           ← 어제 날짜 자동 적용
/calendar --date 2026-03-23 --no-confluence
```

---

## 2. 전체 워크플로우

### Step 1. 로그 수집

**staff_sessions.jsonl에서 해당 날짜 세션 추출:**
```python
# 조건: start_ts가 타겟 날짜이고 status == "completed"
target_sessions = [
    s for s in all_sessions
    if s["start_ts"].startswith(target_date) and s.get("status") == "completed"
]
```

**Confluence 최근 수정 문서 조회 (선택):**
- `GET /rest/api/content/search?cql=lastModified >= "타겟날짜" AND contributor = currentUser()`
- 페이지 제목, 수정 시간, 담당자 추출

---

### Step 2. 시간블럭 통합

**규칙:**
1. 각 세션의 `start_ts`를 **30분 단위로 내림** (floor to :00 or :30)
2. 같은 30분 블럭에 여러 세션이 있으면 **하나로 병합**
3. 최소 블럭 길이: **30분**. 실제 소요 시간이 30분 초과면 60분으로 올림
4. 하루 내 블럭이 인접하면 (30분 이하 간격) **연속 블럭으로 병합 고려**

**블럭 병합 판단 기준:**
- 같은 주제 (동일 프로젝트명, 문서 키워드 유사도)이면 병합
- 다른 주제라도 15분 이하 간격이면 병합 권장

---

### Step 3. 이벤트 생성 규칙

**제목 (Subject):**
- 최대 **20자** 이내 (Korean 기준)
- 핵심 행동 + 대상 형식: `"[행동] [대상]"` (예: `"2-Pager 리뷰 준비"`, `"Auxia Flash 정리"`)
- **[업무] 접두사는 자동 추가** — 제목에 직접 쓰지 않아도 됨

**본문 (Description):**
- 수행한 작업의 구체적인 내용
- 사용 스킬, 참조 문서 URL, 산출물 파일명 포함
- 형식:
  ```
  {작업 상세 설명}
  스킬: {skill1, skill2}
  참조: {Confluence URL 또는 파일명}
  산출물: {output 파일명}
  ```

**시간 형식 (Google Calendar CSV 호환):**
- Start/End Date: `MM/DD/YYYY`
- Start/End Time: `HH:MM AM/PM`

---

### Step 4. 출력 파일 생성

**CSV (Google Calendar 가져오기용):**
```
output/staff_calendar_{YYYYMMDD}.csv
```
- 컬럼: Subject, Start Date, Start Time, End Date, End Time, All Day Event, Description, Location, Private

**ICS (Apple Calendar / Google Calendar 직접 열기):**
```
output/staff_calendar_{YYYYMMDD}.ics
```
- 모든 이벤트 제목에 `[업무]` 접두사 자동 포함
- TZID: Asia/Seoul
- CLASS: PRIVATE

---

## 3. 에이전트 실행 방법

### A. 기존 스크립트 활용 (빠른 실행)

1단계 — 특정 날짜의 세션 데이터로 CSV 생성:
```bash
python3 scripts/generate_calendar_csv.py --from {YYYY-MM-DD} \
  --output calendar-agent-system/output/staff_calendar_{YYYYMMDD}.csv
```

2단계 — CSV → ICS 변환:
```bash
python3 scripts/generate_ics.py \
  --input calendar-agent-system/output/staff_calendar_{YYYYMMDD}.csv \
  --output calendar-agent-system/output/staff_calendar_{YYYYMMDD}.ics
```

> ⚠️ 기존 스크립트는 "completed" 필터 없이 모든 세션 포함. 수동 후처리 필요 시 Step B 사용.

### B. 에이전트 직접 처리 (품질 우선)

1. `output/logs/staff_sessions.jsonl`에서 타겟 날짜 + status=completed 세션 필터링
2. 세션 내용 분석 → 시간블럭 통합 → 제목/본문 생성 (위 Step 2~3 규칙 적용)
3. CSV 파일 직접 작성 (Write 도구 사용)
4. `python3 scripts/generate_ics.py --input {csv_path} --output {ics_path}` 실행

---

## 4. 출력 보고 형식

```
[캘린더 에이전트] 완료했습니다.

📅 대상 날짜: 2026-03-23
📊 총 {N}개 시간블럭 생성

시간블럭 요약:
- 00:00-00:30  Core Customer 업무 현황 정리
- 11:00-11:30  Audience API 세그먼트 연동 답변
- ...

📁 산출물:
- CSV: calendar-agent-system/output/staff_calendar_20260323.csv
- ICS: calendar-agent-system/output/staff_calendar_20260323.ics
```

---

## 5. 모델

이 에이전트는 **Haiku** 모델을 사용한다 (스크립트 실행 + 단순 데이터 변환).

```python
Agent(subagent_type="general-purpose", model="haiku", prompt="...")
```

---

## 6. 의존 파일

| 파일 | 용도 |
|------|------|
| `output/logs/staff_sessions.jsonl` | 세션 로그 원본 |
| `scripts/generate_calendar_csv.py` | JSONL → CSV 변환 |
| `scripts/generate_ics.py` | CSV/JSONL → ICS 변환 |
| `calendar-agent-system/output/` | 산출물 저장 디렉토리 |
