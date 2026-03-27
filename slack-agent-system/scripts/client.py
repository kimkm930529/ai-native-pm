#!/usr/bin/env python3
"""
Slack Web API Client — slack-agent-system
채널 대화 수집, 사용자 조회, 메시지 발송

연동 필요:
  .env에 다음 환경변수 추가:
    SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxx
    SLACK_DEFAULT_CHANNEL=general

  Slack 앱 설정 (api.slack.com/apps):
    OAuth Scopes: channels:history, channels:read, users:read, chat:write

사용법:
  python3 client.py --check
  python3 client.py --channel-id {channel_name}
  python3 client.py --list-channels
  python3 client.py --fetch --channel {channel_id} --oldest {ts} --latest {ts}
  python3 client.py --fetch-threads --channel {channel_id} --thread-ts {ts}
  python3 client.py --user-info {user_id}
  python3 client.py --search "{keyword}" --channel {channel_id}
  python3 client.py --send --channel {channel_id} --message "{text}"
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path


def load_env():
    env_path = Path(__file__).parents[2] / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ.setdefault(key.strip(), val.strip())

load_env()

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_DEFAULT_CHANNEL = os.environ.get("SLACK_DEFAULT_CHANNEL", "general")
SLACK_BASE_URL = "https://slack.com/api"

_user_cache: dict[str, str] = {}


def slack_get(method: str, params: dict = {}) -> dict:
    query = urllib.parse.urlencode(params)
    url = f"{SLACK_BASE_URL}/{method}?{query}"
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            if not data.get("ok"):
                return {"error": data.get("error", "unknown"), "raw": data}
            return data
    except Exception as e:
        return {"error": str(e)}


def slack_post(method: str, body: dict) -> dict:
    url = f"{SLACK_BASE_URL}/{method}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            if not data.get("ok"):
                return {"error": data.get("error", "unknown"), "raw": data}
            return data
    except Exception as e:
        return {"error": str(e)}


# ─── 연결 확인 ──────────────────────────────────────────────

def check_connection():
    if not SLACK_BOT_TOKEN:
        print(json.dumps({
            "status": "error",
            "message": "SLACK_BOT_TOKEN 미설정",
            "guide": "slack-agent-system/CLAUDE.md §Step 0 연결 설정 가이드 참조"
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    result = slack_get("auth.test")
    if "error" in result:
        print(json.dumps({
            "status": "error",
            "message": result["error"],
            "guide": "토큰이 올바른지 확인하세요. xoxb- 로 시작해야 합니다."
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    print(json.dumps({
        "status": "ok",
        "bot": result.get("user"),
        "workspace": result.get("team"),
        "default_channel": SLACK_DEFAULT_CHANNEL,
    }, ensure_ascii=False, indent=2))


# ─── 채널 관련 ──────────────────────────────────────────────

def list_channels():
    result = slack_get("conversations.list", {"limit": 200, "types": "public_channel,private_channel"})
    if "error" in result:
        print(json.dumps(result, ensure_ascii=False, indent=2)); return

    channels = result.get("channels", [])
    print(json.dumps({
        "channels": [
            {
                "id": c.get("id"),
                "name": c.get("name"),
                "is_private": c.get("is_private"),
                "num_members": c.get("num_members"),
                "topic": c.get("topic", {}).get("value", ""),
            }
            for c in channels
        ],
        "count": len(channels),
    }, ensure_ascii=False, indent=2))


def get_channel_id(channel_name: str) -> str:
    """채널명 → ID 변환"""
    name = channel_name.lstrip("#")
    result = slack_get("conversations.list", {"limit": 200, "types": "public_channel,private_channel"})
    if "error" in result:
        return ""
    channels = result.get("channels", [])
    for c in channels:
        if c.get("name") == name:
            return c.get("id", "")

    # 유사 채널 제안
    similar = [c.get("name") for c in channels if name.lower() in c.get("name", "").lower()]
    print(json.dumps({
        "error": f"채널 '{name}'을 찾을 수 없습니다.",
        "similar_channels": similar[:5],
    }, ensure_ascii=False, indent=2), file=sys.stderr)
    return ""


def cmd_channel_id(channel_name: str):
    channel_id = get_channel_id(channel_name)
    if channel_id:
        print(json.dumps({"channel": channel_name, "channel_id": channel_id}, ensure_ascii=False, indent=2))
    else:
        sys.exit(1)


# ─── 메시지 수집 ────────────────────────────────────────────

def get_user_name(user_id: str) -> str:
    if user_id in _user_cache:
        return _user_cache[user_id]
    result = slack_get("users.info", {"user": user_id})
    if "error" in result:
        return user_id
    profile = result.get("user", {}).get("profile", {})
    name = profile.get("display_name") or profile.get("real_name") or user_id
    _user_cache[user_id] = name
    return name


def resolve_mentions(text: str) -> str:
    """<@U12345> → @홍길동 변환"""
    import re
    def replace(m):
        return f"@{get_user_name(m.group(1))}"
    return re.sub(r"<@(U[A-Z0-9]+)>", replace, text)


def fetch_messages(channel_id: str, oldest: float = 0.0, latest: float = 0.0, limit: int = 200) -> list:
    params = {"channel": channel_id, "limit": limit}
    if oldest:
        params["oldest"] = str(oldest)
    if latest:
        params["latest"] = str(latest)

    messages = []
    cursor = None
    while True:
        if cursor:
            params["cursor"] = cursor
        result = slack_get("conversations.history", params)
        if "error" in result:
            if result.get("error") == "ratelimited":
                time.sleep(1)
                continue
            break

        for msg in result.get("messages", []):
            if msg.get("type") != "message":
                continue
            user_id = msg.get("user", "")
            messages.append({
                "ts": msg.get("ts"),
                "user": f"@{get_user_name(user_id)}" if user_id else "(bot)",
                "text": resolve_mentions(msg.get("text", "")),
                "thread_ts": msg.get("thread_ts"),
                "reply_count": msg.get("reply_count", 0),
                "reactions": [
                    {"name": r.get("name"), "count": r.get("count")}
                    for r in msg.get("reactions", [])
                ],
            })

        cursor = result.get("response_metadata", {}).get("next_cursor")
        if not cursor or not result.get("has_more"):
            break

    return messages


def fetch_thread(channel_id: str, thread_ts: str) -> list:
    result = slack_get("conversations.replies", {
        "channel": channel_id,
        "ts": thread_ts,
        "limit": 100,
    })
    if "error" in result:
        return []
    replies = []
    for msg in result.get("messages", [])[1:]:  # 첫 메시지는 원본, 스킵
        user_id = msg.get("user", "")
        replies.append({
            "ts": msg.get("ts"),
            "user": f"@{get_user_name(user_id)}" if user_id else "(bot)",
            "text": resolve_mentions(msg.get("text", "")),
        })
    return replies


def cmd_fetch(channel_id: str, oldest: float = 0.0, latest: float = 0.0, limit: int = 200):
    messages = fetch_messages(channel_id, oldest, latest, limit)
    # 스레드 답글 붙이기
    for msg in messages:
        if msg.get("reply_count", 0) > 0 and msg.get("thread_ts"):
            msg["replies"] = fetch_thread(channel_id, msg["thread_ts"])
        else:
            msg["replies"] = []

    print(json.dumps({
        "channel_id": channel_id,
        "message_count": len(messages),
        "thread_count": sum(1 for m in messages if m.get("reply_count", 0) > 0),
        "messages": messages,
    }, ensure_ascii=False, indent=2))


# ─── 검색 ───────────────────────────────────────────────────

def cmd_search(keyword: str, channel_id: str = "", limit: int = 50):
    # Slack search.messages는 User Token 필요 (Bot Token 미지원)
    # → 대안: 최근 메시지에서 키워드 필터링
    oldest = (datetime.now() - timedelta(days=30)).timestamp()
    messages = fetch_messages(channel_id, oldest=oldest, limit=200)
    matched = [m for m in messages if keyword.lower() in m.get("text", "").lower()]

    print(json.dumps({
        "keyword": keyword,
        "channel_id": channel_id,
        "matched_count": len(matched),
        "messages": matched[:limit],
        "note": "최근 30일 메시지에서 검색. 더 넓은 검색은 Slack 앱의 검색 기능을 사용하세요.",
    }, ensure_ascii=False, indent=2))


# ─── 발송 ───────────────────────────────────────────────────

def cmd_send(channel_id: str, message: str):
    result = slack_post("chat.postMessage", {
        "channel": channel_id,
        "text": message,
    })
    if "error" in result:
        print(json.dumps({"status": "error", "error": result["error"]}, ensure_ascii=False, indent=2))
        sys.exit(1)
    print(json.dumps({
        "status": "sent",
        "channel": channel_id,
        "ts": result.get("ts"),
        "message": message[:100],
    }, ensure_ascii=False, indent=2))


# ─── CLI ────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Slack Web API Client")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--list-channels", action="store_true")
    parser.add_argument("--channel-id", type=str, metavar="CHANNEL_NAME")
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--fetch-threads", action="store_true")
    parser.add_argument("--user-info", type=str, metavar="USER_ID")
    parser.add_argument("--search", type=str, metavar="KEYWORD")
    parser.add_argument("--send", action="store_true")
    parser.add_argument("--channel", type=str)
    parser.add_argument("--oldest", type=float, default=0.0)
    parser.add_argument("--latest", type=float, default=0.0)
    parser.add_argument("--thread-ts", type=str)
    parser.add_argument("--message", type=str)
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()

    if args.check:
        check_connection()
    elif args.list_channels:
        list_channels()
    elif args.channel_id:
        cmd_channel_id(args.channel_id)
    elif args.fetch:
        if not args.channel:
            print(json.dumps({"error": "--channel 필요"})); sys.exit(1)
        cmd_fetch(args.channel, args.oldest, args.latest, args.limit)
    elif args.fetch_threads:
        if not args.channel or not args.thread_ts:
            print(json.dumps({"error": "--channel, --thread-ts 필요"})); sys.exit(1)
        replies = fetch_thread(args.channel, args.thread_ts)
        print(json.dumps({"replies": replies}, ensure_ascii=False, indent=2))
    elif args.user_info:
        name = get_user_name(args.user_info)
        print(json.dumps({"user_id": args.user_info, "display_name": name}, ensure_ascii=False, indent=2))
    elif args.search:
        cmd_search(args.search, args.channel or "", args.limit)
    elif args.send:
        if not args.channel or not args.message:
            print(json.dumps({"error": "--channel, --message 필요"})); sys.exit(1)
        cmd_send(args.channel, args.message)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
