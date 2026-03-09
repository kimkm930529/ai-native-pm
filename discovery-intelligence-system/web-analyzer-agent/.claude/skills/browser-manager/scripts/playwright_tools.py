"""
browser-manager/scripts/playwright_tools.py
Web Vision Analyzer — Playwright 브라우저 제어 유틸리티

사전 조건:
  pip install playwright pillow
  playwright install chromium
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, Page
except ImportError:
    print("ERROR: playwright가 설치되지 않았습니다.")
    print("설치 방법: pip install playwright && playwright install chromium")
    sys.exit(1)

SCREENSHOTS_DIR = os.environ.get("WVA_SCREENSHOTS_DIR", "output/screenshots")
USER_DATA_DIR = os.environ.get("WVA_USER_DATA_DIR", "/tmp/wva-browser-profile")


# ──────────────────────────────────────────
# 캡쳐 함수
# ──────────────────────────────────────────

def capture_full_page(page: Page, name: str, output_dir: str = SCREENSHOTS_DIR) -> str:
    """전체 페이지 스크롤 캡쳐. 저장 경로 반환."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")

    # 순번 결정 (기존 파일 수 기반)
    existing = list(Path(output_dir).glob(f"{date_str}_*.png"))
    seq = len(existing) + 1

    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    filename = f"{date_str}_{seq:03d}_{safe_name}.png"
    filepath = str(Path(output_dir) / filename)

    page.screenshot(path=filepath, full_page=True)
    return filepath


def capture_element(page: Page, selector: str, name: str, output_dir: str = SCREENSHOTS_DIR) -> str:
    """특정 요소 크롭 캡쳐. 저장 경로 반환."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    existing = list(Path(output_dir).glob(f"{date_str}_*.png"))
    seq = len(existing) + 1

    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
    filename = f"{date_str}_{seq:03d}_elem_{safe_name}.png"
    filepath = str(Path(output_dir) / filename)

    element = page.locator(selector).first
    element.screenshot(path=filepath)
    return filepath


# ──────────────────────────────────────────
# 로그인 처리
# ──────────────────────────────────────────

def detect_login_required(page: Page) -> dict:
    """로그인 필요 여부 및 유형 감지."""
    url = page.url
    content = page.content().lower()

    # Google OAuth 감지
    if "accounts.google.com" in url or "google.com/o/oauth2" in url:
        return {"required": True, "type": "google_oauth"}

    # 일반 로그인 폼 감지 (password 입력 필드 존재)
    password_input = page.locator("input[type='password']").count()
    if password_input > 0:
        return {"required": True, "type": "form"}

    # 로그인 링크 텍스트 감지
    login_keywords = ["로그인", "sign in", "log in", "login"]
    for kw in login_keywords:
        if f">{kw}<" in content or f"'{kw}'" in content:
            # 단순 링크인지 강제 리디렉션인지 추가 확인 필요
            pass

    return {"required": False, "type": "none"}


def interactive_pause(message: str = "브라우저에서 로그인 후 Enter를 눌러주세요.") -> None:
    """사용자 입력 대기 (Semi-Auto 로그인)."""
    print(f"\n{'='*60}")
    print(f"[WVA 대기] {message}")
    print("='*60}")
    input("로그인 완료 후 Enter: ")


# ──────────────────────────────────────────
# 네비게이션 추출
# ──────────────────────────────────────────

def extract_gnb(page: Page) -> list:
    """GNB(메인 네비게이션) 항목 추출."""
    # 일반적인 GNB 패턴: nav > a, header nav li a
    gnb_selectors = [
        "nav a",
        "header nav li a",
        "[role='navigation'] a",
        ".gnb a",
        ".nav a",
        "#gnb a",
    ]

    items = []
    for selector in gnb_selectors:
        elements = page.locator(selector).all()
        if len(elements) >= 3:  # 최소 3개 이상이면 GNB로 판단
            for el in elements[:20]:  # 최대 20개
                try:
                    text = el.inner_text().strip()
                    href = el.get_attribute("href") or ""
                    if text and len(text) < 50:  # 너무 긴 텍스트 제외
                        items.append({"text": text, "href": href, "selector": selector})
                except Exception:
                    continue
            if items:
                break

    return items


def click_and_wait(page: Page, selector: str, timeout_ms: int = 5000) -> bool:
    """요소 클릭 후 네트워크 안정화 대기."""
    try:
        page.locator(selector).first.click(timeout=timeout_ms)
        page.wait_for_load_state("networkidle", timeout=timeout_ms)
        return True
    except Exception as e:
        print(f"[WVA] 클릭 실패: {selector} — {e}")
        return False


# ──────────────────────────────────────────
# CLI 진입점
# ──────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="WVA Browser Manager")
    parser.add_argument("--action", required=True,
                        choices=["capture_full_page", "capture_element", "extract_gnb", "detect_login"],
                        help="실행할 액션")
    parser.add_argument("--url", help="대상 URL")
    parser.add_argument("--selector", help="CSS selector (capture_element용)")
    parser.add_argument("--name", default="screenshot", help="파일명 접미어")
    parser.add_argument("--output", default=SCREENSHOTS_DIR, help="출력 디렉토리")
    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,  # Semi-Auto 로그인을 위해 GUI 모드
            viewport={"width": 1280, "height": 900},
        )
        page = browser.pages[0] if browser.pages else browser.new_page()

        if args.url:
            page.goto(args.url, wait_until="networkidle", timeout=30000)

        result = {}

        if args.action == "capture_full_page":
            path = capture_full_page(page, args.name, args.output)
            result = {"path": path, "url": page.url}

        elif args.action == "capture_element":
            if not args.selector:
                print("ERROR: --selector 필요")
                sys.exit(1)
            path = capture_element(page, args.selector, args.name, args.output)
            result = {"path": path, "selector": args.selector}

        elif args.action == "extract_gnb":
            items = extract_gnb(page)
            result = {"gnb": items, "count": len(items)}

        elif args.action == "detect_login":
            result = detect_login_required(page)

        print(json.dumps(result, ensure_ascii=False, indent=2))
        browser.close()


if __name__ == "__main__":
    main()
