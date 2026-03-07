#!/usr/bin/env python3
"""
slack-notifier: send_slack.py
Slack Incoming Webhook으로 텍스트 파일을 전송하거나 터미널에 출력.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def load_message(file_path: str) -> str:
    if not os.path.exists(file_path):
        print(f"[slack-notifier] 오류: 입력 파일을 찾을 수 없습니다: {file_path}")
        sys.exit(1)
    with open(file_path, encoding="utf-8") as f:
        return f.read().strip()


def send_webhook(webhook_url: str, message: str) -> bool:
    payload = json.dumps({"text": message}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            if resp.status == 200 and body == "ok":
                return True
            print(f"[slack-notifier] 경고: 예상치 못한 응답 — {resp.status} {body}")
            return False
    except urllib.error.HTTPError as e:
        code = e.code
        if code in (403, 404):
            print("[slack-notifier] Webhook URL이 유효하지 않습니다.")
        elif code >= 500:
            print("[slack-notifier] Slack 서버 오류. 잠시 후 재시도하거나 수동으로 전송해주세요.")
        else:
            print(f"[slack-notifier] HTTP 오류: {code}")
        return False
    except OSError:
        print("[slack-notifier] 네트워크 연결을 확인해주세요.")
        return False


def print_fallback(message: str) -> None:
    separator = "=" * 43
    print()
    print(f"=== Slack 복사용 텍스트 ===")
    print(message)
    print(separator)
    print("위 내용을 Slack에 직접 붙여넣어 주세요.")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Slack Notifier — 슬랙 요약 전송")
    parser.add_argument("--input", required=True, help="전송할 텍스트 파일 경로")
    parser.add_argument("--webhook-url", default=None, help="Slack Webhook URL (미지정 시 환경변수 사용)")
    parser.add_argument("--dry-run", action="store_true", help="실제 전송 없이 터미널 출력만 수행")
    parser.add_argument("--channel", default=None, help="채널 오버라이드 (참고용, Webhook URL이 우선)")
    args = parser.parse_args()

    message = load_message(args.input)

    webhook_url = args.webhook_url or os.environ.get("SLACK_WEBHOOK_URL", "")

    # Preview
    preview_lines = message.split("\n")[:4]
    preview = "\n".join(preview_lines)

    if args.dry_run or not webhook_url:
        if not webhook_url:
            print("[slack-notifier] SLACK_WEBHOOK_URL 미설정 — 터미널 출력 모드")
        else:
            print("[slack-notifier] dry-run 모드")
        print_fallback(message)
        return

    print("[slack-notifier] Slack 전송 중...")
    success = send_webhook(webhook_url, message)

    if success:
        channel_info = f"#{args.channel}" if args.channel else "설정된 채널"
        print(f"[slack-notifier] Slack 전송 완료")
        print(f"채널: {channel_info}")
        print("메시지 미리보기:")
        print("---")
        print(preview)
        print("---")
    else:
        print("[slack-notifier] 전송 실패 — 터미널 출력 모드로 폴백")
        print_fallback(message)


if __name__ == "__main__":
    main()
