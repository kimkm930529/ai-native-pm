#!/usr/bin/env python3
"""
search_shopify.py — Shopify App Store Scraper
PDIS External Knowledge Connector: Shopify

Scrapes the Shopify App Store to find top apps in a category/keyword,
useful for benchmarking e-commerce feature ecosystems and understanding
what third-party solutions dominate a given use case.

Usage:
    python3 search_shopify.py --query "loyalty rewards" --limit 3
    python3 search_shopify.py --category "marketing" --limit 5 --output output/shopify_ref.md
"""

import argparse
import html
import json
import os
import re
import sys
import urllib.request
import urllib.parse
from datetime import datetime

APP_STORE_BASE = "https://apps.shopify.com"
SEARCH_URL = "https://apps.shopify.com/search?q={query}"
CATEGORY_URL = "https://apps.shopify.com/categories/{category}"

# Shopify category slugs
CATEGORY_MAP = {
    "marketing": "marketing",
    "analytics": "store-data",
    "reviews": "product-reviews",
    "loyalty": "rewards-and-loyalty",
    "crm": "customer-accounts",
    "personalization": "product-recommendations",
    "social": "social-media",
    "email": "email-marketing",
    "push": "push-notifications",
    "inventory": "inventory-management",
}


def fetch_url(url: str) -> str:
    """Fetch HTML from a URL with browser-like headers."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"[WARN] URL 접근 실패 ({url}): {e}", file=sys.stderr)
        return ""


def extract_app_cards(html_content: str) -> list[dict]:
    """Extract app name, rating, review count, description from Shopify App Store HTML."""
    apps = []

    # Pattern: JSON-LD structured data (most reliable)
    json_ld_pattern = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)
    for match in json_ld_pattern.finditer(html_content):
        try:
            data = json.loads(match.group(1))
            if isinstance(data, dict) and data.get("@type") == "SoftwareApplication":
                app = {
                    "name": data.get("name", ""),
                    "description": data.get("description", "")[:300],
                    "rating": data.get("aggregateRating", {}).get("ratingValue", "N/A"),
                    "review_count": data.get("aggregateRating", {}).get("reviewCount", "N/A"),
                    "url": data.get("url", ""),
                    "price": data.get("offers", {}).get("price", "N/A"),
                }
                if app["name"]:
                    apps.append(app)
        except (json.JSONDecodeError, AttributeError):
            continue

    # Fallback: regex pattern matching for app titles
    if not apps:
        title_pattern = re.compile(r'<h2[^>]*class="[^"]*app-card__name[^"]*"[^>]*>([^<]+)</h2>')
        desc_pattern = re.compile(r'<p[^>]*class="[^"]*app-card__tagline[^"]*"[^>]*>([^<]+)</p>')

        titles = title_pattern.findall(html_content)
        descs = desc_pattern.findall(html_content)

        for i, title in enumerate(titles):
            apps.append({
                "name": html.unescape(title.strip()),
                "description": html.unescape(descs[i].strip()) if i < len(descs) else "",
                "rating": "N/A",
                "review_count": "N/A",
                "url": "",
                "price": "N/A",
            })

    return apps


def format_discovery_output(apps: list[dict], query: str, limit: int) -> str:
    """Format fetched apps as discovery-ready markdown."""
    apps = apps[:limit]

    lines = [
        f"# Shopify App Store 벤치마크 — {query}",
        f"> 수집일: {datetime.now().strftime('%Y-%m-%d')} | 출처: apps.shopify.com",
        "",
        f"## Top {len(apps)} 앱 ('{query}' 검색 기준)",
        "",
    ]

    for i, app in enumerate(apps, 1):
        lines.append(f"### {i}. {app['name']}")
        if app.get("url"):
            lines.append(f"[앱 링크]({app['url']})")
        lines.append("")
        lines.append(f"**설명:** {app['description']}")
        lines.append(f"**평점:** {app['rating']} ({''.join(['★'] * int(float(app['rating'])) if app['rating'] != 'N/A' else '—')})")
        lines.append(f"**리뷰 수:** {app['review_count']}")
        lines.append(f"**가격:** {app['price']}")
        lines.append("")

    lines += [
        "---",
        "## Discovery 시사점 (PM 추가 해석 필요)",
        "",
        f"- Shopify 생태계에서 `{query}` 문제를 어떻게 해결하고 있는가?",
        "- 무신사 파트너 앱/플러그인 전략과 비교했을 때 공백은?",
        "- 상위 앱들의 공통된 가치 제안(Value Proposition)은?",
        "- 기능 구현보다 생태계·파트너십 접근이 더 빠른 경로인가?",
    ]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Shopify App Store scraper for PDIS")
    parser.add_argument("--query", help="검색 키워드 (예: loyalty rewards, push notifications)")
    parser.add_argument("--category", help="카테고리 슬러그 (예: marketing, analytics, loyalty)")
    parser.add_argument("--limit", type=int, default=3, help="최대 앱 수 (기본: 3)")
    parser.add_argument("--output", help="출력 파일 경로 (미지정 시 stdout)")
    args = parser.parse_args()

    if not args.query and not args.category:
        parser.error("--query 또는 --category 중 하나가 필요합니다.")

    search_term = args.query or args.category

    if args.category:
        slug = CATEGORY_MAP.get(args.category.lower(), args.category.lower())
        url = CATEGORY_URL.format(category=slug)
        print(f"[INFO] Shopify 카테고리 탐색 중: {url}", file=sys.stderr)
    else:
        url = SEARCH_URL.format(query=urllib.parse.quote(args.query))
        print(f"[INFO] Shopify 앱스토어 검색 중: {args.query}", file=sys.stderr)

    html_content = fetch_url(url)

    if not html_content:
        result = f"# Shopify App Store — {search_term}\n\n페이지 접근 실패. 직접 {url} 에서 탐색 권장."
    else:
        apps = extract_app_cards(html_content)
        if not apps:
            result = (
                f"# Shopify App Store — {search_term}\n\n"
                f"앱 데이터 파싱 실패 (동적 렌더링 또는 구조 변경 가능성).\n"
                f"직접 {url} 에서 탐색 권장.\n\n"
                f"> 참고: Shopify App Store는 JavaScript 기반 렌더링을 사용하므로\n"
                f"> 정적 스크래핑이 제한될 수 있습니다."
            )
        else:
            print(f"[INFO] {len(apps)}개 앱 발견", file=sys.stderr)
            result = format_discovery_output(apps, search_term, args.limit)

    if args.output:
        os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"[OK] 저장 완료: {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()
