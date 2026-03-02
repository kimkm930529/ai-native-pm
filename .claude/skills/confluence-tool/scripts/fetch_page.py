"""
Confluence Tool — 페이지 ID 기반 콘텐츠 페치

사용법:
  python3 fetch_page.py --page-id 216960895
  python3 fetch_page.py --page-id 216960895 --output output/epic_source.md
  python3 fetch_page.py --page-id 216960895 --format storage  # XHTML 원문
  python3 fetch_page.py --page-id 216960895 --format markdown  # 마크다운 변환 (기본)

출력:
  --output 지정 시 파일 저장, 미지정 시 stdout 출력
  JSON 형태로 메타데이터(제목, 공간, URL)도 함께 반환
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import client

OUTPUT_DIR = Path(__file__).parents[4] / "output"


# ─── Storage XHTML → Markdown 경량 변환 ──────────────────────────────────

def xhtml_to_markdown(xhtml: str) -> str:
    """Confluence Storage Format(XHTML)을 읽기 쉬운 마크다운으로 경량 변환."""
    text = xhtml

    # 구조화 태그 → 마크다운 제목
    text = re.sub(r"<h1[^>]*>(.*?)</h1>", r"# \1", text, flags=re.DOTALL)
    text = re.sub(r"<h2[^>]*>(.*?)</h2>", r"## \1", text, flags=re.DOTALL)
    text = re.sub(r"<h3[^>]*>(.*?)</h3>", r"### \1", text, flags=re.DOTALL)
    text = re.sub(r"<h4[^>]*>(.*?)</h4>", r"#### \1", text, flags=re.DOTALL)

    # 강조
    text = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", text, flags=re.DOTALL)
    text = re.sub(r"<em[^>]*>(.*?)</em>", r"*\1*", text, flags=re.DOTALL)
    text = re.sub(r"<code[^>]*>(.*?)</code>", r"`\1`", text, flags=re.DOTALL)

    # 목록
    text = re.sub(r"<li[^>]*>(.*?)</li>", r"- \1", text, flags=re.DOTALL)
    text = re.sub(r"<[uo]l[^>]*>|</[uo]l>", "", text)

    # 표 (간단 처리: 헤더 구분만)
    text = re.sub(r"<th[^>]*>(.*?)</th>", r"| **\1** ", text, flags=re.DOTALL)
    text = re.sub(r"<td[^>]*>(.*?)</td>", r"| \1 ", text, flags=re.DOTALL)
    text = re.sub(r"<tr[^>]*>", "", text)
    text = re.sub(r"</tr>", "|\n", text)
    text = re.sub(r"<t(?:head|body|foot)[^>]*>|</t(?:head|body|foot)>", "", text)
    text = re.sub(r"<table[^>]*>|</table>", "\n", text)

    # 단락 / 줄바꿈
    text = re.sub(r"<p[^>]*>", "", text)
    text = re.sub(r"</p>", "\n\n", text)
    text = re.sub(r"<br\s*/?>", "\n", text)

    # Confluence 매크로 / ac: 태그 제거
    text = re.sub(r"<ac:[^>]+>.*?</ac:[^>]+>", "", text, flags=re.DOTALL)
    text = re.sub(r"<ac:[^>]+/>", "", text)
    text = re.sub(r"<ri:[^>]+/>", "", text)

    # 나머지 HTML 태그 제거
    text = re.sub(r"<[^>]+>", "", text)

    # HTML 엔티티 디코딩
    text = text.replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&amp;", "&").replace("&nbsp;", " ")
    text = text.replace("&quot;", '"').replace("&#39;", "'")

    # 과도한 빈 줄 정리
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ─── 메인 페치 함수 ──────────────────────────────────────────────────────

def fetch_page(page_id: str, fmt: str = "markdown") -> dict:
    """
    페이지를 가져와 dict로 반환.
    {
      "id": "...",
      "title": "...",
      "space": "SPACEKEY",
      "url": "https://...",
      "content": "...",   ← fmt에 따라 markdown 또는 storage XHTML
    }
    """
    data = client.get(f"/content/{page_id}?expand=body.storage,space,version")

    base_url = client.get_base_url()
    space_key = data.get("space", {}).get("key", "")
    title = data.get("title", "")
    storage_html = data.get("body", {}).get("storage", {}).get("value", "")

    page_url = f"{base_url}/wiki/spaces/{space_key}/pages/{page_id}"

    content = xhtml_to_markdown(storage_html) if fmt == "markdown" else storage_html

    return {
        "id": page_id,
        "title": title,
        "space": space_key,
        "url": page_url,
        "content": content,
        "version": data.get("version", {}).get("number", 1),
    }


# ─── CLI ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Confluence 페이지 ID로 콘텐츠 페치")
    parser.add_argument("--page-id", "-p", required=True, help="Confluence 페이지 ID")
    parser.add_argument(
        "--format", "-f",
        choices=["markdown", "storage"],
        default="markdown",
        help="출력 형식 (기본: markdown)",
    )
    parser.add_argument("--output", "-o", help="저장할 파일 경로 (미지정 시 stdout)")
    parser.add_argument("--json", action="store_true", help="메타데이터 포함 JSON 출력")
    args = parser.parse_args()

    try:
        result = fetch_page(args.page_id, args.format)
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        output_text = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        output_text = result["content"]
        if not args.output:
            print(f"# {result['title']}")
            print(f"# URL: {result['url']}\n")

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) if args.json else output_text,
            encoding="utf-8",
        )
        print(f"[OK] 저장 완료: {out_path}")
        print(f"     제목: {result['title']}")
        print(f"     URL:  {result['url']}")
    else:
        print(output_text)


if __name__ == "__main__":
    main()
