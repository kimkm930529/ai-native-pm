#!/usr/bin/env python3
"""
staff_sessions.jsonl → Google Calendar CSV (30분 단위 타임블럭)

Usage:
  python3 scripts/generate_calendar_csv.py
  python3 scripts/generate_calendar_csv.py --from 2026-03-24
  python3 scripts/generate_calendar_csv.py --from 2026-03-24 --output output/logs/my_calendar.csv
"""
import csv
import json
import math
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))
LOG_PATH = Path(__file__).parent.parent / "output" / "logs" / "staff_sessions.jsonl"


def floor_to_30min(dt: datetime) -> datetime:
    """30분 단위로 내림"""
    if dt.minute < 30:
        return dt.replace(minute=0, second=0, microsecond=0)
    return dt.replace(minute=30, second=0, microsecond=0)


def main():
    parser = argparse.ArgumentParser(description="staff 세션 → 캘린더 CSV 생성")
    parser.add_argument("--from", dest="from_date", default="2026-03-24",
                        help="집계 시작일 (YYYY-MM-DD, 기본: 2026-03-24)")
    parser.add_argument("--output", default=None, help="출력 CSV 경로")
    args = parser.parse_args()

    from_dt = datetime.strptime(args.from_date, "%Y-%m-%d").replace(tzinfo=KST)

    if args.output:
        out_path = Path(args.output)
    else:
        date_str = args.from_date.replace("-", "")
        out_path = Path(__file__).parent.parent / "output" / "logs" / f"staff_calendar_{date_str}.csv"

    # JSONL 로드 및 중복 제거 (같은 id는 마지막 기록 우선)
    session_map = {}
    if LOG_PATH.exists():
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    session_map[entry["id"]] = entry
                except (json.JSONDecodeError, KeyError):
                    pass

    # 날짜 필터 및 정렬
    sessions = sorted(session_map.values(), key=lambda x: x["start_ts"])
    sessions = [
        s for s in sessions
        if datetime.fromisoformat(s["start_ts"]) >= from_dt
    ]

    rows = []
    for s in sessions:
        start_dt = datetime.fromisoformat(s["start_ts"])

        # 소요 시간 계산 (end_ts 없으면 30분 기본)
        if s.get("end_ts"):
            end_dt = datetime.fromisoformat(s["end_ts"])
            duration_min = max(1, (end_dt - start_dt).total_seconds() / 60)
        else:
            duration_min = 30

        blocks = max(1, math.ceil(duration_min / 30))
        start_block = floor_to_30min(start_dt)
        end_block = start_block + timedelta(minutes=30 * blocks)

        # 제목: summary 우선, 없으면 request 앞 60자
        raw_title = s.get("summary") or s.get("request", "작업")
        title = raw_title[:60] + ("..." if len(raw_title) > 60 else "")

        skills_str = ", ".join(s.get("skills", []))
        outputs_str = ", ".join(s.get("outputs", []))
        desc_parts = []
        if skills_str:
            desc_parts.append(f"스킬: {skills_str}")
        if outputs_str:
            desc_parts.append(f"산출물: {outputs_str}")
        if s.get("request"):
            desc_parts.append(f"요청: {s['request'][:300]}")
        description = " | ".join(desc_parts)

        rows.append({
            "Subject": title,
            "Start Date": start_block.strftime("%m/%d/%Y"),
            "Start Time": start_block.strftime("%I:%M %p"),
            "End Date": end_block.strftime("%m/%d/%Y"),
            "End Time": end_block.strftime("%I:%M %p"),
            "All Day Event": "False",
            "Description": description,
            "Location": "",
            "Private": "True"
        })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["Subject", "Start Date", "Start Time", "End Date", "End Time",
                  "All Day Event", "Description", "Location", "Private"]

    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ CSV 생성 완료: {out_path}")
    print(f"   총 {len(rows)}개 이벤트 ({args.from_date} 이후)")


if __name__ == "__main__":
    main()
