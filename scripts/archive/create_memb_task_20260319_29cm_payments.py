#!/usr/bin/env python3
"""MEMB Task 티켓 생성 — 29cm데이터+페이먼츠 — 2026-03-19"""

import sys
sys.path.insert(0, 'epic-ticket-system/.claude/skills/jira-skill/scripts')
import client

def make_bullet(items):
    return {
        "type": "bulletList",
        "content": [
            {
                "type": "listItem",
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": item}]}]
            }
            for item in items
        ]
    }

def make_heading(text, level=2):
    return {
        "type": "heading",
        "attrs": {"level": level},
        "content": [{"type": "text", "text": text}]
    }

def make_paragraph(text):
    return {
        "type": "paragraph",
        "content": [{"type": "text", "text": text}]
    }

tickets = [
    {
        "summary": "29cm 데이터 MATCH 서비스 제공 관련 PRD 작성",
        "priority": "High",
        "duedate": "2026-03-25",
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                make_heading("배경"),
                make_paragraph(
                    "CorenE 팀에서 2분기 29cm 데이터를 MATCH 서비스에 제공하는 방안을 검토 중이며, "
                    "관련 PRD가 아직 존재하지 않음. 히드로 관련 속성 데이터(박세정님 확인 내용 포함) 및 "
                    "데이터 관련 과제들을 함께 정리하기로 협의됨."
                ),
                make_heading("작업 내용"),
                make_bullet([
                    "히드로 관련 속성 데이터 항목 확인 및 정리 (박세정님 협의)",
                    "29cm → MATCH 서비스 데이터 제공 범위 및 방식 정의",
                    "데이터 관련 연계 과제 목록화 (실시간 서빙, 페이먼츠 등 포함 여부 검토)",
                    "PRD 초안 작성 및 CorenE 팀 공유",
                ]),
                make_heading("완료 기준 (AC)"),
                make_bullet([
                    "제공할 데이터 항목 및 스키마 목록 확정",
                    "데이터 제공 방식(API / 배치 등) 방향 정의",
                    "CorenE 팀 공유 및 피드백 수령",
                ]),
            ]
        }
    },
    {
        "summary": "무신사 페이먼츠 데이터 API 연동 방안 검토",
        "priority": "Medium",
        "duedate": "2026-04-02",
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                make_heading("배경"),
                make_paragraph(
                    "앱테크 팀에서 페이먼츠 데이터를 활용한 타게팅을 계획 중이나, "
                    "무신사 페이먼츠는 DB 직접 조회가 불가하여 Internal API 연동을 통해서만 "
                    "데이터 접근이 가능한 상황. 무신사머니 Internal API 연동 문서(v1.0.1) 수령 완료."
                ),
                make_heading("작업 내용"),
                make_bullet([
                    "무신사머니 Internal API 연동 문서 검토",
                    "MATCH/CRM 타게팅 관점에서 필요한 페이먼츠 데이터 항목 정의",
                    "API 연동 방식 및 호출 주기(실시간/배치) 방향 협의",
                    "페이먼츠팀과 API 제공 범위 확인",
                ]),
                make_heading("완료 기준 (AC)"),
                make_bullet([
                    "타게팅에 활용 가능한 페이먼츠 데이터 항목 목록 확정",
                    "API 연동 방식(실시간 vs 배치) 결정",
                    "페이먼츠팀과 제공 가능 여부 최종 확인",
                ]),
            ]
        }
    },
]

base_url = client.get_base_url()
created = []

for t in tickets:
    payload = {
        "fields": {
            "project":     {"key": "MEMB"},
            "summary":     t["summary"],
            "issuetype":   {"id": "10006"},
            "priority":    {"name": t["priority"]},
            "duedate":     t["duedate"],
            "description": t["description"],
        }
    }
    result = client.post("/issue", payload)
    url = f"{base_url}/browse/{result['key']}"
    created.append((result['key'], t['summary'], url))
    print(f"✅ {result['key']} — {t['summary']}")
    print(f"   {url}")

print(f"\n총 {len(created)}개 티켓 생성 완료.")
