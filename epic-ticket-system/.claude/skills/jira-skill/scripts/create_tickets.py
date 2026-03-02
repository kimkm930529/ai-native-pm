"""
Jira Skill — 에픽 티켓 일괄 생성

사용법:
  python3 create_tickets.py \
    --spec output/epic_spec_20260302_CampaignMetaEngine.json \
    --meta output/initiative_meta.json \
    --output output/jira_result_20260302_CampaignMetaEngine.json

처리 로직:
  1. epic_spec.json의 epics 배열을 순서대로 처리
  2. 각 에픽: 라벨 = 이니셔티브 라벨 + 직무 라벨 추가
  3. POST /rest/api/3/issue 로 Epic 이슈 생성
  4. 성공/실패 결과를 jira_result.json에 저장
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import client

OUTPUT_DIR = Path(__file__).parents[4] / "output"

# 직무별 추가 라벨 매핑
ROLE_LABELS = {
    "BE":  "backend",
    "FE":  "frontend",
    "MLE": "mle",
    "DS":  "data-science",
}

# 직무별 Jira 컴포넌트 매핑 (프로젝트마다 다를 수 있으므로 참고용)
ROLE_COMPONENTS = {
    "BE":  "Backend",
    "FE":  "Frontend",
    "MLE": "ML Engineering",
    "DS":  "Data Science",
}


def build_adf_description(epic: dict) -> dict:
    """
    에픽 description + AC를 Atlassian Document Format(ADF)으로 변환.
    ADF는 Jira Cloud가 요구하는 rich text 포맷.
    """
    content = []

    # 목적 설명 단락
    if epic.get("description"):
        content.append({
            "type": "paragraph",
            "content": [{"type": "text", "text": epic["description"]}],
        })

    # 공수 추정 근거
    if epic.get("effort_rationale"):
        content.append({
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "⏱ 공수 추정: ", "marks": [{"type": "strong"}]},
                {"type": "text", "text": epic["effort_rationale"]},
            ],
        })

    # AC 섹션
    acs = epic.get("acceptance_criteria", [])
    if acs:
        content.append({
            "type": "heading",
            "attrs": {"level": 3},
            "content": [{"type": "text", "text": "✅ AC (수락 기준)"}],
        })
        ac_items = [
            {
                "type": "listItem",
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": ac}]}
                ],
            }
            for ac in acs
        ]
        content.append({"type": "bulletList", "content": ac_items})

    # 의존성
    deps = epic.get("dependencies", [])
    if deps:
        content.append({
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "🔗 선행 에픽: ", "marks": [{"type": "strong"}]},
                {"type": "text", "text": ", ".join(deps)},
            ],
        })

    return {"type": "doc", "version": 1, "content": content}


def create_epic(epic: dict, meta: dict, project_key: str) -> dict:
    """단일 에픽 티켓 생성. 생성된 이슈 key와 URL 반환."""
    base_url = client.get_base_url()
    role = epic.get("role", "BE")

    # 라벨: 이니셔티브 라벨 전부 상속 + 직무 라벨 추가
    labels = list(meta.get("labels", []))
    role_label = ROLE_LABELS.get(role)
    if role_label and role_label not in labels:
        labels.append(role_label)

    # 우선순위
    priority_name = epic.get("priority", "Medium")

    # 날짜
    start_date = epic.get("start_date", "")
    due_date = epic.get("due_date", "")

    fields: dict = {
        "project": {"key": project_key},
        "issuetype": {"name": "Epic"},
        "summary": epic["title"],
        "description": build_adf_description(epic),
        "priority": {"name": priority_name},
        "labels": labels,
    }

    if due_date:
        fields["duedate"] = due_date

    # Start date (customfield_10015 is standard for Jira Next-gen / Team-managed)
    if start_date:
        fields["customfield_10015"] = start_date

    result = client.post("/issue", {"fields": fields})
    issue_key = result.get("key", "")
    issue_url = f"{base_url}/browse/{issue_key}"

    return {
        "role": role,
        "title": epic["title"],
        "issue_key": issue_key,
        "url": issue_url,
        "start_date": start_date,
        "due_date": due_date,
    }


def main():
    parser = argparse.ArgumentParser(description="epic_spec.json → Jira 에픽 티켓 일괄 생성")
    parser.add_argument("--spec", "-s", required=True, help="epic_spec.json 경로")
    parser.add_argument("--meta", "-m", required=True, help="initiative_meta.json 경로")
    parser.add_argument("--output", "-o", required=True, help="jira_result.json 저장 경로")
    parser.add_argument("--dry-run", action="store_true", help="실제 생성 없이 요청 페이로드만 출력")
    args = parser.parse_args()

    # ── 입력 파일 로드 ───────────────────────────────────────
    spec_path = Path(args.spec)
    meta_path = Path(args.meta)

    if not spec_path.exists():
        print(f"[ERROR] spec 파일 없음: {spec_path}", file=sys.stderr)
        sys.exit(1)
    if not meta_path.exists():
        print(f"[ERROR] meta 파일 없음: {meta_path}", file=sys.stderr)
        sys.exit(1)

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    project_key = meta.get("project_key") or client.get_project_key()
    epics = spec.get("epics", [])

    if not epics:
        print("[WARN] 생성할 에픽이 없습니다.", file=sys.stderr)
        sys.exit(0)

    print(f"[INFO] 총 {len(epics)}개 에픽 생성 시작 (프로젝트: {project_key})")

    # ── 에픽 생성 ────────────────────────────────────────────
    created = []
    failed = []

    for i, epic in enumerate(epics, 1):
        title = epic.get("title", f"에픽 {i}")
        print(f"  [{i}/{len(epics)}] {title} 생성 중...", end=" ")

        if args.dry_run:
            print("(dry-run: 스킵)")
            created.append({"role": epic.get("role"), "title": title, "issue_key": "DRY-RUN", "url": ""})
            continue

        try:
            result = create_epic(epic, meta, project_key)
            created.append(result)
            print(f"✅ {result['issue_key']}")
        except RuntimeError as e:
            error_msg = str(e)
            print(f"❌ 실패: {error_msg[:100]}")
            failed.append({"role": epic.get("role"), "title": title, "error": error_msg})

    # ── 결과 저장 ────────────────────────────────────────────
    result_data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "topic": spec.get("topic", ""),
        "initiative_key": spec.get("initiative_key", ""),
        "project_key": project_key,
        "created": created,
        "failed": failed,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result_data, ensure_ascii=False, indent=2), encoding="utf-8")

    # ── 최종 요약 ────────────────────────────────────────────
    print(f"\n✅ 완료: {len(created)}개 생성 / {len(failed)}개 실패")
    print(f"📁 결과: {out_path}")

    if created:
        print("\n🔗 생성된 티켓:")
        for t in created:
            print(f"  [{t['role']}] {t['title']} → {t.get('url') or t.get('issue_key')}")

    if failed:
        print("\n⚠️ 실패 항목:")
        for f in failed:
            print(f"  [{f['role']}] {f['title']} — {f['error'][:80]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
