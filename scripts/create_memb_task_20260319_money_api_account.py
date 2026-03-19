#!/usr/bin/env python3
"""MEMB Task 티켓 생성 — [무신사머니] 계좌 등록 여부 API 추가 개발 요청 — 2026-03-19"""

import sys
sys.path.insert(0, 'epic-ticket-system/.claude/skills/jira-skill/scripts')
import client

payload = {
    "fields": {
        "project":   {"key": "MEMB"},
        "summary":   "[무신사머니] 계좌 등록 여부 API 추가 개발 요청",
        "issuetype": {"id": "10006"},
        "priority":  {"name": "Medium"},
        "duedate":   "2026-04-02",
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
                    "content": [{"type": "text", "text": "앱테크 미션 유저 세그먼트 구성 시 계좌 등록 여부를 조건으로 활용해야 하나, 현재 무신사머니 연동 API 스펙에는 해당 항목이 없어 추가 개발이 필요함."}]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "작업 내용"}]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "무신사페이먼츠 개발팀에 계좌 등록 여부 조회 API 추가 개발 공식 요청"}]}]},
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "요청 문서(스펙 요구사항) 작성 및 전달"}]}]},
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "개발 일정 협의 및 확인"}]}]}
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
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "페이먼츠팀으로부터 API 개발 착수 확인 또는 일정 회신 수령"}]}]},
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "요청 스펙 문서 전달 완료"}]}]}
                    ]
                }
            ]
        }
    }
}

result = client.post("/issue", payload)
base_url = client.get_base_url()
print(f"✅ 티켓 생성 완료: {base_url}/browse/{result['key']}")
