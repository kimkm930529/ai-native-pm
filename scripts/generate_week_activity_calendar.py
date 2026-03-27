#!/usr/bin/env python3
"""
이번 주 Confluence + Jira 활동 기반 캘린더 CSV + ICS 생성
3/17(월) ~ 3/22(토) 작업 세션을 30분 단위 타임블럭으로 변환
"""
import csv, uuid, math
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))
BASE = Path(__file__).parent.parent

# ── 이번 주 작업 세션 ──────────────────────────────────────────────────────────
# (date, start_hhmm, end_hhmm, subject, description)
# 30분 단위, 근접한 활동들은 하나의 블럭으로 묶음
SESSIONS = [
    # ── 3/17 (월) ─────────────────────────────────────────────────────────────
    # Confluence/Jira 기록 없음 → 캘린더 일정 기반(회의 위주) 표시
    ("2026-03-17", "10:00", "10:30", "P13N Weekly & Planning",
     "P13N 주간 회의 및 플래닝"),
    ("2026-03-17", "11:00", "12:00", "CBP Weekly + MATCH 정기미팅",
     "CBP 주간 회의 | MATCH 정기미팅 (테크/마케팅)"),
    ("2026-03-17", "14:00", "15:00", "MATCH 속성 샘플값·어드민 API 논의",
     "MATCH 속성 샘플값 제공 논의 | MATCH 어드민 API 가이드 | 개인화 푸시 과제 퀵논의"),

    # ── 3/18 (화) ─────────────────────────────────────────────────────────────
    ("2026-03-18", "08:00", "08:30", "[업무기록] PSN-961 인프라 EKS 네트워크 요청 처리",
     "PSN-961 [인프라] 데이터 플랫폼팀 musinsa-data→ocmp EKS 네트워크 요청 업데이트"),
    ("2026-03-18", "11:00", "12:00", "캠페인 메타엔진 LLD Phase1 미팅 1·2",
     "CME LLD Phase1 개발 미팅 1차, 2차 연속 진행"),
    ("2026-03-18", "14:00", "14:30", "[업무기록] 1on1 Mike님 노트 + Customer Growth 페이지",
     "1on1 미팅 노트 작성 (Confluence) | Customer Growth 페이지 업데이트"),
    ("2026-03-18", "17:00", "17:30", "[정기 1:1] 2주 반복",
     "정기 1:1 미팅"),
    ("2026-03-18", "20:30", "21:30", "[업무기록] CME PRD 이미지·범위 업데이트",
     "CME PRD 다이어그램·스크린샷 5장 업로드 | 제외된 범위 섹션 작성 (Confluence)"),
    ("2026-03-18", "23:30", "00:00", "[업무기록] MEMB-380 완료 + PSN-1091 업데이트",
     "MEMB-380 완료: MATCH 기반 신규 오디언스 세그먼트 22종 생성 및 Braze API 연동 설정 | PSN-1091 개인화 푸시 최적화 Step2 업데이트"),

    # ── 3/19 (수) ─────────────────────────────────────────────────────────────
    ("2026-03-19", "09:00", "10:00", "P13N Project Weekly + P&E sync",
     "P13N 프로젝트 주간 회의 | P13N & MSS P&E sync | ETR-3219 검토완료: MATCH 앱테크/오프라인 데이터 연동"),
    ("2026-03-19", "11:00", "12:00", "Musinsa-Auxia Weekly Call",
     "Auxia PoC 주간 회의"),
    ("2026-03-19", "13:00", "14:00", "[업무기록] CME PRD 코멘트 + 무신사머니 데이터 정리",
     "CME PRD 코멘트 작성 | 무신사머니 데이터 논의 PM 이해용 정리 문서 작성 (Confluence)"),
    ("2026-03-19", "14:00", "14:30", "캠페인 메타엔진 변경된 개발범위 논의",
     "개발 범위 변경사항 확인 및 논의"),
    ("2026-03-19", "16:00", "17:00", "[업무기록] MATCH 비즈니스 심각도 초안 + HG님 리뷰 논의",
     "MATCH 비즈니스 심각도 정의 초안 작성 (Confluence) | HG님 리뷰 관련 논의"),
    ("2026-03-19", "20:30", "22:00", "[업무기록] Confluence 구조 정리 + PRD-Data 템플릿",
     "Confluence PRD/2-Pager 폴더 구조 재편 | PRD-Data 템플릿 작성 | CME PRD 추가 코멘트"),
    ("2026-03-19", "22:30", "23:30", "[업무기록] MEMB-384 + PSN-959 + DATAPLTFRQ 처리",
     "MEMB-384 생성: 29CM 데이터 MATCH PRD 작성 | PSN-959 CME CDC/인프라 업데이트 | DATAPLTFRQ-1183 Auxia 쿼리 변경 | CPPRD-6140 소재모델링 API 완료"),

    # ── 3/20 (목) ─────────────────────────────────────────────────────────────
    ("2026-03-20", "03:00", "03:30", "[업무기록] MEMB-394 + DATAPLTFRQ 완료 처리",
     "MEMB-394: Auxia DPA Exhibit C 법무 검토 요청 | DATAPLTFRQ-1121/1122 완료: 솔드아웃 GA4 및 통합회원 UID 적재"),
    ("2026-03-20", "09:00", "10:00", "[업무기록] MATCH 방향성 코멘트 + Audience API 에픽",
     "MATCH 방향성 논의 코멘트 2건 (Confluence) | MEMB-390 완료: PSN 티켓 일정/담당자 | PSN-881/882/883 Audience API 에픽 업데이트"),
    ("2026-03-20", "11:00", "12:30", "[업무기록] CRM 워크플로우 다이어그램 v4~v6 제작",
     "CRM 모듈 워크플로우 다이어그램 v4/v5/v6 PNG 렌더링 및 Confluence 업로드"),
    ("2026-03-20", "14:00", "14:30", "[업무기록] CME PRD 코멘트",
     "CME PRD Phase1 추가 코멘트 (Confluence)"),
    ("2026-03-20", "15:00", "15:30", "[업무기록] TM-2054 Initiative 업데이트",
     "TM-2054 통합식별자 연동 29CM 텍소노미 기반 구축 Initiative 업데이트"),
    ("2026-03-20", "15:30", "16:30", "무신사 미팅 내용 정리 + MATCH 방향성 확정",
     "[최종] MATCH 방향성 논의 문서 확정 (Confluence) | Meeting_agenda 정리"),
    ("2026-03-20", "16:00", "16:30", "[업무기록] Auxia Weekly Flash Report 발행",
     "Auxia x Musinsa Weekly Flash Report (26-03-20) Confluence 업로드"),
    ("2026-03-20", "17:30", "18:30", "[업무기록] PM Studio API 연동 + 권한 처리",
     "MEMB-396 Databricks API 연동 | MEMB-398 Figma API 연동 | OSD 권한 처리 (26891)"),
    ("2026-03-20", "19:30", "20:30", "[업무기록] PSN-963/965 CME 에픽 + OSD 권한 일괄 처리",
     "PSN-963 CME Mock API | PSN-965 CME Sync 관리 업데이트 | OSD 권한 신청 4건 처리"),
    ("2026-03-20", "23:30", "00:30", "[업무기록] MEMB 태스크 대량 등록 + 무신사머니 과제 발의",
     "MEMB Task 7건 SUGGESTED 등록 (무신사머니 API·데이터파이프라인·개인정보·29CM 자동화) | ETR-3319 무신사머니 S3 적재 과제 발의 | MEMB-387/395 처리"),

    # ── 3/21 (금) ─────────────────────────────────────────────────────────────
    ("2026-03-21", "07:00", "08:30", "[업무기록] MEMB-393/400/401 처리 + CRM 성과 데이터",
     "MEMB-393 완료: OCMP S3 페이먼츠 가입여부 확인 | MEMB-400 AI Assistant 2-Pager | MEMB-401 MATCH 방향성 문서 업데이트 | CRM 성과 RAW CSV 업로드"),
    ("2026-03-21", "10:00", "10:30", "[주간] Customer Growth Product",
     "Customer Growth 주간 회의"),
    ("2026-03-21", "14:00", "14:30", "MATCH SLI/SLO 논의",
     "MATCH SLI/SLO 정기 논의"),
    ("2026-03-21", "15:00", "15:30", "CME 엑셀시트 논의",
     "캠페인 메타엔진 엑셀시트 관련 논의"),
    ("2026-03-21", "17:00", "17:30", "[업무기록] 29CM 배포 엔진 분석 자료 준비",
     "29CM 앱푸시 배포 엔진 현황 분석 | 사이클 다이어그램·차트 첨부"),
    ("2026-03-21", "18:00", "18:30", "/strategy 스킬 신설 + CAPABILITY_MAP 업데이트",
     "PM Studio 전략 비서 에이전트 신설 | 역량맵 및 비서실장 라우팅 업데이트"),
    ("2026-03-21", "21:00", "22:00", "[업무기록] CME 2-Pager 업데이트",
     "[2-pager] Campaign Meta Engine 구축을 통한 목적 기반 타겟팅 지원 — 업데이트 (Confluence)"),
    ("2026-03-21", "22:30", "23:30", "[업무기록] MATCH 동기화 정책 PRD + PRD 논의 기록",
     "[PRD] MATCH 스프레드시트 동기화 정책 업데이트 (Confluence) | PRD 논의 내용 기록"),

    # ── 3/22 (토) ─────────────────────────────────────────────────────────────
    ("2026-03-22", "00:30", "02:00", "[업무기록] CME PRD + GTM Brief 최종 업데이트",
     "[PRD] Campaign Meta Engine Phase1 최종 업데이트 | [GTM Brief] CME Phase1 작성 | CRM 성과 CSV·이미지 업로드"),
    ("2026-03-22", "09:00", "10:00", "[업무기록] 29CM 캠페인 최적화 2-Pager 완성",
     "[2-Pager] 29CM 캠페인 최적화 인프라 구축 타겟팅 자동화 지원 — WIP 업로드 (Confluence)"),
    ("2026-03-22", "10:00", "11:30", "PM Studio 로깅 시스템 구축",
     "staff 세션 로그 시스템 설계 | CSV/ICS 캘린더 생성 스크립트 | Stop Hook 등록 | 이번 주 세션 역복원 백필"),
]


def floor_30(dt):
    return dt.replace(minute=0 if dt.minute < 30 else 30, second=0, microsecond=0)


def dt(date_s, time_s):
    return datetime.strptime(f"{date_s} {time_s}", "%Y-%m-%d %H:%M").replace(tzinfo=KST)


def escape_ics(s):
    return str(s).replace("\\","\\\\").replace(";","\\;").replace(",","\\,").replace("\n","\\n")


def fold(line):
    enc = line.encode("utf-8")
    parts = []
    while len(enc) > 75:
        cut = 75
        while cut > 0 and (enc[cut] & 0xC0) == 0x80:
            cut -= 1
        parts.append(enc[:cut].decode("utf-8"))
        enc = b" " + enc[cut:]
    parts.append(enc.decode("utf-8"))
    return "\r\n".join(parts)


def build_ics(rows):
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0",
        "PRODID:-//PM Studio//Weekly Activity//KO",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
        "X-WR-CALNAME:[업무] 이번 주 작업 기록 (3/17~3/22)",
        "X-WR-TIMEZONE:Asia/Seoul",
        "BEGIN:VTIMEZONE", "TZID:Asia/Seoul",
        "BEGIN:STANDARD", "DTSTART:19700101T000000",
        "TZOFFSETFROM:+0900", "TZOFFSETTO:+0900", "TZNAME:KST",
        "END:STANDARD", "END:VTIMEZONE",
    ]
    dtstamp = datetime.now(KST).strftime("%Y%m%dT%H%M%S")
    for r in rows:
        start = datetime.strptime(f"{r['Start Date']} {r['Start Time']}", "%m/%d/%Y %I:%M %p").replace(tzinfo=KST)
        end   = datetime.strptime(f"{r['End Date']} {r['End Time']}", "%m/%d/%Y %I:%M %p").replace(tzinfo=KST)
        subj  = r["Subject"]
        if not subj.startswith("[업무]"):
            subj = "[업무] " + subj
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uuid.uuid4()}@pm-studio",
            f"DTSTAMP:{dtstamp}",
            fold(f"DTSTART;TZID=Asia/Seoul:{start.strftime('%Y%m%dT%H%M%S')}"),
            fold(f"DTEND;TZID=Asia/Seoul:{end.strftime('%Y%m%dT%H%M%S')}"),
            fold(f"SUMMARY:{escape_ics(subj)}"),
            fold(f"DESCRIPTION:{escape_ics(r.get('Description',''))}"),
            "CLASS:PRIVATE", "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def main():
    rows = []
    for date_s, start_s, end_s, subject, desc in SESSIONS:
        # end가 "00:00"이면 다음날 00:00
        start_dt = dt(date_s, start_s)
        if end_s == "00:00":
            from datetime import date as ddate
            d = datetime.strptime(date_s, "%Y-%m-%d").date()
            next_d = d + timedelta(days=1)
            end_dt = datetime(next_d.year, next_d.month, next_d.day, 0, 0, tzinfo=KST)
        else:
            end_dt = dt(date_s, end_s)

        # 30분 단위 스냅
        start_block = floor_30(start_dt)
        duration_min = (end_dt - start_dt).total_seconds() / 60
        blocks = max(1, math.ceil(duration_min / 30))
        end_block = start_block + timedelta(minutes=30 * blocks)

        rows.append({
            "Subject": subject,
            "Start Date": start_block.strftime("%m/%d/%Y"),
            "Start Time": start_block.strftime("%I:%M %p"),
            "End Date":   end_block.strftime("%m/%d/%Y"),
            "End Time":   end_block.strftime("%I:%M %p"),
            "All Day Event": "False",
            "Description": desc,
            "Location": "",
            "Private": "True",
        })

    out_dir = BASE / "output" / "logs"
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "activity_week_0317_0322.csv"
    ics_path = out_dir / "activity_week_0317_0322.ics"

    fieldnames = ["Subject","Start Date","Start Time","End Date","End Time",
                  "All Day Event","Description","Location","Private"]
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"✅ CSV: {csv_path} ({len(rows)}개)")

    with open(ics_path, "w", encoding="utf-8") as f:
        f.write(build_ics(rows))
    print(f"✅ ICS: {ics_path} ({len(rows)}개, 모든 제목 [업무] 접두사)")

    # 날짜별 요약
    from collections import defaultdict
    by_day = defaultdict(list)
    for r in rows:
        day = r["Start Date"]
        by_day[day].append(f"  {r['Start Time']}~{r['End Time']} {r['Subject'][:45]}")
    for day in sorted(by_day):
        dt_obj = datetime.strptime(day, "%m/%d/%Y")
        wd = ["월","화","수","목","금","토","일"][dt_obj.weekday()]
        print(f"\n{day} ({wd}) — {len(by_day[day])}개")
        for line in by_day[day]:
            print(line)


if __name__ == "__main__":
    main()
