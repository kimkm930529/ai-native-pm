#!/usr/bin/env python3
"""
/staff 세션 로그 업데이터 — Claude가 직접 호출

Usage:
  # 세션 시작 (SESSION_ID 반환)
  python3 scripts/log_staff_session.py --start "요청 내용"

  # 세션 완료 기록
  python3 scripts/log_staff_session.py \\
    --end 20260324_103045 \\
    --summary "Campaign Meta Engine PRD 작성" \\
    --skills "/prd,/red" \\
    --outputs "prd_20260324_xxx.md,redteam_20260324_xxx.md" \\
    --status completed
"""
import json
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))
LOG_PATH = Path(__file__).parent.parent / "output" / "logs" / "staff_sessions.jsonl"


def now_kst():
    return datetime.now(KST).isoformat()


def session_id():
    return datetime.now(KST).strftime("%Y%m%d_%H%M%S")


def main():
    parser = argparse.ArgumentParser(description="/staff 세션 로그 기록")
    parser.add_argument("--start", help="세션 시작: 요청 내용")
    parser.add_argument("--end", help="세션 종료: SESSION_ID")
    parser.add_argument("--summary", default="", help="세션 요약 (한 줄)")
    parser.add_argument("--skills", default="", help="사용 스킬 (쉼표 구분, 예: /prd,/red)")
    parser.add_argument("--outputs", default="", help="산출물 파일 (쉼표 구분)")
    parser.add_argument("--status", default="completed", choices=["started", "completed", "failed", "interrupted"])
    args = parser.parse_args()

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    if args.start:
        sid = session_id()
        entry = {
            "id": sid,
            "start_ts": now_kst(),
            "end_ts": None,
            "request": args.start[:500],
            "summary": args.summary,
            "skills": [],
            "outputs": [],
            "status": "started"
        }
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print(f"SESSION_ID={sid}")

    elif args.end:
        sid = args.end
        lines = []
        updated = False

        if LOG_PATH.exists():
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        lines.append(line)
                        continue

                    if entry["id"] == sid and entry["status"] == "started":
                        entry["end_ts"] = now_kst()
                        entry["status"] = args.status
                        if args.summary:
                            entry["summary"] = args.summary
                        if args.skills:
                            entry["skills"] = [s.strip() for s in args.skills.split(",") if s.strip()]
                        if args.outputs:
                            entry["outputs"] = [o.strip() for o in args.outputs.split(",") if o.strip()]
                        updated = True
                    lines.append(json.dumps(entry, ensure_ascii=False))

            with open(LOG_PATH, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")

        if updated:
            print(f"OK: Session {sid} → {args.status}")
        else:
            # 훅이 시작 기록을 안 했을 때 fallback: 완료 엔트리 직접 생성
            entry = {
                "id": sid,
                "start_ts": now_kst(),
                "end_ts": now_kst(),
                "request": args.summary or "(unknown)",
                "summary": args.summary,
                "skills": [s.strip() for s in args.skills.split(",") if s.strip()],
                "outputs": [o.strip() for o in args.outputs.split(",") if o.strip()],
                "status": args.status
            }
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            print(f"OK: New entry created for {sid}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
