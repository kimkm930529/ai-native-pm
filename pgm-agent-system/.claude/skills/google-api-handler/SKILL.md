# google-api-handler — Skill Spec

## 역할

Google Docs 문서 생성(upsert) 및 Gmail 초안 생성을 담당한다.
**실제 메일 발송은 하지 않는다. Gmail Draft API만 사용.**

## 환경변수 (필수)

| 변수명 | 설명 |
|--------|------|
| `GOOGLE_CLIENT_SECRETS_PATH` | OAuth 2.0 클라이언트 시크릿 JSON 경로 (Google Cloud Console에서 다운로드) |
| `GOOGLE_CREDENTIALS_PATH` | 인증 토큰 저장 경로 (최초 인증 후 자동 생성, 기본: `~/.google_token.json`) |
| `GOOGLE_DRIVE_FOLDER_ID` | Docs 초안을 저장할 Drive 폴더 ID |
| `FLASH_REPORT_RECIPIENTS` | Gmail 수신자 이메일 (쉼표 구분, 예: `pm@company.com,team@company.com`) |

## Google API 설정 방법

1. Google Cloud Console → API 및 서비스 → 사용 설정:
   - Google Docs API
   - Gmail API
   - Google Drive API
2. OAuth 2.0 클라이언트 ID 생성 → JSON 다운로드 → `GOOGLE_CLIENT_SECRETS_PATH` 지정
3. 최초 실행 시 브라우저 인증 팝업 → `GOOGLE_CREDENTIALS_PATH`에 토큰 저장됨

## 스크립트 목록

### upsert_google_doc.py

```bash
python3 .claude/skills/google-api-handler/scripts/upsert_google_doc.py \
  --title "Weekly Flash [202603] 0305 주간 보고" \
  --content output/flash_20260305.md \
  --folder-id ${GOOGLE_DRIVE_FOLDER_ID}
```

- 동일 제목의 문서가 폴더 내 존재하면 업데이트, 없으면 신규 생성
- 반환값: Google Docs URL (`https://docs.google.com/document/d/{DOC_ID}/edit`)

### create_gmail_draft.py

```bash
python3 .claude/skills/google-api-handler/scripts/create_gmail_draft.py \
  --subject "[주간 보고] 03/05 캠페인 메타 엔진 외 4건 완료" \
  --body-file output/flash_20260305_mail.txt \
  --to "pm@company.com,team@company.com"
```

- `send` API 호출 금지. `draft.create`만 허용.
- 반환값: Gmail Draft ID
