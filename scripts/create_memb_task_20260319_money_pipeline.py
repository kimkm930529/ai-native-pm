#!/usr/bin/env python3
"""MEMB Task 티켓 생성 — [무신사머니] 데이터 파이프라인 방식 추가 여부 검토 — 2026-03-19"""

import sys
sys.path.insert(0, 'epic-ticket-system/.claude/skills/jira-skill/scripts')
import client

payload = {
    "fields": {
        "project":   {"key": "MEMB"},
        "summary":   "[무신사머니] 데이터 파이프라인 방식 추가 여부 검토 (무신사 데이터팀 협의)",
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
                    "content": [{"type": "text", "text": "API 방식 외에 대규모 배치성 유저 분석이 필요할 경우, 기존 OCMP 파이프라인(CDC → Kinesis → S3 → Databricks)에 머니 데이터를 추가하는 방식 검토가 필요함."}]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "작업 내용"}]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "배치성 분석 필요 여부 내부 검토"}]}]},
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "무신사 데이터팀과 파이프라인 방식 추가 가능 여부 논의"}]}]},
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "페이먼츠 DevOps(이승하님)와 대상 테이블 추가 범위 협의"}]}]}
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
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "배치 파이프라인 방식 추가 여부 결정"}]}]},
                        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "필요 시 데이터팀/DevOps와 논의 일정 확정"}]}]}
                    ]
                }
            ]
        }
    }
}

result = client.post("/issue", payload)
base_url = client.get_base_url()
print(f"✅ 티켓 생성 완료: {base_url}/browse/{result['key']}")
