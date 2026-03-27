#!/usr/bin/env python3
"""
ICS 파일에서 이번 주 + 다음 주 일정만 추출

Usage:
  python3 scripts/filter_calendar.py \
    --input "kyungmin.kim@musinsa.com.ics" \
    --output "output/logs/kyungmin_this_next_week.ics"
"""
import re
import argparse
from datetime import datetime, date, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))


def get_week_range():
    """이번 주 월요일 ~ 다음 주 일요일 (KST 기준)"""
    today = datetime.now(KST).date()
    # 이번 주 월요일 (weekday: Mon=0, Sun=6)
    this_monday = today - timedelta(days=today.weekday())
    next_sunday = this_monday + timedelta(days=13)  # 2주치
    return this_monday, next_sunday


def parse_dt(value: str):
    """DTSTART/DTEND 값 → date 반환. 날짜만 있는 경우(하루종일)도 처리."""
    value = value.strip()
    # 날짜만 (YYYYMMDD)
    if len(value) == 8 and value.isdigit():
        return datetime.strptime(value, "%Y%m%d").date()
    # UTC datetime (YYYYMMDDTHHMMSSZ)
    if value.endswith("Z"):
        dt = datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        return dt.astimezone(KST).date()
    # Local datetime (YYYYMMDDTHHMMSS)
    if "T" in value and len(value) >= 15:
        dt = datetime.strptime(value[:15], "%Y%m%dT%H%M%S")
        return dt.date()
    return None


def extract_dtstart(event_lines: list):
    """VEVENT 블록에서 DTSTART 값 추출"""
    for line in event_lines:
        # DTSTART, DTSTART;TZID=..., DTSTART;VALUE=DATE 등 모두 처리
        m = re.match(r'^DTSTART[^:]*:(.+)$', line.strip())
        if m:
            return parse_dt(m.group(1))
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="kyungmin.kim@musinsa.com.ics")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    base = Path(__file__).parent.parent
    in_path = Path(args.input) if Path(args.input).is_absolute() else base / args.input

    this_monday, next_sunday = get_week_range()
    print(f"📅 필터 범위: {this_monday} (월) ~ {next_sunday} (일)")

    if args.output:
        out_path = Path(args.output)
    else:
        out_path = base / "output" / "logs" / f"kyungmin_week_{this_monday.strftime('%m%d')}_{next_sunday.strftime('%m%d')}.ics"

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # ICS 파싱: 헤더/푸터 보존, VEVENT만 필터링
    with open(in_path, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()

    # VCALENDAR 헤더 추출 (BEGIN:VCALENDAR ~ 첫 BEGIN:VEVENT 전까지)
    header_match = re.search(r'^(BEGIN:VCALENDAR.*?)(?=BEGIN:VEVENT)', raw, re.DOTALL)
    header = header_match.group(1) if header_match else "BEGIN:VCALENDAR\r\nVERSION:2.0\r\n"

    # VTIMEZONE 블록 추출 (있으면 보존)
    tz_blocks = re.findall(r'BEGIN:VTIMEZONE.*?END:VTIMEZONE', raw, re.DOTALL)

    # VEVENT 블록 추출
    events = re.findall(r'BEGIN:VEVENT.*?END:VEVENT', raw, re.DOTALL)
    print(f"   전체 이벤트: {len(events)}개")

    kept = []
    for event in events:
        lines = event.splitlines()
        dt = extract_dtstart(lines)
        if dt and this_monday <= dt <= next_sunday:
            kept.append(event)

    print(f"   이번 주+다음 주 이벤트: {len(kept)}개")

    # 출력 조립
    out_lines = [header.rstrip()]
    for tz in tz_blocks:
        out_lines.append(tz)
    for ev in kept:
        out_lines.append(ev)
    out_lines.append("END:VCALENDAR")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))

    print(f"✅ 저장 완료: {out_path}")
    return out_path


if __name__ == "__main__":
    main()
