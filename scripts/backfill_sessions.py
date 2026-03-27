#!/usr/bin/env python3
"""
이번 주 파일 타임스탬프 기반 세션 역복원 (백필)
3/17(월) ~ 3/22(토) 작업을 staff_sessions.jsonl에 삽입
"""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))
LOG_PATH = Path(__file__).parent.parent / "output" / "logs" / "staff_sessions.jsonl"

def ts(date_str, time_str):
    """2026-03-19 15:00 → ISO 8601 KST"""
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M").replace(tzinfo=KST)
    return dt.isoformat()

def sid(date_str, time_str):
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    return dt.strftime("%Y%m%d_%H%M%S")

def e(d, start, end, request, summary, skills, outputs, status="completed"):
    return {
        "id": sid(d, start),
        "start_ts": ts(d, start),
        "end_ts": ts(d, end),
        "request": request,
        "summary": summary,
        "skills": skills,
        "outputs": outputs,
        "status": status,
        "source": "backfill"
    }

BACKFILL = [
    # ── 3/17 (월) ────────────────────────────────────────────────
    e("2026-03-17", "18:20", "18:35",
      "Match CRM Journey 다이어그램 작성 + Confluence Tool 업데이트",
      "Match CRM Journey 다이어그램 생성 + Confluence fetch_comments 스크립트 추가",
      ["/prd"],
      ["output/match_crm_journey.html", "output/match_crm_journey.png"]),

    # ── 3/18 (화) ────────────────────────────────────────────────
    e("2026-03-18", "13:24", "13:40",
      "Confluence 문서 업로드",
      "Confluence 페이지 업로드 완료",
      ["confluence-writer"],
      ["output/upload_result.json"]),

    e("2026-03-18", "21:30", "21:50",
      "시트 싱크 시퀀스 다이어그램 작성",
      "Sheet Sync Sequence 다이어그램 생성",
      ["/prd"],
      ["prd-agent-system/output/diagrams/sheet_sync_sequence.mmd"]),

    # ── 3/19 (수) ────────────────────────────────────────────────
    e("2026-03-19", "09:26", "09:45",
      "Auxia 계약 관련 노트 정리",
      "Auxia 계약 주요 내용 메모 정리",
      [],
      ["input/refs/auxia_contract_notes.md"]),

    e("2026-03-19", "13:40", "14:15",
      "Task Ticket 생성 스킬 및 에이전트 설계",
      "/task-ticket 스킬 + task-ticket-creator 에이전트 신설 + 29CM 결제 태스크 스크립트",
      ["/task-ticket"],
      [".claude/skills/task-ticket/SKILL.md",
       ".claude/agents/task-ticket-creator/AGENT.md",
       "scripts/archive/create_memb_task_20260319_29cm_payments.py"]),

    e("2026-03-19", "15:00", "16:00",
      "무신사머니 API Task 티켓 생성 (계정/트래픽/파이프라인/개인정보)",
      "무신사머니 API 관련 MEMB Task 4개 티켓 생성 스크립트 작성 + 요약 문서",
      ["/task-ticket"],
      ["output/musinsa_money_api_summary_20260319.md",
       "scripts/archive/create_memb_task_20260319_money_api_account.py",
       "scripts/archive/create_memb_task_20260319_money_api_traffic.py",
       "scripts/archive/create_memb_task_20260319_money_pipeline.py",
       "scripts/archive/create_memb_task_20260319_money_privacy.py"]),

    e("2026-03-19", "15:53", "16:10",
      "Match 비즈니스 심각도 기준 초안 작성",
      "Match SLO 비즈니스 심각도 분류 기준 초안 작성",
      ["/prd"],
      ["output/match_business_severity_draft.md"]),

    e("2026-03-19", "15:56", "16:30",
      "Mike 피드백 정리 + 프로모션 추천서 메모",
      "Mike 미팅 피드백 정리 및 상반기 프로모션 동료 추천서 초안",
      [],
      ["input/notes/Mike Feedback.md",
       "input/no_commit/'26년 상반기 프로모션 - 동료 추천서.md"]),

    e("2026-03-19", "18:07", "18:35",
      "3/19 회의 준비 및 회의록 정리 (무사 미팅 + Slack 아젠다)",
      "무신사 미팅 아젠다 + Slack 아젠다 정리, 하루 작업 메모",
      ["/meeting"],
      ["input/notes/2026.03.19.md"]),

    e("2026-03-19", "18:34", "19:00",
      "MATCH 방향성 수정 초안 + CRM 워크플로우 다이어그램",
      "MATCH 서비스 방향성 수정 초안 작성 + CRM 워크플로우 HTML 다이어그램",
      ["/prd"],
      ["input/notes/MATCH_방향성_수정초안_20260319.md",
       "input/notes/MATCH_CRM_workflow.html"]),

    e("2026-03-19", "19:51", "20:25",
      "UX 로직 분석 에이전트 생성 + CRM 시트 읽기 스크립트",
      "ux-logic-analyst 에이전트 설계 + read_crm_sheet.py 작성",
      [],
      ["prd-agent-system/.claude/agents/ux-logic-analyst/AGENT.md",
       "scripts/read_crm_sheet.py"]),

    e("2026-03-19", "21:04", "21:10",
      "무신사머니 관련 대화 내용 기록",
      "무신사머니 관련 논의 내용 노트 저장",
      [],
      ["input/notes/무신사머니 관련 대화.md"]),

    e("2026-03-19", "21:06", "22:00",
      "PGM 에이전트 + Ticket Review + Meeting 스킬 + CONVENTIONS 설계",
      "pgm-agent-system 리팩토링 + ticket-reviewer 에이전트 + meeting 스킬 + CONVENTIONS.md 신설",
      ["/pgm", "/meeting", "/ticket-review"],
      ["pgm-agent-system/CLAUDE.md",
       "pgm-agent-system/.claude/agents/ticket-reviewer/AGENT.md",
       ".claude/skills/meeting/SKILL.md",
       "CONVENTIONS.md"]),

    e("2026-03-19", "21:27", "22:00",
      "26Q2 이니셔티브 7개 구조 설계 및 index 업데이트",
      "2026Q2 이니셔티브 폴더 구조 + meta/context/decisions/references 일괄 생성",
      [],
      ["input/initiatives/index.md",
       "input/initiatives/2026Q2/"]),

    e("2026-03-19", "21:34", "22:00",
      "무신사머니 데이터수집 PRD DOCX → MD 변환",
      "무신사머니 데이터수집 PRD 문서 변환 및 정리",
      ["/prd"],
      ["input/data/무신사머니_데이터수집_PRD.md"]),

    e("2026-03-19", "23:11", "23:57",
      "QA 에이전트 생성 + Campaign Meta Engine QA 테스트케이스 작성",
      "qa-agent 에이전트 설계 + Campaign Meta Engine QA 테스트케이스 + PM 킥오프 브리핑 생성",
      ["/prd"],
      ["prd-agent-system/.claude/agents/qa-agent/AGENT.md",
       "prd-agent-system/output/qa_testcase_20260319_campaign_meta_engine.md",
       "prd-agent-system/output/qa_briefing_20260319_campaign_meta_engine.md",
       "prd-agent-system/.claude/agents/data-prd-writer/AGENT.md"]),

    # ── 3/20 (목) ────────────────────────────────────────────────
    e("2026-03-20", "00:01", "00:50",
      "Diagram Generator 업데이트 + Campaign Meta Engine PRD v3 + QA 재생성",
      "diagram-generator 스킬 업데이트 + export_png 추가 + CME PRD v3 생성 + QA 문서",
      ["/prd"],
      ["prd-agent-system/.claude/skills/diagram-generator/SKILL.md",
       "prd-agent-system/.claude/skills/diagram-generator/scripts/export_png.py",
       "prd-agent-system/output/prd_20260319_campaign_meta_engine_v3.md",
       "prd-agent-system/output/qa_testcase_20260320_campaign_meta_engine.md",
       "prd-agent-system/output/qa_briefing_20260320_campaign_meta_engine.md"]),

    e("2026-03-20", "08:43", "09:00",
      "Databricks / Figma / Slack 에이전트 시스템 일괄 생성",
      "3개 에이전트 시스템 (Databricks, Figma, Slack) 스킬+에이전트+스크립트 생성",
      ["/databricks", "/figma", "/slack"],
      ["databricks-agent-system/", "figma-agent-system/", "slack-agent-system/"]),

    e("2026-03-20", "08:51", "09:00",
      "WORKFLOW_PATTERNS.md 작성 + GitHub Pages index.html + MEMB Task 스크립트",
      "복합 워크플로우 패턴 문서 작성 + pm-studio GitHub Pages 업데이트",
      [],
      ["WORKFLOW_PATTERNS.md", "index.html",
       "scripts/create_memb_mcp_tasks_20260320.py"]),

    e("2026-03-20", "10:50", "12:15",
      "CRM 모듈 워크플로우 다이어그램 v2~v6 반복 개선 + PNG 렌더링",
      "CRM 모듈 워크플로우 다이어그램 6개 버전 반복 작업 (mmd → html → png)",
      ["/prd"],
      ["prd-agent-system/output/diagrams/crm_module_workflow_v2.html",
       "prd-agent-system/output/diagrams/crm_module_workflow_v4.png",
       "prd-agent-system/output/diagrams/crm_module_workflow_v6.png"]),

    e("2026-03-20", "15:51", "16:00",
      "무신사 미팅 내용 정리 + Auxia PoC Weekly Flash 생성",
      "3/19 미팅 아젠다 정리 + Auxia PoC Weekly Flash Report 생성",
      ["/pgm"],
      ["pgm-agent-system/output/flash_20260320_Auxia_PoC_weekly.md",
       "input/meetings/Meeting_agenda_with_Musinsa_Mar19.md"]),

    e("2026-03-20", "16:25", "16:40",
      "Match SLO 참조 삽입 문서 작성",
      "Match SLO 기준 참조를 정책 문서에 삽입 정리",
      ["/prd"],
      ["output/match_slo_reference_insert_20260320.md"]),

    e("2026-03-20", "21:51", "22:40",
      "Match/29CM Campaign Meta Engine 방향성 개선 + 2-Pager 완성 + Red Team",
      "Match 방향성 개선안 + CME PRD 개선안 작성 → 29CM 2-Pager + Red Team 검증",
      ["/prd", "/red"],
      ["output/match_direction_improvement_plan_20260320.md",
       "output/campaign_meta_engine_prd_improvement_20260320.md",
       "output/29cm_2pager_review_20260320.md",
       "prd-agent-system/output/redteam_20260320_29CM_campaign_meta_engine.md",
       "output/2pager_29CM_campaign_optimization_v2_20260320.md"]),

    e("2026-03-20", "22:41", "23:10",
      "Detargeting / CTR 전략 다이어그램 작성 + AI Match Jira Task 생성",
      "Detargeting Flow + CTR 전략 플로우 다이어그램 + AI Match 관련 Jira Task 생성 스크립트",
      ["/prd", "/jira"],
      ["prd-agent-system/output/diagrams/detargeting_flow.html",
       "prd-agent-system/output/diagrams/ctr_strategy_flow.html",
       "scripts/create_memb_tasks_20260320_ai_match.py"]),

    # ── 3/21 (금) ────────────────────────────────────────────────
    e("2026-03-21", "17:22", "17:35",
      "29CM 배포 엔진 분석 문서 작성 + 참조 이미지 추가",
      "29CM 앱푸시 배포 엔진 현황 분석 + 사이클 다이어그램 및 푸시 차트 추가",
      ["/discovery"],
      ["input/refs/29CM_distribution_engine_analysis.md",
       "input/refs/29cm_cycle_diagram.png",
       "input/refs/29cm_app_push_chart.png"]),

    e("2026-03-21", "18:51", "19:00",
      "/strategy 스킬 신설 + CAPABILITY_MAP + CLAUDE.md 업데이트",
      "전략 비서 에이전트 신설 + 역량맵 및 비서실장 라우팅 테이블 업데이트",
      ["/strategy"],
      [".claude/skills/strategy/SKILL.md",
       "CAPABILITY_MAP.md", "CLAUDE.md"]),

    e("2026-03-21", "20:56", "21:00",
      "이동욱 관련 메모 작성",
      "이동욱 관련 참고 내용 노트 정리",
      [],
      ["이동욱.md"]),

    e("2026-03-21", "22:16", "22:50",
      "PRD 논의 내용 기록 + Match 동기화 정책 PRD 업데이트",
      "PRD 관련 팀 논의 내용 기록 + Match 동기화 정책 PRD 수정",
      ["/prd"],
      ["PRD 논의.md",
       "output/prd_match_sync_policy_updated.md"]),

    # ── 3/22 (토) ────────────────────────────────────────────────
    e("2026-03-22", "00:30", "02:10",
      "Campaign Meta Engine Phase 1 PRD + Red Team + 29CM 2-Pager + Red Team",
      "CME Phase 1 PRD 작성 → Red Team 검증 + Platform PM 인사이트 기록 + 29CM 2-Pager Red Team",
      ["/prd", "/red"],
      ["prd-agent-system/.claude/agents/red-team-validator/input/prd_20260322_campaign_meta_engine_phase1.md",
       "prd-agent-system/output/redteam_20260322_campaign_meta_engine_phase1.md",
       "input/notes/insight_20260322_platform_pm.md",
       "prd-agent-system/output/redteam_20260322_29cm_campaign_meta_engine.md"]),

    e("2026-03-22", "09:20", "09:40",
      "29CM Campaign Meta Engine 2-Pager v2 + 측정 기준 검토 + Confluence 업로드",
      "CME 2-Pager v2 완성 + 29CM 측정 기준 검토 문서 + Confluence 업로드",
      ["/prd", "confluence-writer"],
      ["prd-agent-system/output/2pager_29cm_campaign_meta_engine_v2.md",
       "prd-agent-system/output/measurement_standard_review_29cm.md"]),

    e("2026-03-22", "09:34", "10:00",
      "통합 프로필 Cross-Platform 2-Pager 작성",
      "Unified Profile Cross-Platform 전략 2-Pager 작성",
      ["/prd"],
      ["output/2pager_unified_profile_cross_platform.md"]),
]

def main():
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 기존 로그 로드 (중복 방지)
    existing_ids = set()
    existing_lines = []
    if LOG_PATH.exists():
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        existing_ids.add(entry["id"])
                        existing_lines.append(line)
                    except json.JSONDecodeError:
                        pass

    new_entries = [e for e in BACKFILL if e["id"] not in existing_ids]

    # 전체 정렬 후 재기록
    all_entries = []
    for line in existing_lines:
        all_entries.append(json.loads(line))
    all_entries.extend(new_entries)
    all_entries.sort(key=lambda x: x["start_ts"])

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        for entry in all_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"✅ 백필 완료: {len(new_entries)}개 추가 / 전체 {len(all_entries)}개")
    for e in new_entries:
        dt = datetime.fromisoformat(e["start_ts"])
        print(f"   {dt.strftime('%m/%d %H:%M')} | {e['summary'][:55]}")

if __name__ == "__main__":
    main()
