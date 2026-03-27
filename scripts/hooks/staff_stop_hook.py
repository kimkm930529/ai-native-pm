#!/usr/bin/env python3
"""
Stop Hook — Claude 응답 종료 시 staff 세션의 end_ts 자동 기록

Claude Code settings.json의 Stop 훅으로 등록.
가장 최근 "started" 상태인 staff 세션의 end_ts를 자동으로 채운다.
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))
LOG_PATH = Path("/Users/musinsa/Documents/agent_project/pm-studio/output/logs/staff_sessions.jsonl")


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    # transcript에서 /staff 호출 여부 확인 (최근 10개 메시지 검색)
    transcript = data.get("transcript", [])
    was_staff = False
    for msg in transcript[-10:]:
        if isinstance(msg, dict):
            content = str(msg.get("content", ""))
            if "/staff" in content or "staff" in str(msg.get("tool_name", "")):
                was_staff = True
                break

    if not was_staff:
        sys.exit(0)

    if not LOG_PATH.exists():
        sys.exit(0)

    # 가장 최근 "started" 엔트리 찾아서 end_ts 기록
    try:
        entries = []
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

        now = datetime.now(KST).isoformat()
        updated = False
        for entry in reversed(entries):
            if entry.get("status") == "started" and not entry.get("end_ts"):
                entry["end_ts"] = now
                # status는 "completed"로 올리지 않음 — Claude가 명시적으로 완료 기록할 수 있도록
                # summary/skills/outputs는 Claude가 채워야 하므로 여기서는 건드리지 않음
                updated = True
                break

        if updated:
            with open(LOG_PATH, "w", encoding="utf-8") as f:
                for entry in entries:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
