#!/usr/bin/env python3
"""
weekly_digest.py — 이번 주 Jira + Confluence 활동 수집 및 참고자료 생성

사용법:
  python3 scripts/weekly_digest.py
  python3 scripts/weekly_digest.py --week-offset -1   # 지난 주

환경변수 (Confluence와 동일 토큰 사용):
  CONFLUENCE_URL        https://musinsa-oneteam.atlassian.net
  CONFLUENCE_EMAIL      kyungmin.kim@musinsa.com
  CONFLUENCE_API_TOKEN  Atlassian API 토큰
"""

import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    print("[ERROR] requests 패키지가 필요합니다: pip install requests")
    sys.exit(1)


def get_week_range(week_offset=0):
    today = date.today()
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    sunday = monday + timedelta(days=6)
    end = min(today, sunday) if week_offset == 0 else sunday
    return monday.isoformat(), end.isoformat()


def jira_search(base_url, auth, jql, fields=None, max_results=100):
    if fields is None:
        fields = ["summary", "status", "priority", "assignee", "reporter",
                  "resolutiondate", "updated", "created", "labels", "issuetype", "parent",
                  "customfield_10016"]
    # Jira Cloud: POST /rest/api/3/search/jql (v3 GET deprecated → 410)
    url = f"{base_url}/rest/api/3/search/jql"
    payload = {"jql": jql, "maxResults": max_results, "fields": fields}
    r = requests.post(url, auth=auth,
                      headers={"Accept": "application/json", "Content-Type": "application/json"},
                      json=payload)
    r.raise_for_status()
    return r.json().get("issues", [])


def confluence_search(base_url, auth, cql, limit=30):
    url = f"{base_url}/wiki/rest/api/content/search"
    params = {"cql": cql, "limit": limit, "expand": "version,space,history"}
    r = requests.get(url, auth=auth, headers={"Accept": "application/json"}, params=params)
    r.raise_for_status()
    return r.json().get("results", [])


def format_jira_item(issue):
    f = issue["fields"]
    return {
        "key": issue["key"],
        "summary": f.get("summary", ""),
        "status": f.get("status", {}).get("name", ""),
        "priority": f.get("priority", {}).get("name", ""),
        "type": f.get("issuetype", {}).get("name", ""),
        "assignee": (f.get("assignee") or {}).get("displayName", "미배정"),
        "updated": (f.get("updated") or "")[:10],
        "resolved": (f.get("resolutiondate") or "")[:10],
        "labels": f.get("labels", []),
        "story_points": f.get("customfield_10016"),
        "parent": (f.get("parent") or {}).get("key", ""),
        "url": f"{base_url_global}/browse/{issue['key']}",
    }


def format_confluence_item(page):
    space = page.get("space", {})
    version = page.get("version", {})
    history = page.get("history", {})
    last_updated_by = (version.get("by") or {}).get("displayName", "")
    return {
        "id": page["id"],
        "title": page["title"],
        "space": space.get("key", ""),
        "space_name": space.get("name", ""),
        "last_modified": (version.get("when") or "")[:10],
        "last_modified_by": last_updated_by,
        "version": version.get("number", 1),
        "url": f"{base_url_global}/wiki{page.get('_links', {}).get('webui', '')}",
    }


base_url_global = ""


def main():
    global base_url_global

    parser = argparse.ArgumentParser()
    parser.add_argument("--week-offset", type=int, default=0)
    parser.add_argument("--output-dir", default="output")
    args = parser.parse_args()

    base_url = os.environ.get("CONFLUENCE_URL", "").rstrip("/")
    email = os.environ.get("CONFLUENCE_EMAIL", "")
    token = os.environ.get("CONFLUENCE_API_TOKEN", "")

    if not all([base_url, email, token]):
        print("[ERROR] 환경변수 미설정: CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN")
        sys.exit(1)

    base_url_global = base_url
    auth = HTTPBasicAuth(email, token)
    week_start, week_end = get_week_range(args.week_offset)
    today_str = date.today().strftime("%Y%m%d")

    print(f"\n{'='*60}")
    print(f"  이번 주 작업 정리: {week_start} ~ {week_end}")
    print(f"{'='*60}\n")

    # ── 1. Jira: 내가 담당하거나 보고한 티켓 ──────────────────────
    print("[1/3] Jira 티켓 수집 중...")
    jira_results = {"assigned": [], "reported": [], "commented": []}
    try:
        # 담당 티켓 (updatedDate 이번 주)
        jql_assigned = (
            f'assignee = currentUser() '
            f'AND updatedDate >= "{week_start}" '
            f'ORDER BY updated DESC'
        )
        assigned = jira_search(base_url, auth, jql_assigned)
        jira_results["assigned"] = [format_jira_item(i) for i in assigned]
        print(f"  담당 티켓: {len(jira_results['assigned'])}건")

        # 보고 티켓 (내가 만들었고 이번 주 업데이트)
        jql_reported = (
            f'reporter = currentUser() AND assignee != currentUser() '
            f'AND updatedDate >= "{week_start}" '
            f'ORDER BY updated DESC'
        )
        reported = jira_search(base_url, auth, jql_reported)
        jira_results["reported"] = [format_jira_item(i) for i in reported]
        print(f"  보고 티켓: {len(jira_results['reported'])}건")

    except requests.HTTPError as e:
        print(f"  [WARNING] Jira API 오류: {e}")

    # ── 2. Confluence: 내가 수정한 페이지 ────────────────────────
    print("[2/3] Confluence 페이지 수집 중...")
    confluence_results = {"updated": [], "created": []}
    try:
        # 내가 수정한 페이지
        cql_updated = (
            f'contributor = currentUser() '
            f'AND lastModified >= "{week_start}" '
            f'ORDER BY lastModified DESC'
        )
        updated_pages = confluence_search(base_url, auth, cql_updated, limit=50)
        confluence_results["updated"] = [format_confluence_item(p) for p in updated_pages]
        print(f"  수정한 페이지: {len(confluence_results['updated'])}건")

        # 내가 생성한 페이지
        cql_created = (
            f'creator = currentUser() '
            f'AND created >= "{week_start}" '
            f'ORDER BY created DESC'
        )
        created_pages = confluence_search(base_url, auth, cql_created, limit=20)
        confluence_results["created"] = [format_confluence_item(p) for p in created_pages]
        print(f"  생성한 페이지: {len(confluence_results['created'])}건")

    except requests.HTTPError as e:
        print(f"  [WARNING] Confluence API 오류: {e}")

    # ── 3. 마크다운 보고서 작성 ────────────────────────────────────
    print("[3/3] 참고자료 생성 중...")

    def status_icon(s):
        s = s.lower()
        if "done" in s or "완료" in s or "resolved" in s: return "✅"
        if "progress" in s or "in review" in s or "testing" in s: return "▶"
        if "block" in s or "hold" in s: return "🚫"
        return "⬜"

    lines = [
        f"# 이번 주 작업 정리 — {week_start} ~ {week_end}",
        f"\n> 생성일시: {date.today().isoformat()} | 담당자: {email}\n",
        "---\n",
    ]

    # Jira 섹션
    lines.append("## Jira — 담당 티켓\n")
    if jira_results["assigned"]:
        # 상태별 그룹
        status_order = {"Done": [], "In Progress": [], "In Review": [], "Testing": [], "Blocked": [], "기타": []}
        for item in jira_results["assigned"]:
            s = item["status"]
            if s in status_order:
                status_order[s].append(item)
            else:
                status_order["기타"].append(item)

        for status, items in status_order.items():
            if not items: continue
            lines.append(f"### {status_icon(status)} {status} ({len(items)}건)\n")
            for item in items:
                sp = f" `{item['story_points']}SP`" if item.get("story_points") else ""
                parent = f" ↑ {item['parent']}" if item.get("parent") else ""
                labels = f" [{', '.join(item['labels'])}]" if item.get("labels") else ""
                lines.append(f"- [{item['key']}]({item['url']}) **{item['summary']}**{sp}{parent}")
                lines.append(f"  - 우선순위: {item['priority']} | 유형: {item['type']} | 수정: {item['updated']}{labels}\n")
    else:
        lines.append("*이번 주 담당 티켓 없음*\n")

    if jira_results["reported"]:
        lines.append("\n## Jira — 내가 만든 티켓 (타인 담당)\n")
        for item in jira_results["reported"]:
            lines.append(f"- [{item['key']}]({item['url']}) {status_icon(item['status'])} **{item['summary']}**")
            lines.append(f"  - 담당: {item['assignee']} | 상태: {item['status']} | 수정: {item['updated']}\n")

    # Confluence 섹션
    lines.append("\n---\n")
    lines.append("## Confluence — 내가 수정한 페이지\n")
    if confluence_results["updated"]:
        by_space = {}
        for p in confluence_results["updated"]:
            key = f"{p['space_name']} ({p['space']})"
            by_space.setdefault(key, []).append(p)
        for space_name, pages in by_space.items():
            lines.append(f"### {space_name}\n")
            for p in pages:
                lines.append(f"- [{p['title']}]({p['url']})")
                lines.append(f"  - v{p['version']} | 수정: {p['last_modified']}\n")
    else:
        lines.append("*이번 주 수정한 페이지 없음*\n")

    if confluence_results["created"]:
        lines.append("\n## Confluence — 내가 생성한 페이지\n")
        for p in confluence_results["created"]:
            lines.append(f"- [{p['title']}]({p['url']})")
            lines.append(f"  - Space: {p['space_name']} | 생성: {p['last_modified']}\n")

    # 요약
    total_jira = len(jira_results["assigned"]) + len(jira_results["reported"])
    total_confluence = len(confluence_results["updated"]) + len(confluence_results["created"])
    done_count = sum(1 for i in jira_results["assigned"] if "done" in i["status"].lower())
    inprogress_count = sum(1 for i in jira_results["assigned"] if "progress" in i["status"].lower() or "review" in i["status"].lower() or "testing" in i["status"].lower())
    blocked_count = sum(1 for i in jira_results["assigned"] if "block" in i["status"].lower())

    lines.append("\n---\n")
    lines.append("## 이번 주 요약\n")
    lines.append(f"| 항목 | 수치 |")
    lines.append(f"|------|------|")
    lines.append(f"| Jira 담당 티켓 | {len(jira_results['assigned'])}건 (완료 {done_count} / 진행 {inprogress_count} / 블로킹 {blocked_count}) |")
    lines.append(f"| Jira 생성 티켓 (타인 담당) | {len(jira_results['reported'])}건 |")
    lines.append(f"| Confluence 수정 페이지 | {len(confluence_results['updated'])}건 |")
    lines.append(f"| Confluence 생성 페이지 | {len(confluence_results['created'])}건 |")
    lines.append(f"\n*이 문서는 weekly_digest.py가 자동 생성했습니다. `/pgm` 커맨드로 Flash Report 작성 시 참고하세요.*")

    # 파일 저장
    output_path = Path(args.output_dir) / f"weekly_digest_{today_str}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[OK] 참고자료 저장 완료 → {output_path}")

    # JSON raw 저장
    raw_path = Path(args.output_dir) / f"weekly_digest_raw_{today_str}.json"
    raw_data = {
        "week_range": {"start": week_start, "end": week_end},
        "jira": jira_results,
        "confluence": confluence_results,
    }
    raw_path.write_text(json.dumps(raw_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Raw 데이터 저장 완료 → {raw_path}")
    print(f"\n  Jira 총 {total_jira}건 | Confluence 총 {total_confluence}건\n")


if __name__ == "__main__":
    main()
