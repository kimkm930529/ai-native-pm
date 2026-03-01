"""
Confluence Tool — 공통 API 클라이언트

Auth, HTTP, 1회 자동 재시도, 로깅 담당.
search.py / upload.py 에서 import하여 사용.
"""

import os
import json
import base64
import time
import logging
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Optional

# ─── 로그 설정 ────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).parents[4] / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_FILE = OUTPUT_DIR / "confluence_skill.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("confluence-client")


# ─── 환경변수 ──────────────────────────────────────────────

def get_base_url() -> str:
    url = os.environ.get("CONFLUENCE_URL", "").rstrip("/")
    if not url:
        raise EnvironmentError("[AUTH ERROR] CONFLUENCE_URL 환경변수가 설정되지 않았습니다.")
    return url


def get_auth_header() -> str:
    email = os.environ.get("CONFLUENCE_EMAIL", "")
    token = os.environ.get("CONFLUENCE_API_TOKEN", "")
    if not email or not token:
        raise EnvironmentError(
            "[AUTH ERROR] CONFLUENCE_EMAIL 또는 CONFLUENCE_API_TOKEN 환경변수가 설정되지 않았습니다."
        )
    encoded = base64.b64encode(f"{email}:{token}".encode()).decode()
    return f"Basic {encoded}"


# ─── HTTP 요청 (1회 자동 재시도) ──────────────────────────

def request(
    method: str,
    path: str,
    body: Optional[dict] = None,
    retry: int = 1,
) -> dict:
    """
    Confluence REST API 호출.
    path는 /wiki/rest/api 이후 부분 (예: /space?limit=10)
    """
    base_url = get_base_url()
    # confluence_uploader.py는 /wiki/rest/api{path}를 사용
    # 여기서는 base_url에 /wiki가 이미 없으므로 직접 붙임
    if "/wiki" in base_url:
        url = f"{base_url}/rest/api{path}"
    else:
        url = f"{base_url}/wiki/rest/api{path}"

    auth = get_auth_header()
    data = json.dumps(body).encode("utf-8") if body else None
    headers = {
        "Authorization": auth,
        "Accept": "application/json",
    }
    if data:
        headers["Content-Type"] = "application/json; charset=utf-8"

    for attempt in range(retry + 1):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            logger.info(f"→ {method} {url}")
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                logger.info(f"← {resp.status} OK")
                return json.loads(raw) if raw.strip() else {}

        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            logger.warning(f"← HTTP {e.code} {e.reason}: {body_text[:300]}")

            if e.code == 401:
                raise RuntimeError(
                    f"[AUTH ERROR] Confluence API 토큰이 잘못되었거나 만료되었습니다. "
                    f"https://id.atlassian.com/manage-profile/security/api-tokens 에서 재발급 후 "
                    f"CONFLUENCE_API_TOKEN 환경변수를 업데이트하세요."
                ) from e

            if attempt < retry:
                logger.info(f"  재시도 중... ({attempt + 1}/{retry})")
                time.sleep(2)
                continue

            raise RuntimeError(f"HTTP {e.code} {e.reason}: {body_text[:400]}") from e

        except Exception as e:
            if attempt < retry:
                logger.info(f"  네트워크 오류, 재시도 중... ({attempt + 1}/{retry})")
                time.sleep(2)
                continue
            raise


def get(path: str) -> dict:
    return request("GET", path)


def post(path: str, body: dict) -> dict:
    return request("POST", path, body)


def put(path: str, body: dict) -> dict:
    return request("PUT", path, body)
