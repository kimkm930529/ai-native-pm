#!/usr/bin/env python3
"""
MEMB Task 티켓 생성 — PM Studio MCP/API 연동 + 라이브커머스 푸시 분석
생성일: 2026-03-20
"""
import sys, os, json, base64, urllib.request, urllib.parse
from pathlib import Path

for line in Path(__file__).parents[1].joinpath('.env').read_text().splitlines():
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, _, v = line.partition('=')
        os.environ.setdefault(k.strip(), v.strip())

HOST  = os.environ.get('CONFLUENCE_URL','').rstrip('/')
EMAIL = os.environ.get('CONFLUENCE_EMAIL','')
TOKEN = os.environ.get('CONFLUENCE_API_TOKEN','')
CREDS = base64.b64encode(f'{EMAIL}:{TOKEN}'.encode()).decode()
HEADERS = {'Authorization': f'Basic {CREDS}', 'Content-Type': 'application/json'}
ASSIGNEE_ID = '712020:9bbd1f66-a6e3-4385-957b-56995ea34f89'
TASK_TYPE_ID = '10006'

def jira_post(path, payload):
    url = f'{HOST}/rest/api/3{path}'
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, headers=HEADERS, method='POST')
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

def make_doc(*sections):
    """sections: list of (heading, bullet_list)"""
    content = []
    for heading, items in sections:
        content.append({'type':'heading','attrs':{'level':2},'content':[{'type':'text','text':heading}]})
        content.append({'type':'bulletList','content':[
            {'type':'listItem','content':[{'type':'paragraph','content':[{'type':'text','text':item}]}]}
            for item in items
        ]})
    return {'type':'doc','version':1,'content':content}

TICKETS = [
    {
        'summary': 'Databricks API 연동 설정 (PM Studio 데이터팀 활성화)',
        'priority': 'High',
        'duedate': '2026-03-28',
        'labels': ['PM-Studio', 'Databricks', '연동설정'],
        'description': make_doc(
            ('배경', [
                'PM Studio에 데이터팀 에이전트(Unity Catalog 탐색 · 자연어 SQL · 데이터 분석) 구축 완료.',
                'Databricks 워크스페이스 자격증명(환경변수) 등록 및 연결 검증이 필요함.',
                '완료 후 /databricks 스킬로 즉시 데이터 탐색·분석 가능.',
            ]),
            ('작업 내용', [
                '1) Databricks 워크스페이스 접속 → User Settings → Developer → Access Tokens → 토큰 발급',
                '2) .env에 DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_WAREHOUSE_ID 추가',
                '3) python3 databricks-agent-system/scripts/client.py --check 로 연결 확인',
                '4) (선택) MCP 서버 방식: pip install databricks-mcp 후 .claude/mcp.json에 서버 등록',
                '  참고 설정: databricks-agent-system/CLAUDE.md §Step 0 연결 설정 가이드',
            ]),
            ('완료 기준 (AC)', [
                '[ ] client.py --check 실행 시 {"status": "ok", "user": "..."} 반환',
                '[ ] /databricks --explore 실행 시 Unity Catalog 카탈로그 목록 출력',
                '[ ] /databricks --analyze [table] "분석주제" 실행 시 인사이트 리포트 생성',
                '[ ] (선택) MCP 방식: Claude에서 자연어로 Databricks 쿼리 직접 실행 확인',
            ]),
            ('연동 방법 상세', [
                'REST API 방식 (방식 A, 기본):',
                '  export DATABRICKS_HOST=https://your-workspace.azuredatabricks.net',
                '  export DATABRICKS_TOKEN=dapi-xxxxxxxxxxxxxxxxxx',
                '  export DATABRICKS_WAREHOUSE_ID=xxxxxxxxxxxxxxxx',
                'MCP 서버 방식 (방식 B, 선택):',
                '  pip install databricks-mcp',
                '  .claude/mcp.json에 {"mcpServers":{"databricks":{"command":"uvx","args":["databricks-mcp"],"env":{"DATABRICKS_HOST":"...","DATABRICKS_TOKEN":"..."}}}} 추가',
            ]),
        ),
    },
    {
        'summary': 'Slack Bot 연동 설정 (PM Studio 협업팀 활성화)',
        'priority': 'High',
        'duedate': '2026-03-28',
        'labels': ['PM-Studio', 'Slack', '연동설정'],
        'description': make_doc(
            ('배경', [
                'PM Studio에 협업팀 에이전트(Slack 대화 조회·요약, 결정사항·Action Item 추출) 구축 완료.',
                'Slack Bot Token 발급 및 채널 초대가 필요함.',
                '완료 후 /slack --today, /slack --week 스킬로 채널 대화를 자동 요약 가능.',
            ]),
            ('작업 내용', [
                '1) https://api.slack.com/apps → Create New App → From Scratch',
                '2) OAuth & Permissions → Bot Token Scopes 추가:',
                '   channels:history (채널 메시지 읽기)',
                '   channels:read (채널 목록 조회)',
                '   users:read (사용자 이름 조회)',
                '   chat:write (메시지 발송, /slack --send 사용 시)',
                '3) Install App to Workspace → Bot User OAuth Token 복사',
                '4) .env에 SLACK_BOT_TOKEN=xoxb-... 추가',
                '5) Bot을 읽을 채널에 /invite @봇이름 으로 초대',
                '6) python3 slack-agent-system/scripts/client.py --check 로 연결 확인',
                '  참고: slack-agent-system/CLAUDE.md §Step 0 연결 설정 가이드',
            ]),
            ('완료 기준 (AC)', [
                '[ ] client.py --check 실행 시 {"status":"ok","bot":"...","workspace":"..."} 반환',
                '[ ] /slack --today #match-pm 실행 시 오늘 대화 수집 및 요약 출력',
                '[ ] /slack --week 실행 시 이번 주 주요 결정사항·Action Item 추출',
                '[ ] /pgm 파이프라인과 연계하여 Slack 요약이 Flash Report에 보완됨',
            ]),
        ),
    },
    {
        'summary': 'Figma API 연동 설정 (PM Studio 디자인팀 활성화)',
        'priority': 'Medium',
        'duedate': '2026-04-04',
        'labels': ['PM-Studio', 'Figma', '연동설정'],
        'description': make_doc(
            ('배경', [
                'PM Studio에 디자인팀 에이전트(Figma 화면 분석·설계서 생성·PRD 초안) 구축 완료.',
                'Figma Personal Access Token 발급 및 .env 등록이 필요함.',
                '완료 후 /figma [URL] 스킬로 화면 분석·설계서·PRD 자동 생성 가능.',
            ]),
            ('작업 내용', [
                '1) figma.com에 로그인',
                '2) 우측 상단 프로필 → Settings → Security 탭',
                '3) Personal access tokens → Generate new token → 이름 입력 후 발급',
                '4) .env에 FIGMA_ACCESS_TOKEN=figd_xxxxxxxx 추가',
                '5) python3 figma-agent-system/scripts/client.py --check 로 연결 확인',
                '  참고: figma-agent-system/CLAUDE.md §Step 0 연결 설정 가이드',
            ]),
            ('완료 기준 (AC)', [
                '[ ] client.py --check 실행 시 {"status":"ok","user":"...","email":"..."} 반환',
                '[ ] /figma [Figma URL] 실행 시 화면 구조 분석 리포트 생성',
                '[ ] /figma [URL] --spec 실행 시 화면 설계서 MD 파일 생성',
                '[ ] /figma [URL] --prd 실행 시 PRD 초안이 prd-agent-system/output에 저장됨',
            ]),
            ('활용 시나리오', [
                '/figma [URL] → 화면 구조 파악 후 /prd 연계',
                '/figma [URL] --spec → 개발팀 전달용 설계서 → Confluence 저장',
                '/figma [URL] --compare [URL2] → Before/After 변경사항 정리',
                '/figma [URL] --copy → UX 카피 전체 추출',
            ]),
        ),
    },
    {
        'summary': '라이브커머스 푸시 동선·데이터 분석 및 개선 전략 수립',
        'priority': 'High',
        'duedate': '2026-03-28',
        'labels': ['MATCH', '라이브커머스', '푸시', '분석'],
        'description': make_doc(
            ('배경', [
                '라이브커머스 기능의 푸시 알림 효율 개선을 위한 탐색 과제.',
                '현재 라이브 푸시 동선이 명확히 문서화되어 있지 않으며, 데이터 기반 성과 분석이 필요함.',
                '이를 통해 라이브커머스 푸시 전략을 고도화하고, 필요 시 PRD 기획으로 연결 예정.',
            ]),
            ('작업 내용', [
                '1) 라이브커머스 푸시 유형 및 발송 조건 정리 (동선 맵핑)',
                '   - 발송 트리거: 라이브 시작 / N분 전 / 특정 브랜드 팔로우 등',
                '   - 발송 대상 세그먼트 기준',
                '   - 채널별 발송 경로 (Braze, OCMP 등)',
                '2) 현재 라이브 푸시 성과 데이터 조회',
                '   - 발송량, CTR, 전환율(구매), 수신거부율 현황',
                '   - 시간대별 / 브랜드별 / 세그먼트별 성과 비교',
                '3) 경쟁사 라이브커머스 푸시 전략 벤치마크 (3개 이상)',
                '4) 개선 방향 도출 및 우선순위 제안',
                '5) 결과 Confluence 정리 및 필요 시 /prd로 연결',
            ]),
            ('완료 기준 (AC)', [
                '[ ] 라이브커머스 푸시 동선도(Flow) 작성 완료',
                '[ ] 주요 지표(CTR, 전환율, 수신거부율) 현황 데이터 확보',
                '[ ] 벤치마크 3개 서비스 이상 분석',
                '[ ] 개선 방향 3건 이상 도출 및 우선순위화',
                '[ ] 결과를 Confluence에 정리 (링크 기재)',
            ]),
            ('참고 도구', [
                'Databricks 데이터 탐색: /databricks --analyze [라이브관련 테이블] "라이브 푸시 성과"',
                '경쟁사 분석: /discovery --ref all "라이브커머스 푸시 전략"',
                'PRD 연계: 개선 방향 확정 후 /prd 로 기획 문서 자동 생성',
            ]),
        ),
    },
]

results = []
for t in TICKETS:
    payload = {
        'fields': {
            'project': {'key': 'MEMB'},
            'summary': t['summary'],
            'issuetype': {'id': TASK_TYPE_ID},
            'priority': {'name': t['priority']},
            'duedate': t['duedate'],
            'description': t['description'],
            'assignee': {'accountId': ASSIGNEE_ID},
            'labels': t['labels'],
        }
    }
    try:
        res = jira_post('/issue', payload)
        key = res.get('key','?')
        print(f'✅ {key} — {t["summary"]}')
        print(f'   {HOST}/browse/{key}')
        results.append({'key': key, 'summary': t['summary'], 'url': f'{HOST}/browse/{key}'})
    except Exception as e:
        print(f'❌ 실패: {t["summary"]}')
        print(f'   {e}')
        results.append({'key': None, 'summary': t['summary'], 'error': str(e)})

print('\n=== 완료 ===')
print(json.dumps(results, ensure_ascii=False, indent=2))
