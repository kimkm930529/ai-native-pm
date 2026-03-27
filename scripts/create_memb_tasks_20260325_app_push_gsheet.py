#!/usr/bin/env python3
"""MEMB Task 티켓 2개 생성 — App Push PRD 수정 + Google Sheet API 신청 — 2026-03-25"""

import sys
sys.path.insert(0, 'epic-ticket-system/.claude/skills/jira-skill/scripts')
import client

ASSIGNEE_ID = "712020:9bbd1f66-a6e3-4385-957b-56995ea34f89"   # 김경민
WATCHER_ID  = "712020:e408163e-78d3-4eaf-b560-426c93797e6a"   # 김윤태
TASK_TYPE_ID = "10006"
DUE_DATE = "2026-04-08"

tickets = [
    {
        "summary": "App Push Schedule Sync Pipeline 기반 PRD 수정",
        "priority": "Medium",
        "background": "윤태님이 구현한 App Push Schedule Sync Pipeline의 실제 구조 및 동작 방식을 반영하여 기존 PRD를 업데이트해야 한다.",
        "tasks": [
            "윤태님의 App Push Schedule Sync Pipeline 구현 내용 파악 및 문서화",
            "기존 PRD 내용 중 파이프라인 관련 항목 검토",
            "파이프라인 스펙(입력/출력, 스케줄링 방식, 동기화 로직)에 맞게 PRD 수정",
        ],
        "ac": [
            "Pipeline 동작 방식이 PRD에 정확하게 기술됨",
            "수정된 PRD가 Confluence에 반영됨",
        ],
    },
    {
        "summary": "Google Sheet API 신청하기",
        "priority": "Medium",
        "background": "프로젝트 내 데이터 연동 또는 자동화 작업을 위해 Google Sheet API 접근 권한 신청이 필요하다.",
        "tasks": [
            "Google Cloud Console에서 API 신청 또는 사내 시스템을 통한 접근 권한 요청",
            "API 키 또는 서비스 계정 발급 확인",
            "필요 시 팀 내 공유 및 사용 가이드 정리",
        ],
        "ac": [
            "Google Sheet API 접근 권한 발급 완료",
            "테스트 호출 성공",
        ],
    },
]


def make_bullet(items):
    return [
        {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": item}]}]}
        for item in items
    ]


def make_description(background, tasks, ac):
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "배경"}]},
            {"type": "paragraph", "content": [{"type": "text", "text": background}]},
            {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "작업 내용"}]},
            {"type": "bulletList", "content": make_bullet(tasks)},
            {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": "완료 기준 (AC)"}]},
            {"type": "bulletList", "content": make_bullet(ac)},
        ],
    }


base_url = client.get_base_url()
created_keys = []

for t in tickets:
    payload = {
        "fields": {
            "project":     {"key": "MEMB"},
            "summary":     t["summary"],
            "issuetype":   {"id": TASK_TYPE_ID},
            "priority":    {"name": t["priority"]},
            "duedate":     DUE_DATE,
            "assignee":    {"accountId": ASSIGNEE_ID},
            "description": make_description(t["background"], t["tasks"], t["ac"]),
        }
    }

    result = client.post("/issue", payload)
    key = result["key"]
    created_keys.append(key)
    print(f"✅ 티켓 생성: {base_url}/browse/{key}  ({t['summary']})")

    # 김윤태 watcher 추가
    client.post(f"/issue/{key}/watchers", WATCHER_ID)
    print(f"   👀 워처 추가 완료: 김윤태")

print("\n🎉 완료!")
for key in created_keys:
    print(f"   🔗 {base_url}/browse/{key}")
