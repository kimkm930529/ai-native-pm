#!/usr/bin/env python3
"""
UserPromptSubmit Hook — /staff 세션 자동 로그 기록기

Claude Code settings.json의 UserPromptSubmit 훅으로 등록.
/staff 가 포함된 프롬프트가 제출될 때 자동 실행.
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

    prompt = data.get("prompt", "") or ""

    # /staff 또는 staff 스킬 호출이 포함된 경우만 기록
    if "/staff" not in prompt and "staff" not in str(data.get("tools", [])):
        sys.exit(0)

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(KST)
    sid = now.strftime("%Y%m%d_%H%M%S")

    # /staff 접두사 및 커맨드 헤더 정리
    clean_request = prompt.strip()
    for prefix in ["/staff ", "ARGUMENTS: ", "<command-args>", "</command-args>"]:
        if clean_request.startswith(prefix):
            clean_request = clean_request[len(prefix):]
    clean_request = clean_request.strip()[:500]

    entry = {
        "id": sid,
        "start_ts": now.isoformat(),
        "end_ts": None,
        "request": clean_request,
        "summary": "",
        "skills": [],
        "outputs": [],
        "status": "started"
    }

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
