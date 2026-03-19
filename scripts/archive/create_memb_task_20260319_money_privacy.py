#!/usr/bin/env python3
"""MEMB Task 티켓 생성 — [무신사머니] 개인정보 포함 데이터 처리 방식 정보보안팀 검토 요청 — 2026-03-19"""

import sys
sys.path.insert(0, 'epic-ticket-system/.claude/skills/jira-skill/scripts')
import client

payload = {
    "fields": {
        "project":   {"key": "MEMB"},
        "summary":   "[무신사머니] 개인정보 포함 데이터 처리 방식 정보보안팀 검토 요청",
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
                    "content": [{"type": "text", "text": "무신사머니 데이터(가입 여부, 잔액 등)는 개인정보를 포함하고 있어, 수집·활용 방식 확정 전 정보보안팀의 사전 검토가 필요함."}]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "작업 내용"}]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "수집 예정 데이터 항목 및 활용 목적 정리"}]}]},
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "정보보안팀에 검토 요청 및 관련 문서 전달"}]}]},
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "검토 결과에 따른 활용 방식 조정"}]}]}
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
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "정보보안팀 검토 요청 접수 완료"}]}]},
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "검토 결과 수령 및 활용 가능 여부 확인"}]}]}
                    ]
                }
            ]
        }
    }
}

result = client.post("/issue", payload)
base_url = client.get_base_url()
print(f"✅ 티켓 생성 완료: {base_url}/browse/{result['key']}")
