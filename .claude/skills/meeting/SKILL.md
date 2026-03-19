# /meeting — Meeting Agent

## 사용법

```
/meeting [옵션]
```

## 옵션

| 옵션 | 설명 |
|------|------|
| `--input {파일경로}` | 회의 노트 텍스트 파일 |
| `--confluence {URL}` | Confluence 페이지 참조 (컨텍스트 보완) |
| `--initiative {TM-XXXX}` | Jira Initiative 배경 자동 로드 |
| `--title {제목}` | 회의 제목 (없으면 AI가 컨텍스트에서 추론) |
| `--date {YYYY-MM-DD}` | 회의 날짜 (기본: 오늘) |
| `--attendees {이름1,이름2}` | 참석자 목록 |
| `--calendar` | 회의록 완성 후 Google Calendar 이벤트에 요약 등록 |
| `--calendar-event-id {ID}` | 업데이트할 캘린더 이벤트 ID (없으면 날짜+제목 검색) |
| `--calendar-only` | 캘린더 등록만 실행 (회의록이 이미 완성된 경우) |

## 빠른 실행 예시

```bash
# 노트 파일로 회의록 작성
/meeting --input meeting-agent-system/input/notes_20260309.txt --title "Auxia 정기 미팅"

# Initiative 배경 포함 회의록
/meeting --input notes.txt --initiative TM-2055

# 회의록 + 캘린더 등록 한 번에
/meeting --input notes.txt --title "Auxia 정기 미팅" --calendar

# 기존 회의록을 캘린더에만 등록
/meeting --calendar-only --date 2026-03-09 --title "Auxia 정기 미팅"

# 텍스트 직접 붙여넣기 (args 없이 실행 → 회의 내용 입력 요청)
/meeting
```

## 실행 규칙

1. `meeting-agent-system/CLAUDE.md`를 읽어 워크플로우를 파악한다.
2. args를 파싱하여 모드 결정:
   - `--calendar-only` → calendar-only 모드
   - `--calendar` → write + calendar 모드
   - 나머지 → write 모드
3. args가 없으면 회의 내용 입력 방법을 안내한다.
4. `meeting-agent-system/CLAUDE.md`의 Step 1~5를 순서대로 실행한다.
5. Confluence 업로드 전 반드시 미리보기 + 사용자 승인.
6. 최종 산출물은 `meeting-agent-system/output/`에 저장.

## Confluence 업로드 대상

- **Space**: Core Customer (`config/spaces.json`의 `core_customer.space_key`)
- **상위 페이지**: [MATCH 미팅 회의록] (`config/spaces.json`의 `core_customer.meeting_parent_id`)
- **페이지 제목 형식**: `{YYYY년 MM월 DD일} {회의 제목}`

## PGM 연동

회의록 업로드 후 Jira Initiative 코멘트 반영이 필요하면:
```
/pgm --weekly {Confluence URL}
```
