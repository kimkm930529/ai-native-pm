#!/usr/bin/env python3
"""
fetch_braze.py — Braze GitHub Docs Fetcher
PDIS External Knowledge Connector: Braze

Fetches relevant documentation sections from Braze's public GitHub repo
(braze-inc/braze-docs) based on a topic keyword.

Usage:
    python3 fetch_braze.py --topic "push notifications" --limit 5
    python3 fetch_braze.py --topic "canvas segmentation" --output output/braze_ref.md
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime

GITHUB_SEARCH_API = "https://api.github.com/search/code"
REPO_FULL = "braze-inc/braze-docs"
RAW_BASE = "https://raw.githubusercontent.com/braze-inc/braze-docs/develop"

TOPIC_KEYWORD_MAP = {
    "push": ["push_notifications", "push", "fcm", "apns"],
    "in-app": ["in-app_messages", "in-app", "modal", "slideup"],
    "email": ["email", "deliverability", "unsubscribe"],
    "canvas": ["canvas", "journey", "workflow", "step"],
    "campaign": ["campaign", "messaging", "targeting"],
    "segment": ["segment", "audience", "filter", "attribute"],
    "personalization": ["personalization", "liquid", "connected_content", "catalog"],
    "crm": ["user_profile", "custom_attributes", "lifecycle"],
    "retention": ["retention", "win-back", "reengagement", "lapsed"],
}


def build_headers():
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "PDIS-Fetcher/1.0"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def search_docs(topic: str, limit: int = 5) -> list[dict]:
    """Search Braze docs via GitHub code search API."""
    keywords = []
    for key, vals in TOPIC_KEYWORD_MAP.items():
        if key in topic.lower():
            keywords.extend(vals[:2])
    if not keywords:
        keywords = topic.split()[:3]

    query = f"{' '.join(keywords[:3])} repo:{REPO_FULL} extension:md"
    url = f"{GITHUB_SEARCH_API}?q={urllib.parse.quote(query)}&per_page={limit}"

    req = urllib.request.Request(url, headers=build_headers())
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            return data.get("items", [])
    except Exception as e:
        print(f"[WARN] GitHub search failed: {e}", file=sys.stderr)
        return []


def fetch_file_content(path: str) -> str:
    """Fetch raw markdown content from Braze GitHub."""
    raw_url = f"{RAW_BASE}/{path}"
    req = urllib.request.Request(raw_url, headers={"User-Agent": "PDIS-Fetcher/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            return content[:3000] + ("\n...[truncated]" if len(content) > 3000 else "")
    except Exception as e:
        return f"[ERROR] Could not fetch content: {e}"


def strip_front_matter(content: str) -> str:
    """Remove YAML front matter from markdown."""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[end + 3:].strip()
    return content


def summarize_for_discovery(items: list[dict], topic: str) -> str:
    """Build a discovery-ready summary from fetched Braze docs."""
    lines = [
        f"# Braze 외부 레퍼런스 — {topic}",
        f"> 수집일: {datetime.now().strftime('%Y-%m-%d')} | 출처: github.com/braze-inc/braze-docs",
        "",
        "## 주요 참조 문서",
        "",
    ]

    for i, item in enumerate(items, 1):
        path = item.get("path", "")
        html_url = item.get("html_url", "")

        content = fetch_file_content(path)
        content = strip_front_matter(content)

        lines.append(f"### {i}. `{path}`")
        lines.append(f"[원본 링크]({html_url})")
        lines.append("")
        lines.append("**섹션 헤딩 미리보기:**")
        lines.append("```")
        headings = [l for l in content.split("\n") if l.startswith("#")][:8]
        lines.extend(headings if headings else content.split("\n")[:10])
        lines.append("```")
        lines.append("")

    lines += [
        "---",
        "## Discovery 시사점 (PM 추가 해석 필요)",
        "",
        f"- Braze는 `{topic}` 기능을 어떤 방식으로 구현·가이드하는가?",
        "- 무신사 CRM/마케팅 시스템과 비교했을 때 참고할 UX 패턴이나 정책은?",
        "- Canvas / 캠페인 설계 시 벤치마킹 포인트는?",
    ]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Fetch Braze docs for PDIS")
    parser.add_argument("--topic", required=True, help="탐색 주제 (예: push notifications, canvas, crm)")
    parser.add_argument("--limit", type=int, default=5, help="최대 문서 수 (기본: 5)")
    parser.add_argument("--output", help="출력 파일 경로 (미지정 시 stdout)")
    args = parser.parse_args()

    print(f"[INFO] Braze 문서 검색 중: {args.topic}", file=sys.stderr)
    items = search_docs(args.topic, args.limit)

    if not items:
        print(f"[WARN] '{args.topic}' 관련 Braze 문서를 찾지 못했습니다.", file=sys.stderr)
        result = f"# Braze 레퍼런스 — {args.topic}\n\n검색 결과 없음. 직접 https://www.braze.com/docs 에서 탐색 권장."
    else:
        print(f"[INFO] {len(items)}개 문서 발견, 내용 수집 중...", file=sys.stderr)
        result = summarize_for_discovery(items, args.topic)

    if args.output:
        os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"[OK] 저장 완료: {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()
