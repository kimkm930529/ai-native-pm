"""
Confluence Tool — 페이지 댓글 조회

사용법:
  python3 fetch_comments.py --page-id 216960895
  python3 fetch_comments.py --page-id 216960895 --output output/comments.md
  python3 fetch_comments.py --page-id 216960895 --json

출력:
  기본: 마크다운 형식 (작성자 / 날짜 / 내용)
  --json: 메타데이터 포함 JSON
  --output: 파일 저장
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import client

OUTPUT_DIR = Path(__file__).parents[4] / "output"


# ─── HTML → 텍스트 경량 변환 ─────────────────────────────────────────────

def html_to_text(html: str) -> str:
    text = html
    text = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", text, flags=re.DOTALL)
    text = re.sub(r"<em[^>]*>(.*?)</em>", r"*\1*", text, flags=re.DOTALL)
    text = re.sub(r"<code[^>]*>(.*?)</code>", r"`\1`", text, flags=re.DOTALL)
    text = re.sub(r"<li[^>]*>(.*?)</li>", r"- \1", text, flags=re.DOTALL)
    text = re.sub(r"<[uo]l[^>]*>|</[uo]l>", "", text)
    text = re.sub(r"<p[^>]*>", "", text)
    text = re.sub(r"</p>", "\n", text)
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<ac:[^>]+>.*?</ac:[^>]+>", "", text, flags=re.DOTALL)
    text = re.sub(r"<ac:[^>]+/>", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&amp;", "&").replace("&nbsp;", " ")
    text = text.replace("&quot;", '"').replace("&#39;", "'")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ─── 댓글 페치 ───────────────────────────────────────────────────────────

def fetch_comments(page_id: str) -> list[dict]:
    """
    페이지의 모든 댓글을 가져와 리스트로 반환.
    각 항목: { author, date, body, id }
    """
    start = 0
    limit = 50
    comments = []

    while True:
        data = client.get(
            f"/content/{page_id}/child/comment"
            f"?expand=body.storage,version,history"
            f"&limit={limit}&start={start}"
        )
        results = data.get("results", [])
        for r in results:
            author = (
                r.get("history", {})
                 .get("createdBy", {})
                 .get("displayName", "알 수 없음")
            )
            date = (
                r.get("history", {})
                 .get("createdDate", "")[:10]  # YYYY-MM-DD
            )
            html = r.get("body", {}).get("storage", {}).get("value", "")
            comments.append({
                "id": r.get("id", ""),
                "author": author,
                "date": date,
                "body": html_to_text(html),
            })

        if len(results) < limit:
            break
        start += limit

    return comments


def to_markdown(page_title: str, page_url: str, comments: list[dict]) -> str:
    lines = [f"# 댓글 목록 — {page_title}", f"URL: {page_url}", ""]
    for i, c in enumerate(comments, 1):
        lines.append(f"## [{i}] {c['author']} ({c['date']})")
        lines.append(c["body"])
        lines.append("")
    if not comments:
        lines.append("_댓글이 없습니다._")
    return "\n".join(lines)


# ─── CLI ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Confluence 페이지 댓글 조회")
    parser.add_argument("--page-id", "-p", required=True, help="Confluence 페이지 ID")
    parser.add_argument("--output", "-o", help="저장할 파일 경로 (미지정 시 stdout)")
    parser.add_argument("--json", action="store_true", help="JSON 형식으로 출력")
    args = parser.parse_args()

    # 페이지 제목 조회
    try:
        page_data = client.get(f"/content/{args.page_id}?expand=space")
        page_title = page_data.get("title", args.page_id)
        space_key = page_data.get("space", {}).get("key", "")
        base_url = client.get_base_url()
        page_url = f"{base_url}/wiki/spaces/{space_key}/pages/{args.page_id}"
    except RuntimeError as e:
        print(f"[ERROR] 페이지 조회 실패: {e}", file=sys.stderr)
        sys.exit(1)

    # 댓글 조회
    try:
        comments = fetch_comments(args.page_id)
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[OK] 댓글 {len(comments)}개 조회 완료 — {page_title}", file=sys.stderr)

    # 출력
    if args.json:
        output_text = json.dumps(
            {"page_id": args.page_id, "title": page_title, "url": page_url, "comments": comments},
            ensure_ascii=False, indent=2,
        )
    else:
        output_text = to_markdown(page_title, page_url, comments)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_text, encoding="utf-8")
        print(f"[OK] 저장 완료: {out_path}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == "__main__":
    main()
