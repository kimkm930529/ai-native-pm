"""
Jira Skill — 공통 API 클라이언트

Confluence와 동일한 Atlassian 계정(CONFLUENCE_URL/EMAIL/API_TOKEN)을 사용.
Jira REST API v3 엔드포인트 호출 담당.
"""

import os
import json
import base64
import time
import logging
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# ─── 로그 설정 ────────────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).parents[4] / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_FILE = OUTPUT_DIR / "jira_skill.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("jira-client")


# ─── 환경변수 ──────────────────────────────────────────────────────────────

def get_base_url() -> str:
    """Atlassian 도메인. Confluence와 동일한 CONFLUENCE_URL 환경변수 사용."""
    url = os.environ.get("CONFLUENCE_URL", "").rstrip("/")
    if not url:
        raise EnvironmentError(
            "[AUTH ERROR] CONFLUENCE_URL 환경변수가 설정되지 않았습니다. "
            "(Jira와 Confluence는 동일한 Atlassian 도메인을 사용합니다.)"
        )
    # /wiki 경로가 포함된 경우 도메인만 추출
    parsed = urlparse(url)
    if parsed.path.startswith("/wiki"):
        return f"{parsed.scheme}://{parsed.netloc}"
    return url


def get_project_key() -> str:
    key = os.environ.get("JIRA_PROJECT_KEY", "")
    if not key:
        raise EnvironmentError(
            "[CONFIG ERROR] JIRA_PROJECT_KEY 환경변수가 설정되지 않았습니다. "
            "예: export JIRA_PROJECT_KEY='TM'"
        )
    return key


def get_auth_header() -> str:
    email = os.environ.get("CONFLUENCE_EMAIL", "")
    token = os.environ.get("CONFLUENCE_API_TOKEN", "")
    if not email or not token:
        raise EnvironmentError(
            "[AUTH ERROR] CONFLUENCE_EMAIL 또는 CONFLUENCE_API_TOKEN 환경변수가 설정되지 않았습니다."
        )
    encoded = base64.b64encode(f"{email}:{token}".encode()).decode()
    return f"Basic {encoded}"


# ─── HTTP 요청 (1회 자동 재시도) ──────────────────────────────────────────

def request(
    method: str,
    path: str,
    body: Optional[dict] = None,
    retry: int = 1,
) -> dict:
    """
    Jira REST API v3 호출.
    path는 /rest/api/3 이후 부분 (예: /issue/TM-2061)
    """
    base_url = get_base_url()
    url = f"{base_url}/rest/api/3{path}"
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
                    "[AUTH ERROR] Atlassian API 토큰이 잘못되었거나 만료되었습니다. "
                    "https://id.atlassian.com/manage-profile/security/api-tokens 에서 재발급 후 "
                    "CONFLUENCE_API_TOKEN 환경변수를 업데이트하세요."
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
