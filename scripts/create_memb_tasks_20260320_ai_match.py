#!/usr/bin/env python3
"""MEMB Task 티켓 생성 — AI Assistant 2-Pager / MATCH 방향성 문서 업데이트 — 2026-03-20"""

import sys, os, json, base64, urllib.request
from pathlib import Path

for line in Path(__file__).parents[1].joinpath('.env').read_text().splitlines():
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, _, v = line.partition('=')
        os.environ.setdefault(k.strip(), v.strip())

HOST     = os.environ.get('CONFLUENCE_URL', '').rstrip('/')
EMAIL    = os.environ.get('CONFLUENCE_EMAIL', '')
TOKEN    = os.environ.get('CONFLUENCE_API_TOKEN', '')
CREDS    = base64.b64encode(f'{EMAIL}:{TOKEN}'.encode()).decode()
HEADERS  = {'Authorization': f'Basic {CREDS}', 'Content-Type': 'application/json'}

ASSIGNEE_ID   = '712020:9bbd1f66-a6e3-4385-957b-56995ea34f89'
TASK_TYPE_ID  = '10006'
DUE_DATE      = '2026-03-24'


def jira_post(path, payload):
    url  = f'{HOST}/rest/api/3{path}'
    body = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=body, headers=HEADERS, method='POST')
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def make_doc(background, tasks, ac):
    def bullets(items):
        return {
            'type': 'bulletList',
            'content': [
                {'type': 'listItem', 'content': [
                    {'type': 'paragraph', 'content': [{'type': 'text', 'text': item}]}
                ]}
                for item in items
            ]
        }

    def heading(text):
        return {'type': 'heading', 'attrs': {'level': 2}, 'content': [{'type': 'text', 'text': text}]}

    return {
        'type': 'doc', 'version': 1,
        'content': [
            heading('배경'),
            {'type': 'paragraph', 'content': [{'type': 'text', 'text': background}]},
            heading('작업 내용'),
            bullets(tasks),
            heading('완료 기준 (AC)'),
            bullets(ac),
        ]
    }


TICKETS = [
    {
        'summary': 'AI Assistant 2-Pager 정리',
        'description': make_doc(
            background='AI Assistant 기능의 핵심 내용을 2-Pager 문서 형태로 정리하여 이해관계자와 공유할 수 있는 문서 산출물을 마련한다.',
            tasks=[
                'AI Assistant 주요 기능 및 가치 제안 정리',
                '2-Pager 포맷에 맞게 핵심 내용 구성 및 작성',
                '이해관계자 배포 가능한 문서 완성',
            ],
            ac=[
                'AI Assistant 2-Pager 문서 초안 완성',
                '주요 기능 및 가치 제안 포함 여부 확인',
            ],
        ),
    },
    {
        'summary': 'MATCH 방향성 문서 업데이트',
        'description': make_doc(
            background='현재 MATCH 방향성 문서에 수집된 피드백 및 전략 옵션(A/B/C)을 반영하여 "방향성 논의" → "요구사항 전달" 문서로 성격 전환 및 최신화한다.',
            tasks=[
                'TL;DR / Executive Summary 상단 신설',
                '앱테크 역할 분리 및 보상 스킴 범위 명확화',
                '전략 옵션(A/B/C) 섹션 추가',
                '증분 데이터 및 비용 현황(78원/건) 반영',
            ],
            ac=[
                'Confluence 문서 업데이트 완료',
                '댓글 P0 항목 전체 반영 확인',
            ],
        ),
    },
]

results = []
for t in TICKETS:
    payload = {
        'fields': {
            'project':     {'key': 'MEMB'},
            'summary':     t['summary'],
            'issuetype':   {'id': TASK_TYPE_ID},
            'priority':    {'name': 'Medium'},
            'duedate':     DUE_DATE,
            'assignee':    {'accountId': ASSIGNEE_ID},
            'description': t['description'],
        }
    }
    try:
        res = jira_post('/issue', payload)
        key = res.get('key', '?')
        print(f'✅ {key} — {t["summary"]}')
        print(f'   {HOST}/browse/{key}')
        results.append({'key': key, 'url': f'{HOST}/browse/{key}'})
    except Exception as e:
        print(f'❌ 실패: {t["summary"]} — {e}')
        results.append({'key': None, 'error': str(e)})

print('\n=== 완료 ===')
