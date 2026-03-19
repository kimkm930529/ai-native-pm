#!/usr/bin/env python3
"""MEMB Task 티켓 생성 — [무신사머니] 페이먼츠팀에 API 호출 영역 및 예상 빈도 공유 — 2026-03-19"""

import sys
sys.path.insert(0, 'epic-ticket-system/.claude/skills/jira-skill/scripts')
import client

payload = {
    "fields": {
        "project":   {"key": "MEMB"},
        "summary":   "[무신사머니] 페이먼츠팀에 API 호출 영역 및 예상 빈도 공유",
        "issuetype": {"id": "10006"},
        "priority":  {"name": "High"},
        "duedate":   "2026-03-26",
        "assignee":  {"accountId": "712020:9bbd1f66-a6e3-4385-957b-56995ea34f89"},
        "labels":    ["무신사머니"],
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "배경"}]
                },
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "무신사페이먼츠 이아현(sammi)님이 트래픽 대응을 위해 API 호출 영역과 예상 빈도 공유를 요청함. 기획 확정 후 조속히 회신이 필요함."}]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "작업 내용"}]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "앱테크 미션에서 API를 호출할 영역(화면/기능) 정리"}]}]},
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "예상 DAU, 호출 빈도(1회/일, 세션당 1회 등) 추정"}]}]},
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "이아현(sammi)님께 슬랙 또는 메일로 정보 회신"}]}]}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "완료 기준 (AC)"}]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "호출 영역 및 예상 빈도 정보 페이먼츠팀에 전달 완료"}]}]},
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "페이먼츠팀으로부터 수신 확인"}]}]}
                    ]
                }
            ]
        }
    }
}

result = client.post("/issue", payload)
base_url = client.get_base_url()
print(f"✅ 티켓 생성 완료: {base_url}/browse/{result['key']}")
