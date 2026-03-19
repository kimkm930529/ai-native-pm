#!/usr/bin/env python3
"""MEMB Task 티켓 생성 — 2026-03-19 일일 과제 6건"""

import sys
sys.path.insert(0, 'epic-ticket-system/.claude/skills/jira-skill/scripts')
import client

ASSIGNEE = {"accountId": "712020:9bbd1f66-a6e3-4385-957b-56995ea34f89"}


def p(text):
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}


def h2(text):
    return {"type": "heading", "attrs": {"level": 2}, "content": [{"type": "text", "text": text}]}


def bullets(items):
    return {
        "type": "bulletList",
        "content": [
            {"type": "listItem", "content": [p(item)]}
            for item in items
        ]
    }


def ac(items):
    return {
        "type": "bulletList",
        "content": [
            {"type": "listItem", "content": [p("[ ] " + item)]}
            for item in items
        ]
    }


def body(background, work_items, ac_items):
    return {
        "type": "doc",
        "version": 1,
        "content": [
            h2("배경"), p(background),
            h2("작업 내용"), bullets(work_items),
            h2("완료 기준 (AC)"), ac(ac_items),
        ]
    }


tickets = [
    {
        "summary": "TM-2391 하위 PSN 티켓 일정 업데이트 및 담당자 변경",
        "priority": "High",
        "duedate": "2026-03-19",
        "labels": ["Audience-API", "TM-2391"],
        "description": body(
            "Audience API 개발 일정이 변경됨 (개발환경 3/24, 운영환경 3/27). "
            "이건우님이 TM-2391 이니셔티브 하위 PSN 티켓에 일정 업데이트가 없어 "
            "구두로만 전달받다 오해가 발생했다고 요청. 또한 준호님이 담당자로 되어 있으나 실제 작업자로 변경 필요.",
            [
                "TM-2391 하위 PSN 티켓 일정 업데이트 (개발환경 3/24, 운영환경 3/27)",
                "실제 작업자로 담당자 변경 (현재 준호님 → 실제 작업자)",
                "이건우님께 업데이트 완료 멘션",
            ],
            [
                "TM-2391 하위 PSN 티켓에 변경된 일정이 반영됨",
                "담당자가 실제 작업자로 변경됨",
                "이건우님께 업데이트 완료 멘션",
            ]
        ),
    },
    {
        "summary": "29CM 마케팅팀 2-Pager 리뷰 미팅 준비 및 진행",
        "priority": "Medium",
        "duedate": "2026-03-27",
        "labels": ["29CM", "자동화푸시"],
        "description": body(
            "이재인님(그로스마케팅2)이 29CM 자동화 푸시 도입 타임라인을 문의. "
            "차주 중 29CM 마케팅 담당자들께 2-Pager 리뷰를 진행하기로 약속. "
            "관련 문서: https://wiki.team.musinsa.com/wiki/spaces/membership/pages/317442347/2-Pager+29CM+.",
            [
                "2-Pager 내용 최종 다듬기",
                "29CM 마케팅 담당자들 리뷰 미팅 일정 잡기",
                "과제 방향성·목표·변화 내용 리뷰 진행",
            ],
            [
                "2-Pager 문서 최종본 준비 완료",
                "29CM 마케팅 담당자 대상 리뷰 미팅 완료",
            ]
        ),
    },
    {
        "summary": "29CM 자동화 푸시 Phased Approach 업데이트",
        "priority": "Medium",
        "duedate": "2026-03-27",
        "labels": ["29CM", "자동화푸시"],
        "description": body(
            "이재인님이 이해한 Phased Approach(2Q 운영안정화, 3Q 파이프라인, 4Q 개인화)에 수정이 필요. "
            "2분기에 프로모션 푸시로 운영되는 것들의 타겟팅 자동화를 목표로 하는 방향으로 내용 업데이트 필요.",
            [
                "Q별 자동화 목표 수정 (2Q: 프로모션 푸시 타겟팅 자동화 중심으로)",
                "자동화 비중 단계별 목표 재정의",
                "문서 업데이트 및 마케팅팀 공유",
            ],
            [
                "Phased Approach 문서에 수정된 분기별 목표 반영",
                "29CM 마케팅팀에 업데이트된 내용 공유 완료",
            ]
        ),
    },
    {
        "summary": "OCMP S3 페이먼츠 데이터 가입여부 칼럼 확인 요청",
        "priority": "Medium",
        "duedate": "2026-03-25",
        "labels": ["페이먼츠", "MATCH-데이터"],
        "description": body(
            "29cm 데이터 MATCH 연동 과제에서 페이먼츠 데이터 활용 시 API 연동 방식은 사용하지 않기로 결정. "
            "OCMP S3에 적재된 페이먼츠 데이터를 활용하는 방식으로 전환하였으며, "
            "가입여부 칼럼 존재 여부 확인 후 MATCH 파이프라인 구성이 가능함.",
            [
                "박병길님께 OCMP S3 페이먼츠 데이터에 가입여부 칼럼 존재 여부 확인 요청",
                "확인 결과 바탕으로 MATCH 데이터 파이프라인 구성 검토",
            ],
            [
                "OCMP S3 페이먼츠 데이터에 가입여부 칼럼 존재 여부 확인 완료",
                "칼럼 존재 시 MATCH 연동 방안 확정",
            ]
        ),
    },
    {
        "summary": "Auxia DPA Exhibit C 추가 반영 확인 및 법무 검토 진행",
        "priority": "High",
        "duedate": "2026-04-02",
        "labels": ["Auxia", "계약", "법무"],
        "description": body(
            "Auxia와 체결한 Amendment to Musinsa Order Form and DPA (27 February 2026) 계약서 내 "
            "Section 5. Security of Personal Data 항목에 Exhibit C(무신사 표준 위탁계약서 기준 보호조치 내용)가 "
            "포함되어 있지 않아 보완 요청. Will/snehal/charles에게 양식 작성 후 스캔본 전달 요청 완료.",
            [
                "Auxia로부터 Exhibit C 추가된 계약서 스캔본 수령 확인",
                "법무팀에 검토 의뢰",
                "검토 완료 후 서명 진행",
            ],
            [
                "Auxia로부터 Exhibit C 포함 계약서 스캔본 수령 완료",
                "법무팀 검토 완료",
                "최종 서명 완료",
            ]
        ),
    },
    {
        "summary": "MATCH 비즈니스 심각도 기준 SLI/SLO 정의",
        "priority": "Medium",
        "duedate": "2026-03-25",
        "labels": ["MATCH", "SLO", "안정성"],
        "description": body(
            "CBP 비즈니스 심각도 정의 - MATCH 관련 문서 작성 중. "
            "김준호님이 CSP 구분에서 수준별 SLI/SLO 정의가 필요하다고 요청. "
            "이전 Auxia 및 외부 PoC 정리 내용을 참고하여 작성하기로 함. "
            "참고 문서: https://wiki.team.musinsa.com/wiki/spaces/~7120209bbd1f66a6e34385957b56995ea34f89/pages/352912671/MATCH",
            [
                "이전 Auxia/외부 PoC 정리 자료에서 SLI/SLO 참고 내용 확인",
                "MATCH 비즈니스 심각도 수준별 SLI/SLO 초안 작성",
                "김준호님과 내용 검토 및 확정",
            ],
            [
                "MATCH 비즈니스 심각도 기준별 SLI/SLO 초안 작성 완료",
                "김준호님 검토 및 최종 확정",
            ]
        ),
    },
]

base_url = client.get_base_url()
results = []

for t in tickets:
    payload = {
        "fields": {
            "project":     {"key": "MEMB"},
            "summary":     t["summary"],
            "issuetype":   {"id": "10006"},
            "priority":    {"name": t["priority"]},
            "duedate":     t["duedate"],
            "assignee":    ASSIGNEE,
            "labels":      t.get("labels", []),
            "description": t["description"],
        }
    }
    result = client.post("/issue", payload)
    key = result["key"]
    url = f"{base_url}/browse/{key}"
    results.append((key, t["summary"], t["priority"], t["duedate"], url))
    print(f"✅ {key} — {t['summary']}")
    print(f"   {url}")

print("\n📋 생성 완료 요약")
print("-" * 60)
for key, summary, priority, due, url in results:
    print(f"  {key} [{priority}] ~{due}  {summary}")
