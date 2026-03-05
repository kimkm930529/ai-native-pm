#!/usr/bin/env python3
"""
generate_md.py — Weekly Flash 마크다운 파일 생성 스크립트

사용법:
  python3 generate_md.py \
    --input output/analysed_report.json \
    --template config.json \
    --output output/flash_20260305.md
"""

import argparse
import json
import os
import sys
from datetime import datetime


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def render_achievements(items: list) -> str:
    if not items:
        return "_이번 주 완료된 항목 없음_\n"
    lines = []
    for item in items:
        prefix = "⭐ " if item.get("is_featured") else ""
        key = item.get("key", "")
        summary = item.get("summary", "")
        highlight = item.get("highlight", "")
        sp = item.get("story_points", 0)
        if item.get("is_featured"):
            lines.append(f"- {prefix}**[{key}] {summary}** — {highlight} *(SP: {sp})*")
        else:
            lines.append(f"- [{key}] {summary} — {highlight} *(SP: {sp})*")
    return "\n".join(lines) + "\n"


def render_status(items: list) -> str:
    if not items:
        return "_진행 중인 항목 없음_\n"
    lines = []
    for item in items:
        key = item.get("key", "")
        summary = item.get("summary", "")
        note = item.get("progress_note", "")
        status = item.get("status_name", "")
        if item.get("is_featured"):
            lines.append(f"- ▶ **[{key}] {summary}** `{status}` — {note}")
        else:
            lines.append(f"- [{key}] {summary} `{status}`" + (f" — {note}" if note else ""))
    return "\n".join(lines) + "\n"


def render_next_week(items: list) -> str:
    if not items:
        return "_다음 주 계획 항목 없음_\n"
    lines = []
    for item in items:
        key = item.get("key", "")
        summary = item.get("summary", "")
        if item.get("is_featured"):
            lines.append(f"- **[{key}] {summary}**")
        else:
            lines.append(f"- [{key}] {summary}")
    return "\n".join(lines) + "\n"


def render_blocks(items: list) -> str:
    if not items:
        return ""  # Blocks 0건이면 섹션 생략
    lines = []
    for item in items:
        key = item.get("key", "")
        summary = item.get("summary", "")
        reason = item.get("block_reason", "")
        owner = item.get("owner", "")
        owner_str = f" (담당: {owner})" if owner else ""
        lines.append(f"- 🚫 **[{key}] {summary}**{owner_str} — {reason}")
    return "\n".join(lines) + "\n"


def render_memo_items(items: list, category: str) -> str:
    """특정 카테고리의 메모 항목을 렌더링 (해당 섹션에 병합)."""
    relevant = [i for i in items if i.get("category") == category]
    if not relevant:
        return ""
    lines = []
    for item in relevant:
        text = item.get("text", "")
        if item.get("is_featured"):
            lines.append(f"- ⭐ **{text}** _(메모)_")
        else:
            lines.append(f"- {text} _(메모)_")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Weekly Flash 마크다운 생성기")
    parser.add_argument("--input", default="output/analysed_report.json")
    parser.add_argument("--template", default="config.json")
    parser.add_argument("--output", default=f"output/flash_{datetime.now().strftime('%Y%m%d')}.md")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[ERROR] 분석 결과 파일을 찾을 수 없습니다: {args.input}")
        sys.exit(1)

    data = load_json(args.input)
    config = load_json(args.template) if os.path.exists(args.template) else {}

    stats = data.get("summary_stats", {})
    week = data.get("week", "")
    achievements = data.get("achievements", [])
    status_items = data.get("status", [])
    next_week = data.get("next_week", [])
    blocks = data.get("blocks", [])
    memo_items = data.get("memo_items", [])

    total_done = stats.get("total_done", len(achievements))
    total_in_progress = stats.get("total_in_progress", len(status_items))
    total_blocks = stats.get("total_blocks", len(blocks))
    done_sp = stats.get("done_story_points", sum(a.get("story_points", 0) for a in achievements))

    # 날짜 포맷
    today_str = datetime.now().strftime("%Y년 %m월 %d일")

    lines = [
        f"# Weekly Flash — {today_str} 주간 보고",
        "",
        f"> 완료 **{total_done}건** (SP: **{done_sp}**) | 진행 중 {total_in_progress}건 | 블로킹 {total_blocks}건",
        f"> 보고 주간: {week}",
        "",
        "---",
        "",
        f"## ✅ 성과 (총 {done_sp} SP 완료)",
        "",
    ]

    lines.append(render_achievements(achievements))
    ach_memo = render_memo_items(memo_items, "achievements")
    if ach_memo:
        lines.append(ach_memo)

    lines += ["## ▶ 진행 현황", ""]
    lines.append(render_status(status_items))
    status_memo = render_memo_items(memo_items, "status")
    if status_memo:
        lines.append(status_memo)

    lines += ["## 📋 다음 주 계획", ""]
    lines.append(render_next_week(next_week))
    plan_memo = render_memo_items(memo_items, "next_week")
    if plan_memo:
        lines.append(plan_memo)

    blocks_md = render_blocks(blocks)
    if blocks_md:
        lines += ["## 🚫 이슈 / 블로킹", ""]
        lines.append(blocks_md)
        blocks_memo = render_memo_items(memo_items, "blocks")
        if blocks_memo:
            lines.append(blocks_memo)

    lines += [
        "---",
        f"*Auto-generated by pgm-agent-system — {datetime.now().strftime('%Y-%m-%d %H:%M')}*"
    ]

    content = "\n".join(lines)

    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)

    # 검증: 볼드 패턴 확인
    if "**" not in content:
        print("[WARNING] 볼드 처리된 항목이 없습니다. analyst 결과를 확인하세요.")

    # 검증: 카테고리 헤더 확인
    required_headers = ["## ✅ 성과", "## ▶ 진행 현황", "## 📋 다음 주 계획"]
    missing = [h for h in required_headers if h not in content]
    if missing:
        print(f"[WARNING] 누락된 섹션: {missing}")

    print(f"[OK] 마크다운 생성 완료 → {args.output}")
    print(f"[OK] 파일 크기: {len(content)}자")


if __name__ == "__main__":
    main()
