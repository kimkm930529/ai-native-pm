#!/usr/bin/env python3
"""
upsert_google_doc.py — Google Docs 문서 생성/업데이트 스크립트 (Stub)

환경변수:
  GOOGLE_CLIENT_SECRETS_PATH : OAuth 클라이언트 시크릿 JSON 경로
  GOOGLE_CREDENTIALS_PATH    : 인증 토큰 저장 경로 (기본: ~/.google_token.json)
  GOOGLE_DRIVE_FOLDER_ID     : 문서를 저장할 Drive 폴더 ID

사용법:
  python3 upsert_google_doc.py \
    --title "Weekly Flash [202603] 0305 주간 보고" \
    --content output/flash_20260305.md \
    --folder-id {FOLDER_ID}
"""

import argparse
import json
import os
import sys


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
    # SCOPES = [
    #     "https://www.googleapis.com/auth/documents",
    #     "https://www.googleapis.com/auth/drive"
    # ]
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


def find_existing_doc(drive_service, title: str, folder_id: str):
    """
    STUB: Drive에서 동일 제목 문서 검색.

    실제 코드:
      query = f"name='{title}' and '{folder_id}' in parents and mimeType='application/vnd.google-apps.document' and trashed=false"
      results = drive_service.files().list(q=query, fields="files(id, name)").execute()
      files = results.get("files", [])
      return files[0]["id"] if files else None
    """
    return None  # STUB: 항상 신규 생성


def create_doc(docs_service, drive_service, title: str, content: str, folder_id: str) -> str:
    """
    STUB: Google Docs 문서 생성 및 내용 삽입.

    실제 코드:
      doc = docs_service.documents().create(body={"title": title}).execute()
      doc_id = doc["documentId"]
      docs_service.documents().batchUpdate(
          documentId=doc_id,
          body={"requests": [{"insertText": {"location": {"index": 1}, "text": content}}]}
      ).execute()
      drive_service.files().update(
          fileId=doc_id,
          addParents=folder_id,
          fields="id, parents"
      ).execute()
      return f"https://docs.google.com/document/d/{doc_id}/edit"
    """
    stub_doc_id = "STUB_DOC_ID_REPLACE_AFTER_ACTIVATION"
    print(f"[STUB] Google Docs 생성 시뮬레이션")
    print(f"[STUB] 제목: {title}")
    print(f"[STUB] 폴더 ID: {folder_id}")
    print(f"[STUB] 실제 연동 시 URL이 반환됩니다.")
    return f"https://docs.google.com/document/d/{stub_doc_id}/edit"


def main():
    parser = argparse.ArgumentParser(description="Google Docs 문서 생성/업데이트")
    parser.add_argument("--title", required=True, help="문서 제목")
    parser.add_argument("--content", required=True, help="내용 파일 경로 (.md)")
    parser.add_argument("--folder-id", default=os.environ.get("GOOGLE_DRIVE_FOLDER_ID", ""))
    args = parser.parse_args()

    secrets_path = os.environ.get("GOOGLE_CLIENT_SECRETS_PATH", "")
    token_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", os.path.expanduser("~/.google_token.json"))

    if not secrets_path:
        print("[WARNING] GOOGLE_CLIENT_SECRETS_PATH 미설정 — STUB 모드로 실행합니다.")

    if not os.path.exists(args.content):
        print(f"[ERROR] 콘텐츠 파일을 찾을 수 없습니다: {args.content}")
        sys.exit(1)

    with open(args.content, "r", encoding="utf-8") as f:
        content = f.read()

    # STUB: 실제 API 서비스 객체 생성 생략
    creds = get_credentials(secrets_path, token_path)
    # docs_service = build("docs", "v1", credentials=creds)
    # drive_service = build("drive", "v3", credentials=creds)

    doc_url = create_doc(None, None, args.title, content, args.folder_id)
    print(f"[OK] Google Docs URL: {doc_url}")

    # 결과를 파일로도 저장 (publisher가 참조)
    result_path = "output/google_doc_result.json"
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump({"title": args.title, "url": doc_url, "stub": True}, f, ensure_ascii=False, indent=2)

    print(f"[OK] 결과 저장: {result_path}")


if __name__ == "__main__":
    main()
