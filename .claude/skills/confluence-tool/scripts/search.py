"""
Confluence Tool — 문서 검색 스크립트

사용법:
  python3 search.py --query "검색어" [--space DEV] [--limit 10]
  python3 search.py --list-spaces

출력:
  JSON → stdout 및 output/context.json 저장
"""

import argparse
import json
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path

# scripts/ 디렉토리를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))
import client

OUTPUT_DIR = Path(__file__).parents[4] / "output"
CONTEXT_FILE = OUTPUT_DIR / "context.json"
SPACES_FILE = Path(__file__).parents[4] / "config" / "spaces.json"


def load_priority_spaces() -> list[str]:
    """config/spaces.json에서 Priority Space 목록 로드"""
    if SPACES_FILE.exists():
        with open(SPACES_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("priority", [])
    return []


def list_spaces(limit: int = 20) -> list[dict]:
    """접근 가능한 전체 Space 목록 조회"""
    result = client.get(f"/space?limit={limit}&type=global")
    spaces = []
    for s in result.get("results", []):
        spaces.append({
            "key": s.get("key"),
            "name": s.get("name"),
            "type": s.get("type"),
        })
    return spaces


def search_by_space(query: str, space_key: str, limit: int) -> list[dict]:
    """특정 Space에서 CQL 검색"""
    cql = f'text ~ "{query}" AND space = "{space_key}" ORDER BY lastModified DESC'
    encoded = urllib.parse.quote(cql)
    result = client.get(
        f"/content/search?cql={encoded}&limit={limit}"
        f"&expand=version,space,body.view"
    )
    return parse_results(result)


def search_global(query: str, limit: int) -> list[dict]:
    """전체 Space CQL 검색"""
    cql = f'text ~ "{query}" ORDER BY lastModified DESC'
    encoded = urllib.parse.quote(cql)
    result = client.get(
        f"/content/search?cql={encoded}&limit={limit}"
        f"&expand=version,space,body.view"
    )
    return parse_results(result)


def parse_results(api_result: dict) -> list[dict]:
    """API 응답에서 필요한 필드만 추출"""
    parsed = []
    for item in api_result.get("results", []):
        # excerpt 추출 (body.view.value 에서 HTML 태그 제거)
        body_val = ""
        try:
            body_val = item["body"]["view"]["value"]
            # 간단한 HTML 태그 제거
            import re
            body_val = re.sub(r"<[^>]+>", " ", body_val)
            body_val = " ".join(body_val.split())[:300]
        except (KeyError, TypeError):
            pass

        space_key = ""
        try:
            space_key = item["space"]["key"]
        except (KeyError, TypeError):
            pass

        base_url = client.get_base_url()
        page_url = f"{base_url}/wiki/spaces/{space_key}/pages/{item.get('id', '')}"

        parsed.append({
            "id": item.get("id", ""),
            "title": item.get("title", ""),
            "space": space_key,
            "url": page_url,
            "excerpt": body_val,
            "lastModified": item.get("version", {}).get("when", "")[:10],
        })
    return parsed


def save_context(query: str, results: list[dict], escalate: bool = False):
    """output/context.json에 검색 결과 저장"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    context = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "total": len(results),
        "escalate": escalate,
        "results": results,
    }
    with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
        json.dump(context, f, ensure_ascii=False, indent=2)
    return context


def main():
    parser = argparse.ArgumentParser(description="Confluence 문서 검색")
    parser.add_argument("--query", "-q", help="검색어")
    parser.add_argument("--space", "-s", help="Space 키 (미지정 시 priority 순서)")
    parser.add_argument("--limit", "-l", type=int, default=10, help="최대 결과 수 (기본: 10)")
    parser.add_argument("--list-spaces", action="store_true", help="접근 가능 Space 목록 출력")
    args = parser.parse_args()

    # ── Space 목록 조회 모드 ─────────────────────────────
    if args.list_spaces:
        spaces = list_spaces()
        print("\n접근 가능한 Confluence Space 목록:")
        print("-" * 45)
        for s in spaces:
            print(f"  [{s['key']:15s}] {s['name']}")
        print()
        sys.exit(0)

    if not args.query:
        parser.print_help()
        sys.exit(1)

    # ── 검색 실행 ────────────────────────────────────────
    results = []

    if args.space:
        # 특정 Space 지정
        results = search_by_space(args.query, args.space, args.limit)
    else:
        # Priority Space 순서대로 시도
        priority = load_priority_spaces()
        for space_key in priority:
            results = search_by_space(args.query, space_key, args.limit)
            if results:
                break

        # Priority Space 전부 0건이면 전체 검색
        if not results and priority:
            print(f"  Priority Space에서 결과 없음. 전체 Space 검색 시도...", file=sys.stderr)
            results = search_global(args.query, args.limit)

    escalate = len(results) == 0

    # ── 저장 및 출력 ─────────────────────────────────────
    context = save_context(args.query, results, escalate)
    print(json.dumps(context, ensure_ascii=False, indent=2))

    if escalate:
        print(
            "\n[ESCALATE] 검색 결과가 없습니다. "
            "오케스트레이터에게 타 부서 Space 검색 에스컬레이션을 권장합니다.",
            file=sys.stderr,
        )
        sys.exit(0)  # 결과 없음도 정상 종료 (escalate 플래그로 처리)


if __name__ == "__main__":
    main()
