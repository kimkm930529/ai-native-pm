#!/usr/bin/env python3
"""
parse_jira.py — Jira REST API 호출 및 주간 티켓 수집 스크립트 (Stub)

환경변수:
  JIRA_BASE_URL     : Jira 인스턴스 URL (예: https://yourcompany.atlassian.net)
  JIRA_USER_EMAIL   : Jira 계정 이메일
  JIRA_API_TOKEN    : Jira API Token (Atlassian 계정 설정에서 발급)

사용법:
  python3 parse_jira.py --project MATCH --week-offset 0 --output output/jira_raw_20260305.json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, date


def get_week_range(week_offset: int = 0):
    """이번 주 월요일~오늘 범위를 반환 (week_offset=-1이면 지난 주)."""
    today = date.today()
    monday = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end = today + timedelta(weeks=week_offset) if week_offset == 0 else monday + timedelta(days=6)
    return monday.isoformat(), end.isoformat()


def build_jql(project: str, week_start: str, week_end: str, include_status: str) -> str:
    """Jira JQL 쿼리 생성."""
    statuses = ", ".join(f'"{s.strip()}"' for s in include_status.split(","))
    return (
        f'project = "{project}" '
        f'AND status in ({statuses}) '
        f'AND (resolved >= "{week_start}" OR status != "Done") '
        f'AND updatedDate >= "{week_start}" '
        f'ORDER BY priority DESC, updated DESC'
    )


def fetch_issues(base_url: str, email: str, token: str, jql: str) -> list:
    """
    Jira REST API v3 호출.

    STUB: 실제 API 호출 대신 샘플 데이터를 반환합니다.
    연동을 활성화하려면 아래 주석 처리된 코드를 사용하세요.
    필요 패키지: pip install requests
    """

    # --- 실제 API 호출 코드 (stub 해제 시 사용) ---
    # import requests
    # from requests.auth import HTTPBasicAuth
    #
    # auth = HTTPBasicAuth(email, token)
    # headers = {"Accept": "application/json"}
    # url = f"{base_url}/rest/api/3/search"
    # params = {"jql": jql, "maxResults": 100, "fields": [
    #     "summary", "status", "priority", "story_points",
    #     "assignee", "resolutiondate", "labels", "flagged",
    #     "issuelinks", "sprint", "customfield_10016"
    # ]}
    #
    # response = requests.get(url, headers=headers, auth=auth, params=params)
    # response.raise_for_status()
    # raw = response.json()
    #
    # issues = []
    # for item in raw.get("issues", []):
    #     f = item["fields"]
    #     issues.append({
    #         "key": item["key"],
    #         "summary": f.get("summary", ""),
    #         "status": {"name": f.get("status", {}).get("name", "")},
    #         "priority": {"name": f.get("priority", {}).get("name", "Medium")},
    #         "story_points": f.get("customfield_10016") or 0,
    #         "assignee": (f.get("assignee") or {}).get("displayName", ""),
    #         "resolved": f.get("resolutiondate"),
    #         "labels": f.get("labels", []),
    #         "flagged": f.get("flagged", False),
    #         "linked_issues": [
    #             {"key": link.get("outwardIssue", {}).get("key", ""),
    #              "type": link.get("type", {}).get("outward", "")}
    #             for link in f.get("issuelinks", [])
    #         ],
    #         "sprint": None  # sprint 필드는 프로젝트 설정에 따라 customfield 번호 다름
    #     })
    # return issues
    # --- stub 종료 ---

    # STUB 샘플 데이터
    print("[STUB] 실제 Jira API 호출 없이 샘플 데이터를 반환합니다.")
    print(f"[STUB] 연동 활성화: JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN 환경변수 설정 후 코드 주석 해제")
    return [
        {
            "key": "SAMPLE-001",
            "summary": "[STUB] 캠페인 메타 엔진 Phase 1 배포",
            "status": {"name": "Done"},
            "priority": {"name": "Highest"},
            "story_points": 8,
            "assignee": "홍길동",
            "resolved": datetime.now().isoformat(),
            "labels": ["weekly-flash", "okr"],
            "flagged": False,
            "linked_issues": [],
            "sprint": {"name": "Sprint 12", "start_date": "", "end_date": ""}
        },
        {
            "key": "SAMPLE-002",
            "summary": "[STUB] 데이터 익스플로러 QA 진행",
            "status": {"name": "In Progress"},
            "priority": {"name": "High"},
            "story_points": 5,
            "assignee": "김철수",
            "resolved": None,
            "labels": ["weekly-flash"],
            "flagged": False,
            "linked_issues": [],
            "sprint": {"name": "Sprint 12", "start_date": "", "end_date": ""}
        },
        {
            "key": "SAMPLE-003",
            "summary": "[STUB] Audience API 외부 연동 블로킹",
            "status": {"name": "Blocked"},
            "priority": {"name": "High"},
            "story_points": 3,
            "assignee": "이영희",
            "resolved": None,
            "labels": [],
            "flagged": True,
            "linked_issues": [{"key": "EXT-001", "type": "is blocked by"}],
            "sprint": {"name": "Sprint 12", "start_date": "", "end_date": ""}
        }
    ]


def main():
    parser = argparse.ArgumentParser(description="Jira 주간 티켓 수집기")
    parser.add_argument("--project", required=True, help="Jira 프로젝트 키 (예: MATCH)")
    parser.add_argument("--week-offset", type=int, default=0, help="0=이번 주, -1=지난 주")
    parser.add_argument("--output", default=f"output/jira_raw_{date.today().strftime('%Y%m%d')}.json")
    parser.add_argument("--include-status", default="Done,In Progress,In Review,Testing,Blocked")
    args = parser.parse_args()

    # 환경변수 확인
    base_url = os.environ.get("JIRA_BASE_URL", "")
    email = os.environ.get("JIRA_USER_EMAIL", "")
    token = os.environ.get("JIRA_API_TOKEN", "")

    if not all([base_url, email, token]):
        print("[WARNING] JIRA 환경변수 미설정 — STUB 모드로 실행합니다.")
        print("  필요 환경변수: JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN")

    week_start, week_end = get_week_range(args.week_offset)
    jql = build_jql(args.project, week_start, week_end, args.include_status)

    print(f"[INFO] 프로젝트: {args.project}")
    print(f"[INFO] 주간 범위: {week_start} ~ {week_end}")
    print(f"[INFO] JQL: {jql}")

    issues = fetch_issues(base_url, email, token, jql)

    result = {
        "fetched_at": datetime.now().isoformat(),
        "project": args.project,
        "week_range": {"start": week_start, "end": week_end},
        "issues": issues,
        "total": len(issues)
    }

    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[OK] {len(issues)}건 저장 완료 → {args.output}")


if __name__ == "__main__":
    main()
