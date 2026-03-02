"""
Jira Skill — 이니셔티브 메타데이터 조회

사용법:
  python3 fetch_initiative.py --issue-key TM-2061
  python3 fetch_initiative.py --issue-key TM-2061 --output output/initiative_meta.json

출력 (initiative_meta.json):
  {
    "issue_key": "TM-2061",
    "project_key": "TM",
    "summary": "Campaign Meta Engine Phase 1",
    "labels": ["membership", "campaign"],
    "components": ["Backend"],
    "fix_versions": ["2026 Q1"],
    "priority": "High",
    "status": "In Progress"
  }
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import client

OUTPUT_DIR = Path(__file__).parents[4] / "output"


def fetch_initiative(issue_key: str) -> dict:
    """이니셔티브 이슈에서 공통 메타데이터를 추출한다."""
    data = client.get(f"/issue/{issue_key}?fields=summary,labels,components,fixVersions,priority,status,project,issuetype")

    fields = data.get("fields", {})

    # 라벨 추출
    labels = fields.get("labels", [])

    # 컴포넌트 이름 추출
    components = [c.get("name", "") for c in fields.get("components", []) if c.get("name")]

    # Fix Version 추출
    fix_versions = [v.get("name", "") for v in fields.get("fixVersions", []) if v.get("name")]

    # 우선순위
    priority_obj = fields.get("priority") or {}
    priority = priority_obj.get("name", "Medium")

    # 상태
    status_obj = fields.get("status") or {}
    status = status_obj.get("name", "")

    # 프로젝트 키
    project_obj = fields.get("project") or {}
    project_key = project_obj.get("key", client.get_project_key())

    result = {
        "issue_key": issue_key,
        "project_key": project_key,
        "summary": fields.get("summary", ""),
        "labels": labels,
        "components": components,
        "fix_versions": fix_versions,
        "priority": priority,
        "status": status,
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="Jira 이니셔티브 메타데이터 조회")
    parser.add_argument("--issue-key", "-k", required=True, help="Jira 이슈 키 (예: TM-2061)")
    parser.add_argument("--output", "-o", help="저장 경로 (미지정 시 stdout)")
    args = parser.parse_args()

    try:
        meta = fetch_initiative(args.issue_key)
    except RuntimeError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    output_json = json.dumps(meta, ensure_ascii=False, indent=2)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_json, encoding="utf-8")
        print(f"[OK] 저장 완료: {out_path}")
        print(f"     이슈: {meta['issue_key']} / 라벨: {meta['labels']} / 컴포넌트: {meta['components']}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
