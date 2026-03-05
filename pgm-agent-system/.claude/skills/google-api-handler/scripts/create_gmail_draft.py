#!/usr/bin/env python3
"""
create_gmail_draft.py — Gmail 초안 생성 스크립트 (Stub)

주의: 이 스크립트는 Draft를 생성하며 실제 발송은 하지 않습니다.

환경변수:
  GOOGLE_CLIENT_SECRETS_PATH : OAuth 클라이언트 시크릿 JSON 경로
  GOOGLE_CREDENTIALS_PATH    : 인증 토큰 저장 경로

사용법:
  python3 create_gmail_draft.py \
    --subject "[주간 보고] 03/05 캠페인 메타 엔진 외 4건 완료" \
    --body-file output/flash_20260305_mail.txt \
    --to "pm@company.com,team@company.com"
"""

import argparse
import base64
import json
import os
import sys
from email.mime.text import MIMEText


def get_credentials(secrets_path: str, token_path: str):
    """
    STUB: Google OAuth 2.0 인증 처리.

    연동 활성화:
      pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
    """
    # --- 실제 인증 코드 (stub 해제 시 사용) ---
    # from google.oauth2.credentials import Credentials
    # from google_auth_oauthlib.flow import InstalledAppFlow
    # from google.auth.transport.requests import Request
    #
    # SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]
    # creds = None
    # if os.path.exists(token_path):
    #     creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
    #         creds = flow.run_local_server(port=0)
    #     with open(token_path, "w") as f:
    #         f.write(creds.to_json())
    # return creds
    return None  # STUB


def create_draft(service, subject: str, body: str, to: str) -> str:
    """
    STUB: Gmail Draft 생성.
    ⚠️ send() 메서드 호출 금지. drafts.create()만 사용.

    실제 코드:
      message = MIMEText(body)
      message["to"] = to
      message["subject"] = subject
      raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
      draft = service.users().drafts().create(
          userId="me",
          body={"message": {"raw": raw}}
      ).execute()
      return draft["id"]
    """
    stub_draft_id = "STUB_DRAFT_ID_REPLACE_AFTER_ACTIVATION"
    print(f"[STUB] Gmail Draft 생성 시뮬레이션")
    print(f"[STUB] 수신자: {to}")
    print(f"[STUB] 제목: {subject}")
    print(f"[STUB] 본문 길이: {len(body)}자")
    print(f"[STUB] 실제 연동 시 Draft ID가 반환됩니다.")
    print("\n" + "="*60)
    print("📧 메일 본문 미리보기")
    print("="*60)
    print(body)
    print("="*60 + "\n")
    return stub_draft_id


def main():
    parser = argparse.ArgumentParser(description="Gmail 초안 생성 (발송 없음)")
    parser.add_argument("--subject", required=True, help="메일 제목")
    parser.add_argument("--body-file", required=True, help="본문 텍스트 파일 경로")
    parser.add_argument("--to", default=os.environ.get("FLASH_REPORT_RECIPIENTS", ""),
                        help="수신자 이메일 (쉼표 구분)")
    args = parser.parse_args()

    if not args.to:
        print("[ERROR] 수신자 이메일 미지정 — --to 파라미터 또는 FLASH_REPORT_RECIPIENTS 환경변수 필요")
        sys.exit(1)

    if not os.path.exists(args.body_file):
        print(f"[ERROR] 본문 파일을 찾을 수 없습니다: {args.body_file}")
        sys.exit(1)

    with open(args.body_file, "r", encoding="utf-8") as f:
        body = f.read()

    secrets_path = os.environ.get("GOOGLE_CLIENT_SECRETS_PATH", "")
    token_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", os.path.expanduser("~/.google_token.json"))

    if not secrets_path:
        print("[WARNING] GOOGLE_CLIENT_SECRETS_PATH 미설정 — STUB 모드로 실행합니다.")

    creds = get_credentials(secrets_path, token_path)
    # service = build("gmail", "v1", credentials=creds)

    draft_id = create_draft(None, args.subject, body, args.to)
    print(f"[OK] Gmail Draft ID: {draft_id}")

    # 결과를 파일로도 저장 (publisher가 참조)
    result_path = "output/gmail_draft_result.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump({
            "subject": args.subject,
            "to": args.to,
            "draft_id": draft_id,
            "stub": True
        }, f, ensure_ascii=False, indent=2)

    print(f"[OK] 결과 저장: {result_path}")


if __name__ == "__main__":
    main()
