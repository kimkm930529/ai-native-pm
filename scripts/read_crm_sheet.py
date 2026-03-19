"""
Google Spreadsheet → raw_df 로드 스크립트
대상 시트: CRM대시보드_채널별실적

인증 우선순위:
  1. Colab 환경 → google.colab.auth (팝업 로그인)
  2. 서비스 계정 JSON → GOOGLE_SERVICE_ACCOUNT_FILE 환경변수
"""

import os
import pandas as pd
import gspread

SPREADSHEET_ID = "1TAtR2t9kmvPV6C7UQ4NqTAAbG7hMFCKbXPeG179nhks"
SHEET_NAME = "CRM대시보드_채널별실적"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def _get_client() -> gspread.Client:
    """환경에 맞는 gspread 클라이언트를 반환합니다."""
    # 1) Colab 환경
    try:
        from google.colab import auth
        from google.auth import default

        auth.authenticate_user()
        creds, _ = default(scopes=SCOPES)
        return gspread.authorize(creds)
    except ImportError:
        pass  # Colab 아님 → 서비스 계정으로 폴백

    # 2) 서비스 계정 JSON
    from google.oauth2.service_account import Credentials

    sa_file = os.environ.get(
        "GOOGLE_SERVICE_ACCOUNT_FILE",
        os.path.expanduser("~/.config/gcloud/service_account.json"),
    )
    creds = Credentials.from_service_account_file(sa_file, scopes=SCOPES)
    return gspread.authorize(creds)


def load_raw_df(
    spreadsheet_id: str = SPREADSHEET_ID,
    sheet_name: str = SHEET_NAME,
) -> pd.DataFrame:
    client = _get_client()
    worksheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    records = worksheet.get_all_records(empty2zero=False, head=1)
    return pd.DataFrame(records)


# ── 실행 ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    raw_df = load_raw_df()

    print(f"Shape   : {raw_df.shape}")
    print(f"Columns : {raw_df.columns.tolist()}")
    print(raw_df.head(10).to_string(index=False))
