#!/usr/bin/env python3
"""
staff_sessions.jsonl (또는 CSV) → calendar.ics
모든 일정 앞에 [업무] 접두사를 붙여 생성.

Usage:
  # JSONL에서 직접 생성 (권장)
  python3 scripts/generate_ics.py
  python3 scripts/generate_ics.py --from 2026-03-24

  # CSV에서 생성
  python3 scripts/generate_ics.py --input output/logs/staff_calendar_20260324.csv

  # 출력 경로 지정
  python3 scripts/generate_ics.py --from 2026-03-24 --output output/logs/staff_calendar.ics
"""
import csv
import json
import math
import uuid
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))
LOG_PATH = Path(__file__).parent.parent / "output" / "logs" / "staff_sessions.jsonl"


# ── ICS 유틸 ──────────────────────────────────────────────────────────────────

def dt_to_ics(dt: datetime) -> str:
    return dt.strftime("%Y%m%dT%H%M%S")


def escape_ics(text: str) -> str:
    if not text:
        return ""
    text = str(text)
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;")
    text = text.replace(",", "\\,")
    text = text.replace("\n", "\\n")
    text = text.replace("\r", "")
    return text


def fold_line(line: str) -> str:
    """ICS RFC 5545 — 75바이트 초과 시 줄 접기"""
    result = []
    encoded = line.encode("utf-8")
    while len(encoded) > 75:
        cut = 75
        # UTF-8 멀티바이트 경계 보호
        while cut > 0 and (encoded[cut] & 0xC0) == 0x80:
            cut -= 1
        result.append(encoded[:cut].decode("utf-8"))
        encoded = b" " + encoded[cut:]
    result.append(encoded.decode("utf-8"))
    return "\r\n".join(result)


def build_ics(events: list) -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//PM Studio//Staff Session Logger//KO",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:[업무] PM Studio 작업 로그",
        "X-WR-TIMEZONE:Asia/Seoul",
        # VTIMEZONE (Asia/Seoul = UTC+9, no DST)
        "BEGIN:VTIMEZONE",
        "TZID:Asia/Seoul",
        "BEGIN:STANDARD",
        "DTSTART:19700101T000000",
        "TZOFFSETFROM:+0900",
        "TZOFFSETTO:+0900",
        "TZNAME:KST",
        "END:STANDARD",
        "END:VTIMEZONE",
    ]

    for ev in events:
        uid = str(uuid.uuid4()) + "@pm-studio"
        dtstamp = dt_to_ics(datetime.now(KST))

        # [업무] 접두사 — 이미 붙어 있으면 중복 방지
        subject = ev["subject"].strip()
        if not subject.startswith("[업무]"):
            summary = f"[업무] {subject}"
        else:
            summary = subject

        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{dtstamp}",
            fold_line(f"DTSTART;TZID=Asia/Seoul:{dt_to_ics(ev['start'])}"),
            fold_line(f"DTEND;TZID=Asia/Seoul:{dt_to_ics(ev['end'])}"),
            fold_line(f"SUMMARY:{escape_ics(summary)}"),
            fold_line(f"DESCRIPTION:{escape_ics(ev.get('description', ''))}"),
            "CLASS:PRIVATE",
            "END:VEVENT",
        ]

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


# ── 데이터 로더 ────────────────────────────────────────────────────────────────

def floor_to_30min(dt: datetime) -> datetime:
    if dt.minute < 30:
        return dt.replace(minute=0, second=0, microsecond=0)
    return dt.replace(minute=30, second=0, microsecond=0)


def load_from_jsonl(from_date: str) -> list:
    from_dt = datetime.strptime(from_date, "%Y-%m-%d").replace(tzinfo=KST)

    session_map = {}
    if LOG_PATH.exists():
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        s = json.loads(line)
                        session_map[s["id"]] = s
                    except (json.JSONDecodeError, KeyError):
                        pass

    sessions = sorted(session_map.values(), key=lambda x: x["start_ts"])
    sessions = [s for s in sessions if datetime.fromisoformat(s["start_ts"]) >= from_dt]

    events = []
    for s in sessions:
        start_dt = datetime.fromisoformat(s["start_ts"])
        duration_min = 30
        if s.get("end_ts"):
            end_dt = datetime.fromisoformat(s["end_ts"])
            duration_min = max(1, (end_dt - start_dt).total_seconds() / 60)

        blocks = max(1, math.ceil(duration_min / 30))
        start_block = floor_to_30min(start_dt)
        end_block = start_block + timedelta(minutes=30 * blocks)

        raw_title = s.get("summary") or s.get("request", "작업")
        title = raw_title[:60] + ("..." if len(raw_title) > 60 else "")

        skills_str = ", ".join(s.get("skills", []))
        desc = f"스킬: {skills_str} | 요청: {s.get('request', '')[:300]}" if skills_str else s.get("request", "")[:300]

        events.append({"start": start_block, "end": end_block, "subject": title, "description": desc})
    return events


def load_from_csv(csv_path: Path) -> list:
    events = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                start_dt = datetime.strptime(
                    f"{row['Start Date']} {row['Start Time']}", "%m/%d/%Y %I:%M %p"
                ).replace(tzinfo=KST)
                end_dt = datetime.strptime(
                    f"{row['End Date']} {row['End Time']}", "%m/%d/%Y %I:%M %p"
                ).replace(tzinfo=KST)
                subject = row["Subject"].strip()
                if subject.startswith("[업무] "):
                    subject = subject[5:]
                events.append({
                    "start": start_dt,
                    "end": end_dt,
                    "subject": subject,
                    "description": row.get("Description", ""),
                })
            except (KeyError, ValueError):
                continue
    return events


# ── 메인 ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="staff 세션 → ICS 캘린더 파일 생성")
    parser.add_argument("--input", default=None, help="입력 CSV 경로 (없으면 JSONL에서 직접 생성)")
    parser.add_argument("--from", dest="from_date", default="2026-03-24",
                        help="집계 시작일 (YYYY-MM-DD, JSONL 모드에서만 적용)")
    parser.add_argument("--output", default=None, help="출력 ICS 경로")
    args = parser.parse_args()

    base = Path(__file__).parent.parent / "output" / "logs"

    if args.input:
        events = load_from_csv(Path(args.input))
        out_path = Path(args.output) if args.output else base / "staff_calendar.ics"
    else:
        events = load_from_jsonl(args.from_date)
        date_str = args.from_date.replace("-", "")
        out_path = Path(args.output) if args.output else base / f"staff_calendar_{date_str}.ics"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    ics_content = build_ics(events)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(ics_content)

    print(f"✅ ICS 생성 완료: {out_path}")
    print(f"   총 {len(events)}개 이벤트 (모든 제목에 [업무] 접두사 포함)")


if __name__ == "__main__":
    main()
