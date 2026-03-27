# -*- coding: utf-8 -*-
"""
MATCH Draft 문서 수정 스크립트 v2
mike_request.md 피드백 반영
"""
import re
from pathlib import Path

BASE = Path(__file__).parents[1]
INPUT = BASE / "output" / "draft_original.html"
OUTPUT = BASE / "output" / "draft.html"

content = INPUT.read_text(encoding="utf-8")

# ─── Executive Summary HTML ────────────────────────────────
EXEC_SUMMARY = """<h1>1. Executive Summary</h1><p>이 문서는 <strong>마케팅 자동화 및 업무 효율화 솔루션으로서 MATCH에 지속 투자해야 하는 이유</strong>와 운영 구조 옵션을 정리합니다.</p><p>Decision Layer 솔루션 선택의 문제가 아닌, <strong>MATCH를 통한 마케팅 자동화에 지속 투자할 것인가</strong>가 핵심 의사결정입니다.</p><table data-table-width="760" data-layout="center"><tbody><tr><th><p><strong>의사결정 항목</strong></p></th><th><p><strong>내용</strong></p></th></tr><tr><td><p><strong>핵심 메시지</strong></p></td><td><p>MATCH는 마케팅 자동화·업무 효율화 측면에서 지속 투자해야 하는 전략 자산. Auxia 등 AI SaaS는 MATCH를 대체하는 것이 아닌, 전술적 도구로 활용.</p></td></tr><tr><td><p><strong>운영 구조 옵션</strong></p></td><td><p>A. Braze 단독 / B. Braze + Auxia / C. Braze + MATCH (권장) / D. 현행 3중 병행 → 상세 비교: 6.2 참조</p></td></tr><tr><td><p><strong>권장 방향</strong></p></td><td><p><strong>C. Braze + MATCH 중심 운영.</strong> Auxia PoC 결과 기반 갱신 여부 별도 판단.</p></td></tr><tr><td><p><strong>Auxia PoC</strong></p></td><td><p>진행 중 (~2026.05.12). 갱신 결정 시점: <strong>2026.04.14</strong></p></td></tr></tbody></table><p><strong>결론 근거</strong></p><ul><li><p><strong>마케팅 자동화 성과</strong>: 캠페인 발송시간 5시간 → 30분 이내 단축, 세일즈푸시 CTR 0.6% → 1.0% 이상 개선 (2월 GMV 기준 4.1억원 증분 추정)</p></li><li><p><strong>데이터 주권 및 자산화</strong>: 무신사 고유 데이터(오프라인 POS, PLCC, 앱테크 등)를 내부 ML 모델과 결합할 수 있는 유일한 플랫폼. 외부 SaaS는 국내 리전 부재 및 오디언스 자산화 미제공.</p></li><li><p><strong>도메인 확장성</strong>: CRM 외 앱테크, 쿠폰/혜택, 배너, 상품 추천, Market Intelligence 등 전 서비스 개인화 로직을 일관되게 통제 가능.</p></li><li><p><strong>비용 효율</strong>: Auxia 미갱신 시 연 ~3.75억원 절감. 중장기적으로 Braze 의존도 감소 경로 확보.</p></li></ul>"""

# ─── 6.2 옵션별 종합 비교 HTML ────────────────────────────────
OPTIONS_TABLE = """<h2>6.2 옵션별 종합 비교</h2><table data-table-width="1200" data-layout="full-width"><tbody><tr><th><p><strong>구분</strong></p></th><th><p><strong>A — Braze 단독</strong></p></th><th><p><strong>B — Braze + Auxia</strong></p></th><th><p><strong>✅ C — Braze + MATCH</strong></p></th><th><p><strong>D — 현행 3중 병행</strong></p></th></tr><tr><td><p><strong>구성</strong></p></td><td><p>Braze 단독 운영</p></td><td><p>Auxia (Decision) + Braze (채널)</p></td><td><p>MATCH (Decision 주도) + Braze (채널/A/B)</p></td><td><p>Braze + MATCH + Auxia 3중 병행</p></td></tr><tr><td><p><strong>비용 절감 예상</strong></p></td><td><p>Auxia ~3.75억/yr 절감 + MATCH 운영비 절감. Braze $724K/yr (~10.9억) 유지</p></td><td><p>MATCH 운영비 절감. 단, Auxia $250K 추가로 전체 ~$974K/yr (~14.6억). 순비용 증가</p></td><td><p>Auxia 미갱신 시 ~3.75억/yr 절감. Braze 중장기 의존도 감소 경로 확보</p></td><td><p>절감 없음. Braze $724K + Auxia $250K + MATCH 운영비 = 비용 최대</p></td></tr><tr><td><p><strong>마케팅/운영 인력 절감 기대</strong></p></td><td><p>없음. Braze 기본 기능만으로 자동화 한계</p></td><td><p>AI 타겟팅 자동화로 일부 절감 가능. 단, CRM 외 도메인 지원 제한</p></td><td><p>MATCH 자동화 고도화로 캠페인 운영시간 단축 지속 기대 (현재 5h→30min). 향후 확대</p></td><td><p>3중 운영 복잡도로 오히려 인력 부담 증가</p></td></tr><tr><td><p><strong>장점</strong></p></td><td><p>운영 구조 단순화</p></td><td><p>AI 타겟팅 빠른 도입. 실시간 트리거 활용. Braze 채널 그대로 유지</p></td><td><p>데이터 주권 보유. 앱테크·쿠폰·추천 등 도메인 확장. 무신사 고유 데이터 내재화. Auxia 절감분 재투자 가능</p></td><td><p>단기 유연성 유지</p></td></tr><tr><td><p><strong>단점</strong></p></td><td><p>MATCH 기투자 낭비. Braze 종속. CRM 외 도메인 자동화 불가</p></td><td><p>데이터 주권 약화. 국내 리전 없어 무신사 고유 데이터 연동 불가. 외부 AI Lock-in 리스크. 오디언스 자산화 미제공</p></td><td><p>MATCH 고도화 속도 담보 필요</p></td><td><p>방향 없는 비용 증가. Decision Layer 3중 충돌. 데이터 파편화</p></td></tr><tr><td><p><strong>권장 여부</strong></p></td><td><p>❌</p></td><td><p>❌</p></td><td><p>✅ 권장</p></td><td><p>❌ (현재 상태)</p></td></tr></tbody></table>"""

# ─── Market Intelligence 도메인 행 ────────────────────────────
MI_ROW = """<tr><td><p>Market Intelligence (시장/트렌드 분석)</p></td><td><p>✅ (확장 예정)</p></td><td><p>❌</p></td><td data-highlight-colour="#fff0b3"><p>❌</p></td><td><p /></td></tr>"""

# ─── Step 1: Insert Executive Summary before section 1 ────────
SECTION1_HEADING = '<h1 local-id="3bc4f02bc3b3">1. 마케팅 팀의 업무 범위 및 관련 모듈 </h1>'
content = content.replace(SECTION1_HEADING, EXEC_SUMMARY + SECTION1_HEADING)
assert EXEC_SUMMARY in content, "Executive Summary 삽입 실패"
print("✅ Executive Summary 삽입 완료")

# ─── Step 2: Direct heading replacements (exact strings from original) ─────
# Map of exact old_heading → new_heading (text content only, between > and <)
heading_map = {
    # h1
    '1. 마케팅 팀의 업무 범위 및 관련 모듈 ': '2. 마케팅 팀의 업무 범위 및 관련 모듈 ',
    '2. MATCH &amp; Auxia 소개 ':             '3. MATCH &amp; Auxia 소개 ',
    '3. MATCH 업무 성과 및 계획 ':             '4. MATCH 업무 성과 및 계획 ',
    '4. Auxia PoC 목표 및 일정 ':              '5. Auxia PoC 목표 및 일정 ',
    '5. 결론':                                 '6. 결론',
    '6. Appendix':                             '7. Appendix',
    # h2 — plain text
    '1.1 마케팅팀 업무 범위 및 협업 포인트':   '2.1 마케팅팀 업무 범위 및 협업 포인트',
    '1.2 CRM 업무 와 업무 별 필요한 모듈':     '2.2 CRM 업무 와 업무 별 필요한 모듈',
    '2.1 MATCH, Auxia High-Level 소개':        '3.1 MATCH, Auxia High-Level 소개',
    '2.2 CRM 측면에서 MATCH, Auxia의 모듈 커버리지': '3.2 CRM 측면에서 MATCH, Auxia의 모듈 커버리지',
    '3.2 앞으로 진행 예정인 MATCH 업무 내용':  '4.2 앞으로 진행 예정인 MATCH 업무 내용',
    '5.1 결론적으로 말씀드리고 싶은 의견 ':    '6.1 결론적으로 말씀드리고 싶은 의견 ',
    '5.2 기타 의견 ':                          '6.3 기타 의견 ',
    '6.1 Auxia, MATCH 기능 및 가격 비교':      '7.1 Auxia, MATCH 기능 및 가격 비교',
    '6.2 각 모듈별 MATCH 진행 현황':           '7.2 각 모듈별 MATCH 진행 현황',
    # h2 — <strong> wrapped
    '<strong>3.1 </strong>현재까지 진행된 업무 내용 및 임팩트': '<strong>4.1 </strong>현재까지 진행된 업무 내용 및 임팩트',
    '<strong>4.1 PoC 목표</strong>':           '<strong>5.1 PoC 목표</strong>',
    '<strong>4.2 PoC 일정</strong>':           '<strong>5.2 PoC 일정</strong>',
    '<strong>4.3 PoC 실험대상 및 목표 </strong>': '<strong>5.3 PoC 실험대상 및 목표 </strong>',
    # h3
    '5.2.1 객관적 진단 및 전략적 방향':        '6.3.1 객관적 진단 및 전략적 방향',
    '5.2 최종 의견: &quot;SaaS는 전술적 도구, MATCH는 전략적 기반&quot;':
        '6.3 최종 의견: &quot;SaaS는 전술적 도구, MATCH는 전략적 기반&quot;',
}

for old, new in heading_map.items():
    if old in content:
        content = content.replace(old, new, 1)
        print(f"  ✅ '{old[:50]}' → '{new[:50]}'")
    else:
        print(f"  ⚠️ 못 찾음: '{old[:60]}'")

print("✅ 섹션 번호 재정렬 완료")

# ─── Step 3: Add Market Intelligence row to domain table ─────
PLP_TABLE_END = '</tr></tbody></table><ol start="1" local-id="dca2a66ef7d4">'
if PLP_TABLE_END in content:
    content = content.replace(
        PLP_TABLE_END,
        '</tr>' + MI_ROW + '</tbody></table><ol start="1" local-id="dca2a66ef7d4">',
        1
    )
    print("✅ Market Intelligence 도메인 행 추가 완료")
else:
    print("⚠️ PLP 테이블 끝 패턴 못 찾음")

# ─── Step 4: Insert 6.2 options table before 6.3 기타 의견 ────
# Find the <hr> tag right before 6.3 기타 의견 h2
match = re.search(r'<hr local-id="f0e62272eafc" />', content)
if match:
    insert_pos = match.start()
    content = content[:insert_pos] + OPTIONS_TABLE + content[insert_pos:]
    print("✅ 6.2 옵션별 종합 비교 삽입 완료")
else:
    # fallback: find 6.3 기타 의견 directly
    idx = content.find('>6.3 기타 의견')
    if idx != -1:
        hr_pos = content.rfind('<hr', 0, idx)
        content = content[:hr_pos] + OPTIONS_TABLE + content[hr_pos:]
        print("✅ 6.2 옵션별 종합 비교 삽입 완료 (대체)")
    else:
        print("⚠️ 삽입 위치 못 찾음")

# ─── Verify ──────────────────────────────────────────────────
print("\n=== 최종 헤딩 구조 ===")
for m in re.finditer(r'<h[12][^>]*>(.*?)</h[12]>', content, re.DOTALL):
    text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    tag = m.group()[:3]
    print(f"  {tag}> {text[:70]}")

OUTPUT.write_text(content, encoding="utf-8")
print(f"\n✅ 저장 완료: {OUTPUT} ({len(content)} bytes)")
