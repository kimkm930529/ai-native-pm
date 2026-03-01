"""
Confluence Tool — 페이지 업로드 스크립트

사용법:
  python3 upload.py --title "페이지 제목" --space SPACE_KEY [--parent-id 12345]
                    [--draft output/draft.html]

사전 조건: output/draft.html 에 Confluence Storage Format(XHTML)이 저장되어 있어야 함.
"""

import argparse
import json
import sys
import urllib.parse
from pathlib import Path
from typing import Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))
import client

OUTPUT_DIR = Path(__file__).parents[4] / "output"
DEFAULT_DRAFT = OUTPUT_DIR / "draft.html"


# ─── 페이지 조회 ──────────────────────────────────────────

def find_page(space_key: str, title: str) -> Tuple[Optional[str], Optional[int]]:
    """동일 제목 페이지 검색 → (page_id, version_number) 또는 (None, None)"""
    encoded = urllib.parse.quote(title)
    try:
        result = client.get(
            f"/content?spaceKey={space_key}&title={encoded}&expand=version"
        )
        results = result.get("results", [])
        if results:
            page = results[0]
            return page["id"], page["version"]["number"]
    except Exception:
        pass
    return None, None


# ─── 페이지 생성 ──────────────────────────────────────────

def create_page(
    space_key: str,
    title: str,
    storage_html: str,
    parent_id: Optional[str],
) -> dict:
    body: dict = {
        "type": "page",
        "title": title,
        "space": {"key": space_key},
        "body": {
            "storage": {
                "value": storage_html,
                "representation": "storage",
            }
        },
    }
    if parent_id:
        body["ancestors"] = [{"id": str(parent_id)}]
    return client.post("/content", body)


# ─── 페이지 업데이트 ──────────────────────────────────────

def update_page(
    page_id: str,
    title: str,
    storage_html: str,
    version: int,
) -> dict:
    body = {
        "type": "page",
        "title": title,
        "version": {"number": version + 1},
        "body": {
            "storage": {
                "value": storage_html,
                "representation": "storage",
            }
        },
    }
    return client.put(f"/content/{page_id}", body)


# ─── 메인 ─────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Confluence 페이지 업로드")
    parser.add_argument("--title", "-t", required=True, help="페이지 제목")
    parser.add_argument("--space", "-s", required=True, help="Space 키")
    parser.add_argument("--parent-id", "-p", help="부모 페이지 ID (선택)")
    parser.add_argument(
        "--draft",
        "-d",
        default=str(DEFAULT_DRAFT),
        help=f"draft HTML 경로 (기본: {DEFAULT_DRAFT})",
    )
    args = parser.parse_args()

    # ── draft.html 읽기 ────────────────────────────────────
    draft_path = Path(args.draft)
    if not draft_path.exists():
        print(f"[ERROR] draft 파일이 없습니다: {draft_path}", file=sys.stderr)
        sys.exit(1)

    storage_html = draft_path.read_text(encoding="utf-8").strip()
    if not storage_html:
        print("[ERROR] draft 파일이 비어 있습니다.", file=sys.stderr)
        sys.exit(1)

    # ── 중복 페이지 확인 ───────────────────────────────────
    base_url = client.get_base_url()
    page_id, version = find_page(args.space, args.title)

    try:
        if page_id:
            # 업데이트
            result = update_page(page_id, args.title, storage_html, version)
            new_version = version + 1
            page_url = f"{base_url}/wiki/spaces/{args.space}/pages/{page_id}"
            print(f"[UPDATE] 페이지 업데이트 완료 (버전: {version} → {new_version})")
        else:
            # 신규 생성
            result = create_page(args.space, args.title, storage_html, args.parent_id)
            new_id = result.get("id", "")
            page_url = f"{base_url}/wiki/spaces/{args.space}/pages/{new_id}"
            print(f"[CREATE] 페이지 생성 완료")

        print(f"URL: {page_url}")

        # 결과를 output/upload_result.json에 저장
        OUTPUT_DIR.mkdir(exist_ok=True)
        result_path = OUTPUT_DIR / "upload_result.json"
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "title": args.title,
                    "space": args.space,
                    "url": page_url,
                    "action": "update" if page_id else "create",
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

    except RuntimeError as e:
        print(f"[ERROR] 업로드 실패: {e}", file=sys.stderr)
        print(
            f"  draft 파일은 {draft_path}에 보존되어 있습니다. 수동 업로드 가능.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
