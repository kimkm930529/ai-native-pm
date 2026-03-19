#!/usr/bin/env python3
"""
Jira Bulk Ticket Creator — TM-2061 하위 [BE][CME] Epics + Tasks
사용법: python3 scripts/create_jira_cme_tickets.py
"""

import os, base64, json, time
import urllib.request, urllib.error

EMAIL     = os.environ.get("CONFLUENCE_EMAIL", "")
TOKEN     = os.environ.get("CONFLUENCE_API_TOKEN", "")
BASE_URL  = "https://musinsa-oneteam.atlassian.net"
AUTH      = "Basic " + base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()

PROJECT_KEY        = "PSN"
EPIC_TYPE_ID       = "10000"
TASK_TYPE_ID       = "10006"
PARENT_INITIATIVE  = "TM-2061"
LABELS             = ["26-Q1", "CDP", "MATCH", "캠페인메타엔진"]


# ─── ADF 헬퍼 ────────────────────────────────────────────────────────────────

def para(text: str) -> dict:
    return {"type": "paragraph", "content": [{"type": "text", "text": text}]}

def heading(level: int, text: str) -> dict:
    return {"type": "heading", "attrs": {"level": level},
            "content": [{"type": "text", "text": text}]}

def bullet_list(items: list[str]) -> dict:
    return {
        "type": "bulletList",
        "content": [
            {"type": "listItem",
             "content": [{"type": "paragraph",
                          "content": [{"type": "text", "text": item}]}]}
            for item in items
        ],
    }

def adf(*blocks) -> dict:
    return {"type": "doc", "version": 1, "content": list(blocks)}


# ─── Jira API ────────────────────────────────────────────────────────────────

def create_issue(fields: dict):
    url  = f"{BASE_URL}/rest/api/3/issue"
    body = json.dumps({"fields": fields}).encode("utf-8")
    req  = urllib.request.Request(
        url, data=body,
        headers={"Authorization": AUTH, "Accept": "application/json",
                 "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("key")
    except urllib.error.HTTPError as e:
        print(f"    [ERROR] HTTP {e.code}: {e.read().decode()[:200]}")
        return None


def build_fields(summary, issue_type_id, parent_key,
                 priority, duedate, description_adf):
    return {
        "project":     {"key": PROJECT_KEY},
        "summary":     summary,
        "issuetype":   {"id": issue_type_id},
        "parent":      {"key": parent_key},
        "labels":      LABELS,
        "priority":    {"name": priority},
        "duedate":     duedate,
        "description": description_adf,
    }


# ─── 티켓 데이터 ─────────────────────────────────────────────────────────────

EPICS = [
    # ── 1. CDC / 인프라 ──────────────────────────────────────────────────────
    {
        "summary":  "[BE][CME] CDC / 인프라",
        "priority": "High",
        "duedate":  "2026-03-14",
        "description": adf(
            para("PostgreSQL → Debezium → Kafka 파이프라인 구축. "
                 "campaign_sync, campaign_asset, campaign_cms_meta 테이블의 변경사항을 "
                 "CDC(Change Data Capture)로 캡처하여 ML 결과 처리 파이프라인과 연결한다."),
            heading(3, "배경 (HLD 참조)"),
            para("HLD §4.7 저장소 매핑: CMS Integration → PG campaign 테이블(신규), "
                 "Audience Evaluation → PG cohort + CH cohort_users(기존). "
                 "CDC는 이 데이터의 실시간 변경 이벤트를 하류 ML Consumer에 전달하는 인프라 레이어."),
            heading(3, "작업 범위"),
            bullet_list([
                "PostgreSQL wal_level = logical 설정",
                "Debezium Connector 구성 및 배포 (3개 테이블)",
                "ML 결과 Kafka Consumer DLQ 처리",
            ]),
        ),
        "tasks": [
            {
                "summary":  "PostgreSQL wal_level logical 설정",
                "priority": "High",
                "duedate":  "2026-03-10",
                "description": adf(
                    para("PostgreSQL의 wal_level을 logical로 변경하여 Debezium CDC 활성화를 위한 사전 준비 작업."),
                    heading(3, "작업 내용"),
                    bullet_list([
                        "postgresql.conf: wal_level = logical 설정",
                        "max_replication_slots, max_wal_senders 값 조정",
                        "대상 테이블: campaign_sync, campaign_asset, campaign_cms_meta",
                        "설정 변경 후 PostgreSQL 재시작 및 replication slot 생성 확인",
                    ]),
                    heading(3, "주의사항"),
                    para("운영 DB 설정 변경이므로 DBA 협의 및 유지보수 윈도우 내 진행 필요."),
                ),
            },
            {
                "summary":  "Debezium Connector 설정 및 배포 (campaign_sync, campaign_asset, campaign_cms_meta)",
                "priority": "High",
                "duedate":  "2026-03-12",
                "description": adf(
                    para("Debezium PostgreSQL Connector를 구성하고 Kafka와 연동하여 "
                         "3개 테이블의 INSERT/UPDATE/DELETE 이벤트를 스트리밍한다."),
                    heading(3, "작업 내용"),
                    bullet_list([
                        "Debezium Connector JSON 설정 작성 (database.hostname, slot.name 등)",
                        "campaign_sync, campaign_asset, campaign_cms_meta 테이블 대상 지정",
                        "Kafka Topic 네이밍 컨벤션 결정 및 생성",
                        "Connector 배포 및 이벤트 흐름 검증",
                    ]),
                    heading(3, "HLD 참조"),
                    para("HLD §6.3: 새 어디언스 소스 추가 시 Audience Evaluation 경로만 추가, 하류 모듈 변경 없음."),
                ),
            },
            {
                "summary":  "ML 결과 Kafka Consumer DLQ 처리",
                "priority": "Medium",
                "duedate":  "2026-03-14",
                "description": adf(
                    para("ML 모델링 결과를 Kafka Consumer로 처리하고, 처리 실패 메시지를 "
                         "DLQ(Dead Letter Queue)로 격리하여 재처리할 수 있도록 구현한다."),
                    heading(3, "작업 내용"),
                    bullet_list([
                        "Kafka Consumer 구현 (ML 결과 topic 구독)",
                        "DLQ 토픽 설정 및 실패 메시지 라우팅 로직 구현",
                        "재처리 메커니즘 (retry with backoff) 구현",
                        "DLQ 모니터링 알림 설정 (Slack 연동)",
                    ]),
                    heading(3, "HLD 참조"),
                    para("HLD §6.2: Inbox 적재 실패 → Global Optimization Job 재실행 (멱등성 보장 필요)."),
                ),
            },
        ],
    },

    # ── 2. Mock API ──────────────────────────────────────────────────────────
    {
        "summary":  "[BE][CME] Mock API",
        "priority": "Medium",
        "duedate":  "2026-03-14",
        "description": adf(
            para("FE 개발 병행을 위한 Mock API 제공. "
                 "실제 BE API 완성 전 FE 팀이 Sync, Campaign Asset, CMS 연동, 엑셀 업로드 "
                 "4개 도메인을 병행 개발할 수 있도록 응답 스펙을 고정한 Mock 엔드포인트를 제공한다."),
            heading(3, "배경"),
            para("Phase 1 마감(2026-03-31)까지 FE/BE 병행 개발이 필수. "
                 "BE API 완성을 기다리지 않고 FE가 독립적으로 개발·테스트할 수 있어야 한다."),
            heading(3, "제공 도메인"),
            bullet_list([
                "Sync CRUD / Braze 검증 Mock",
                "Campaign Asset CRUD / 상태 전환 Mock",
                "CMS 프록시 (landing_url 메타, 소재 탐색) Mock",
                "엑셀 업로드 / 유효성 검사 Mock",
            ]),
        ),
        "tasks": [
            {
                "summary":  "FE 병행 개발용 Mock API 제공 (Sync, Campaign, CMS, 엑셀)",
                "priority": "Medium",
                "duedate":  "2026-03-14",
                "description": adf(
                    para("4개 도메인 전체를 커버하는 Mock API 서버를 구축한다. "
                         "실제 API 스펙(request/response schema)과 동일하게 유지하여 "
                         "BE 완성 후 FE 코드 변경 없이 연동 전환 가능하도록 한다."),
                    heading(3, "Mock 엔드포인트 목록"),
                    bullet_list([
                        "POST /api/syncs, GET /api/syncs/{id}, PUT, DELETE",
                        "POST /api/campaign-assets, GET, PUT, DELETE + 상태 전환",
                        "POST /api/cms/meta?landing_url=..., GET /api/cms/search",
                        "GET /api/excel/template, POST /api/excel/upload",
                    ]),
                    heading(3, "구현 방식"),
                    para("WireMock 또는 Spring MockMvc 기반 Mock 서버. "
                         "응답 데이터는 실제 스키마 기반 샘플 데이터로 고정."),
                ),
            },
        ],
    },

    # ── 3. Sync 관리 ─────────────────────────────────────────────────────────
    {
        "summary":  "[BE][CME] Sync 관리",
        "priority": "High",
        "duedate":  "2026-03-19",
        "description": adf(
            para("MATCH ↔ Braze 연결 어댑터 레이어. Braze Campaign ID 기반으로 캠페인 설정을 "
                 "Braze에 전달하고 API-triggered 발송 방식을 관리한다."),
            heading(3, "배경 (Context.md 참조)"),
            para("Sync 구축은 이미 완료(Red Sync — MATCH ↔ Braze 어댑터 레이어). "
                 "Phase 1에서는 CRUD API, 유효성 검증, 삭제 처리, 알림 스케줄러를 추가 구현한다."),
            heading(3, "핵심 정책"),
            bullet_list([
                "코호트 설정: 자동 코호트(마케팅 수신 동의 전체) vs 사용자 지정 코호트",
                "발송 주기/기간 설정 — '종료일 없음' 옵션 포함",
                "Phase 1: 개인화 변수 설정 제거 (Message Template 영역은 Phase 2)",
            ]),
        ),
        "tasks": [
            {
                "summary":  "Sync CRUD API",
                "priority": "High",
                "duedate":  "2026-03-14",
                "description": adf(
                    para("Sync 생성·조회·수정·삭제 REST API 구현. "
                         "Braze Campaign ID를 입력받아 Sync를 생성하고 관리한다."),
                    heading(3, "주요 필드"),
                    bullet_list([
                        "braze_campaign_id: Braze Campaign ID (필수)",
                        "cohort_type: AUTO | CUSTOM",
                        "schedule_type: ONCE | RECURRING",
                        "start_dt / end_dt (end_dt: nullable — 종료일 없음 옵션)",
                    ]),
                    heading(3, "HLD 참조"),
                    para("HLD §4.3: Braze API → 발송 방향, Send Router Worker 플러그인 인터페이스."),
                ),
            },
            {
                "summary":  "Braze Campaign ID 유효성 검증 API",
                "priority": "High",
                "duedate":  "2026-03-14",
                "description": adf(
                    para("Sync 생성 시 입력된 Braze Campaign ID의 실존 여부와 유효성을 "
                         "Braze API를 통해 실시간으로 검증하는 API."),
                    heading(3, "검증 항목"),
                    bullet_list([
                        "Braze API 호출로 Campaign 존재 여부 확인",
                        "Campaign 상태(ACTIVE/STOPPED) 반환",
                        "Campaign 이름, 발송 채널 타입 메타 반환",
                    ]),
                    heading(3, "응답 예시"),
                    para('{ "valid": true, "campaign_name": "...", "status": "ACTIVE" }'),
                ),
            },
            {
                "summary":  "Sync 삭제 시 하위 캠페인 STOPPED 일괄 처리",
                "priority": "Medium",
                "duedate":  "2026-03-17",
                "description": adf(
                    para("Sync 삭제 이벤트 발생 시 해당 Sync에 연결된 모든 Campaign Asset을 "
                         "STOPPED 상태로 일괄 전환하는 로직."),
                    heading(3, "처리 흐름"),
                    bullet_list([
                        "DELETE /api/syncs/{id} 호출",
                        "연관 Campaign Asset 목록 조회",
                        "전체 status → STOPPED 일괄 업데이트 (트랜잭션)",
                        "Braze에 캠페인 중단 신호 전송",
                    ]),
                    heading(3, "정책"),
                    para("부분 성공 불가 — 트랜잭션 실패 시 Sync 삭제도 롤백."),
                ),
            },
            {
                "summary":  "종료일 없는 Sync 365일 경과 슬랙 알림 스케줄러",
                "priority": "Low",
                "duedate":  "2026-03-19",
                "description": adf(
                    para("'종료일 없음' 옵션으로 생성된 Sync 중 365일이 경과한 항목을 감지하여 "
                         "담당자에게 Slack 알림을 발송하는 배치 스케줄러."),
                    heading(3, "구현 방식"),
                    bullet_list([
                        "HLD Shared Scheduler(EventBridge) 활용 — 매일 자정 실행",
                        "조건: end_dt IS NULL AND created_at <= NOW() - INTERVAL '365 days'",
                        "Slack Webhook으로 담당자 및 운영 채널에 알림",
                    ]),
                    heading(3, "HLD 참조"),
                    para("HLD §1: Shared Scheduler — EventBridge 통합 + Job 간 의존성 명시화."),
                ),
            },
        ],
    },

    # ── 4. Campaign Asset 관리 ───────────────────────────────────────────────
    {
        "summary":  "[BE][CME] Campaign Asset 관리",
        "priority": "High",
        "duedate":  "2026-03-22",
        "description": adf(
            para("홍보 대상(기획전, 매거진, 라이브)의 표준화된 소재 정보 단위 관리. "
                 "landing_url 기반 CMS 메타 자동 수집·정규화, UTM 파라미터 포함 push_url 자동 생성, "
                 "소재 생명주기 상태 관리를 담당한다."),
            heading(3, "배경 (HLD 참조)"),
            para("HLD P1 문제: 캠페인 메타엔진 부재 — landing URL 메타 없음. "
                 "ML이 피처로 활용 불가 → 최적화 성과 한계. "
                 "Campaign Asset 표준 스키마 정의로 해결."),
            heading(3, "Phase 1 소재 범위"),
            bullet_list(["기획전", "매거진", "라이브 (상품 단위 제외 — Phase 2)"]),
        ),
        "tasks": [
            {
                "summary":  "Campaign Asset CRUD API",
                "priority": "High",
                "duedate":  "2026-03-17",
                "description": adf(
                    para("Campaign Asset 생성·조회·수정·삭제 REST API 구현."),
                    heading(3, "주요 필드 (엑셀 템플릿 기준)"),
                    bullet_list([
                        "send_dt: YYYY-MM-DD",
                        "target: 전체 | 남성 | 여성",
                        "ad_code: APSCMCD 형식 (필수)",
                        "brand_id: 미입력 시 landing_url 기준 자동 적용",
                        "landing_url, image_url, title, contents (필수)",
                        "priority: 정수 (낮을수록 높음)",
                    ]),
                    heading(3, "HLD 참조"),
                    para("HLD §4.7: CMS Integration → PG cohort_meta 확장, 신규 campaign 테이블."),
                ),
            },
            {
                "summary":  "중복 체크 API (send_dt + gender + ad_code)",
                "priority": "Medium",
                "duedate":  "2026-03-19",
                "description": adf(
                    para("send_dt + gender(target) + ad_code 복합 키 조합으로 "
                         "중복 소재 등록을 방지하는 유효성 검사 API."),
                    heading(3, "호출 시점"),
                    bullet_list([
                        "단건 Campaign Asset 등록 시",
                        "엑셀 업로드 유효성 검사 시 (행별 체크)",
                    ]),
                    heading(3, "응답"),
                    para('{ "duplicate": true, "existing_id": 123, "existing_summary": "..." }'),
                ),
            },
            {
                "summary":  "push_url 자동 생성 로직 (UTM 조합)",
                "priority": "Medium",
                "duedate":  "2026-03-21",
                "description": adf(
                    para("소재 등록 시 landing_url에 UTM 파라미터를 조합하여 push_url을 자동 생성한다."),
                    heading(3, "UTM 포맷 (Context.md §3 참조)"),
                    para("?utm_source=app_push&utm_medium=cr&utm_content=mf"
                         "&utm_campaign={ad_code}&source={ad_code}"),
                    heading(3, "처리 규칙"),
                    bullet_list([
                        "landing_url에 이미 query string이 있는 경우 & 로 이어붙임",
                        "ad_code는 APSCMCD 형식 검증 후 주입",
                        "생성된 push_url은 DB에 저장 (변경 불가 — 스냅샷 정책)",
                    ]),
                ),
            },
            {
                "summary":  "상태 전환 로직 (SCHEDULED / SENT / UNSENT / STOPPED)",
                "priority": "High",
                "duedate":  "2026-03-22",
                "description": adf(
                    para("Campaign Asset의 생명주기 상태 전환 로직 구현."),
                    heading(3, "상태 전이 규칙"),
                    bullet_list([
                        "등록 시: SCHEDULED",
                        "발송 완료: SCHEDULED → SENT",
                        "ML 미매칭 / 발송 제외: SCHEDULED → UNSENT",
                        "Sync 삭제 또는 수동 중단: → STOPPED",
                    ]),
                    heading(3, "HLD 참조"),
                    para("HLD §4.4: 모델링 완료 후 Inbox Optimizer가 최종 발송 판단 — "
                         "SENT/UNSENT는 Inbox Optimizer 결과를 반영한 상태."),
                ),
            },
        ],
    },

    # ── 5. CMS 연동 ──────────────────────────────────────────────────────────
    {
        "summary":  "[BE][CME] CMS 연동 (musinsa-data → ocmp → musinsa)",
        "priority": "High",
        "duedate":  "2026-03-26",
        "description": adf(
            para("musinsa-data → ocmp → musinsa 네트워크 경로를 통해 "
                 "무신사 CMS(CPCMS)의 콘텐츠 메타데이터(브랜드, 할인율, 종료일 등)를 자동 수집한다. "
                 "ocmp가 프록시 역할을 담당한다."),
            heading(3, "배경 (HLD 참조)"),
            para("HLD §4.3 외부 서비스 의존 관계: 무신사 CMS ← 수신, CMS Adapter 인터페이스. "
                 "HLD P1: 캠페인 메타엔진 부재 — landing URL 메타 없음, ML 피처 활용 불가."),
            heading(3, "Phase 1 제약"),
            para("데이터 스냅샷 방식: 등록 시점 데이터 보존. 이후 CMS 원본 변경 시 즉시 동기화 불가."),
        ),
        "tasks": [
            {
                "summary":  "ocmp에 CMS 프록시 API 개발·배포 (landing_url 메타 수집, 소재 탐색)",
                "priority": "High",
                "duedate":  "2026-03-17",
                "description": adf(
                    para("ocmp 서비스에 무신사 CMS(CPCMS) 프록시 API를 개발·배포한다. "
                         "landing_url 메타 수집 및 소재 탐색 기능을 포함하며 "
                         "HLD CMS Adapter 인터페이스를 구현한다."),
                    heading(3, "제공 엔드포인트"),
                    bullet_list([
                        "GET /cms/meta?landing_url={url} — landing URL 메타데이터 수집",
                        "GET /cms/search?keyword={kw}&type={기획전|매거진|라이브} — 소재 탐색",
                    ]),
                    heading(3, "수집 메타 항목"),
                    bullet_list(["브랜드(brand_id)", "할인율", "종료일", "콘텐츠 유형", "썸네일 URL"]),
                ),
            },
            {
                "summary":  "musinsa-data ↔ ocmp 네트워크 연결 확인",
                "priority": "High",
                "duedate":  "2026-03-12",
                "description": adf(
                    para("musinsa-data 서비스와 ocmp 간 네트워크 방화벽 정책, 포트 개방 여부를 확인하고 "
                         "실제 연결 테스트를 수행한다."),
                    heading(3, "확인 항목"),
                    bullet_list([
                        "방화벽 정책 확인 (musinsa-data → ocmp 포트 허용 여부)",
                        "DNS 해석 및 응답 레이턴시 측정",
                        "curl/telnet 기반 연결 테스트",
                        "필요 시 인프라팀에 방화벽 정책 요청",
                    ]),
                ),
            },
            {
                "summary":  "ocmp ↔ musinsa 네트워크 연결 확인",
                "priority": "High",
                "duedate":  "2026-03-12",
                "description": adf(
                    para("ocmp와 musinsa 서비스 간 네트워크 방화벽 정책, 포트 개방 여부를 확인하고 "
                         "실제 연결 테스트를 수행한다."),
                    heading(3, "확인 항목"),
                    bullet_list([
                        "방화벽 정책 확인 (ocmp → musinsa CMS API 포트 허용 여부)",
                        "DNS 해석 및 응답 레이턴시 측정",
                        "curl/telnet 기반 연결 테스트",
                        "필요 시 인프라팀에 방화벽 정책 요청",
                    ]),
                ),
            },
            {
                "summary":  "landing_url 유형 판별 + CMS 메타 수집 API (ocmp 경유)",
                "priority": "High",
                "duedate":  "2026-03-21",
                "description": adf(
                    para("landing_url의 유형(기획전/매거진/라이브)을 판별하고 "
                         "CMS API를 통해 메타데이터를 수집하여 Campaign Asset 표준 스키마로 정규화한다."),
                    heading(3, "유형 판별 규칙"),
                    bullet_list([
                        "URL 패턴 기반 자동 분류 (예: /events/ → 기획전, /magazine/ → 매거진)",
                        "CMS API로 콘텐츠 유형 재확인",
                        "판별 불가 시: 사용자 직접 입력 요청",
                    ]),
                    heading(3, "정규화 출력"),
                    bullet_list(["brand_id", "discount_rate", "end_dt", "content_type", "thumbnail_url"]),
                ),
            },
            {
                "summary":  "CMS 소재 탐색·검색 API (ocmp 경유)",
                "priority": "Medium",
                "duedate":  "2026-03-24",
                "description": adf(
                    para("키워드 또는 조건 기반으로 CMS 내 소재를 탐색·검색하는 API. "
                         "Campaign Asset 등록 시 소재를 찾는 용도로 사용한다."),
                    heading(3, "검색 조건"),
                    bullet_list([
                        "키워드: 브랜드명, 기획전명",
                        "필터: 소재 유형(기획전/매거진/라이브), 발송 가능 여부",
                        "Phase 1 범위: 기획전, 매거진, 라이브 (상품 단위 제외)",
                    ]),
                    heading(3, "HLD 참조"),
                    para("HLD §3.1 In-Scope: CMS Integration Layer — campaign_id 체계 + 캠페인 메타데이터 수신."),
                ),
            },
            {
                "summary":  "Campaign Asset 등록 시 CMS 메타 스냅샷 저장",
                "priority": "Medium",
                "duedate":  "2026-03-26",
                "description": adf(
                    para("소재 등록 시점의 CMS 메타데이터를 스냅샷으로 DB에 저장한다. "
                         "이후 CMS 원본이 변경되어도 등록 시점 데이터를 보존한다."),
                    heading(3, "스냅샷 저장 항목"),
                    bullet_list([
                        "brand_id, discount_rate, end_dt, content_type, thumbnail_url",
                        "snapshot_at: 저장 시각",
                        "cms_source_url: 원본 CMS URL",
                    ]),
                    heading(3, "Phase 1 제약 (Context.md 참조)"),
                    para("데이터 스냅샷 방식 — 등록 이후 CMS 원본 변경 시 즉시 동기화 불가 (Phase 1). "
                         "Phase 2에서 동기화 전략 고도화 예정."),
                ),
            },
        ],
    },

    # ── 6. 엑셀 일괄 등록 ───────────────────────────────────────────────────
    {
        "summary":  "[BE][CME] 엑셀 일괄 등록",
        "priority": "High",
        "duedate":  "2026-03-28",
        "description": adf(
            para("기존 세일즈푸시 엑셀 운영 프로세스를 MATCH 시스템으로 100% 이관. "
                 "최대 1,000행, 전체 롤백 정책(부분 성공 불가), 서버 유효성 검사를 포함한다."),
            heading(3, "배경 (Context.md Phase 1 목표)"),
            para("기존 엑셀 기반 세일즈푸시 운영 프로세스를 MATCH 시스템으로 100% 이관이 Phase 1 핵심 목표. "
                 "HLD P4: 엑셀 기반 캠페인 세팅 — 정합성·유지보수 문제 (Critical)."),
            heading(3, "핵심 정책"),
            bullet_list([
                "최대 1,000행 업로드",
                "전체 중 하나라도 오류 시 전체 업로드 취소 (부분 성공 불가)",
                "실패 행 번호 + 사유 상세 반환",
            ]),
        ),
        "tasks": [
            {
                "summary":  "엑셀 템플릿 다운로드 API",
                "priority": "Medium",
                "duedate":  "2026-03-21",
                "description": adf(
                    para("사용자가 다운로드할 수 있는 엑셀 템플릿 파일을 생성·제공하는 API."),
                    heading(3, "템플릿 필드 (Context.md §2 참조)"),
                    bullet_list([
                        "send_dt (필수): YYYY-MM-DD",
                        "target (필수): 전체/남성/여성",
                        "priority (선택): 정수",
                        "ad_code (필수): APSCMCD 형식",
                        "brand_id (선택): 미입력 시 landing_url 기준 자동 적용",
                        "braze_campaign_name, title, contents, landing_url, image_url (필수)",
                    ]),
                    heading(3, "제거된 칼럼 (기존 대비)"),
                    para("send_time, send_day_cd, category, push_url, setting_yn"),
                ),
            },
            {
                "summary":  "엑셀 업로드 + 서버 유효성 검사 API",
                "priority": "High",
                "duedate":  "2026-03-24",
                "description": adf(
                    para("엑셀 파일을 업로드받아 서버 측에서 각 행의 유효성을 검사하는 API."),
                    heading(3, "유효성 검사 항목"),
                    bullet_list([
                        "send_dt: YYYY-MM-DD 형식 검증",
                        "ad_code: APSCMCD 형식 정규식 검증",
                        "중복 체크: send_dt + target + ad_code 복합 키",
                        "landing_url: URL 형식 + CMS 등록 여부 확인",
                        "최대 행수: 1,000행 초과 시 즉시 거부",
                    ]),
                    heading(3, "처리 정책"),
                    para("전체 행 유효성 검사 완료 후 모두 통과 시에만 DB 저장 진행."),
                ),
            },
            {
                "summary":  "업로드 실패 시 전체 롤백 + 실패 행/사유 반환",
                "priority": "High",
                "duedate":  "2026-03-24",
                "description": adf(
                    para("유효성 검사 또는 DB 저장 중 하나라도 실패 시 전체 트랜잭션을 롤백하고 "
                         "실패 행 번호와 사유를 상세히 반환한다."),
                    heading(3, "응답 포맷"),
                    para('{ "success": false, "total": 50, "failed_rows": '
                         '[{"row": 5, "reason": "ad_code 형식 오류"}, ...] }'),
                    heading(3, "구현 요건"),
                    bullet_list([
                        "DB 트랜잭션 단위: 전체 업로드 1개 트랜잭션",
                        "실패 즉시 전체 롤백 (부분 성공 불가)",
                        "사용자가 실패 내용을 확인 후 수정·재업로드 가능하도록 안내",
                    ]),
                ),
            },
            {
                "summary":  "미등록 소재 brand_id 보완 입력 API",
                "priority": "Medium",
                "duedate":  "2026-03-28",
                "description": adf(
                    para("CMS에 미등록된 landing_url의 소재에 대해 "
                         "사용자가 brand_id를 직접 보완 입력할 수 있는 API."),
                    heading(3, "발생 케이스"),
                    bullet_list([
                        "landing_url이 CMS에 등록되지 않아 메타 자동 수집 불가",
                        "brand_id를 엑셀 미입력 + CMS 미등록 이중 미확인",
                    ]),
                    heading(3, "처리 흐름"),
                    bullet_list([
                        "업로드 응답에서 CMS 미등록 행 목록 확인",
                        "PATCH /api/campaign-assets/{id}/brand — brand_id 보완 입력",
                        "보완 완료 후 Campaign Asset 활성화",
                    ]),
                ),
            },
        ],
    },

    # ── 7. ML 모델링 연동 ────────────────────────────────────────────────────
    {
        "summary":  "[BE][CME] ML 모델링 연동",
        "priority": "Medium",
        "duedate":  "2026-03-31",
        "description": adf(
            para("S3/Databricks 기반 ML 코호트 유저 파일과 MATCH 시스템을 연동한다. "
                 "기존 데이터 포맷을 최대한 활용하여 Global Optimization 파이프라인의 "
                 "ML_OPTIMIZED 코호트 생성을 지원한다."),
            heading(3, "배경 (HLD 참조)"),
            para("HLD §4.3: S3/Databricks ← 로드, ML 코호트 유저 파일, automation_rule 경로. "
                 "HLD §4.5 Global Optimization ②글로벌 레이어: 현재 규칙 기반 → 향후 marginal utility 기반 ML."),
            heading(3, "Phase 1 범위"),
            para("기존 데이터 포맷(cohort/cohort_users 테이블 구조) 유지하며 ML 결과 연동. "
                 "ML 알고리즘 자체 개발은 Out-of-Scope (HLD §3.2)."),
        ),
        "tasks": [
            {
                "summary":  "기존 데이터 포맷 활용 ML 연동",
                "priority": "Medium",
                "duedate":  "2026-03-31",
                "description": adf(
                    para("ML 모델링 결과를 기존 cohort/cohort_users 테이블 포맷에 맞춰 "
                         "MATCH Audience Evaluation 파이프라인에 연동한다."),
                    heading(3, "연동 방식"),
                    bullet_list([
                        "S3/Databricks에서 생성된 ML 코호트 유저 파일 → automation_rule 경로 활용",
                        "ML_OPTIMIZED cohort_type으로 cohort 레코드 생성",
                        "cohort_users 테이블에 ML 선정 유저 INSERT (기존 ~18.5억 건 구조 유지)",
                        "Kafka Consumer(CDC 파이프라인)와 연계하여 ML 결과 실시간 반영",
                    ]),
                    heading(3, "HLD 참조"),
                    para("HLD §4.7: Audience Evaluation → PG cohort(기존 828건) + CH cohort_users(기존 ~18.5억). "
                         "변경 없음 — 기존 구조 활용."),
                ),
            },
        ],
    },
]


# ─── 메인 실행 ───────────────────────────────────────────────────────────────

def main():
    created = []

    for epic_data in EPICS:
        print(f"\n▶ Epic 생성: {epic_data['summary']}")

        epic_fields = build_fields(
            summary         = epic_data["summary"],
            issue_type_id   = EPIC_TYPE_ID,
            parent_key      = PARENT_INITIATIVE,
            priority        = epic_data["priority"],
            duedate         = epic_data["duedate"],
            description_adf = epic_data["description"],
        )
        epic_key = create_issue(epic_fields)

        if not epic_key:
            print(f"  [SKIP] Epic 생성 실패 — 하위 Task 건너뜀")
            continue

        print(f"  [OK] Epic: {epic_key}  ({epic_data['priority']}, due: {epic_data['duedate']})")
        created.append({"type": "Epic", "key": epic_key, "summary": epic_data["summary"]})
        time.sleep(0.5)

        for task_data in epic_data.get("tasks", []):
            print(f"   └ Task 생성: {task_data['summary']}")

            task_fields = build_fields(
                summary         = task_data["summary"],
                issue_type_id   = TASK_TYPE_ID,
                parent_key      = epic_key,
                priority        = task_data["priority"],
                duedate         = task_data["duedate"],
                description_adf = task_data["description"],
            )
            task_key = create_issue(task_fields)

            if task_key:
                print(f"     [OK] Task: {task_key}  ({task_data['priority']}, due: {task_data['duedate']})")
                created.append({"type": "Task", "key": task_key, "summary": task_data["summary"],
                                "parent": epic_key})
            time.sleep(0.3)

    # 결과 저장
    output_path = "output/created_cme_tickets.json"
    os.makedirs("output", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"total": len(created), "tickets": created}, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"완료: 총 {len(created)}개 티켓 생성")
    print(f"결과 저장: {output_path}")
    print(f"{'='*60}")
    for t in created:
        prefix = "  └ Task" if t["type"] == "Task" else "Epic  "
        print(f"  {prefix}  {t['key']}  {t['summary']}")


if __name__ == "__main__":
    main()
