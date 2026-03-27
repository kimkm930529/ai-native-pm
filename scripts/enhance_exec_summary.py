# -*- coding: utf-8 -*-
"""
Executive Summary 및 6.2 옵션 비교 보강 스크립트
- Executive Summary: 표 제거, 줄글 문단 형식, C레벨 독립 가독 수준
- 6.2 옵션 비교: 더 상세하고 설득력 있게 보강
"""
import re
from pathlib import Path

BASE = Path(__file__).parents[1]
INPUT  = BASE / "output" / "draft.html"
OUTPUT = BASE / "output" / "draft.html"

content = INPUT.read_text(encoding="utf-8")

# ════════════════════════════════════════════════════════════
# NEW EXECUTIVE SUMMARY — 표 없이 문단 형식
# ════════════════════════════════════════════════════════════

NEW_EXEC_SUMMARY = """<h1>1. Executive Summary</h1><h3>왜 이 문서를 읽어야 하는가</h3><p>무신사는 현재 마케팅 자동화와 개인화 의사결정을 위해 Braze(외부 SaaS), MATCH(자체 플랫폼), Auxia(AI SaaS PoC) 세 개의 플랫폼을 동시에 운영하고 있습니다. 이 문서는 세 플랫폼 중 무엇을 선택해야 하는지를 다루는 것이 아닙니다. 핵심 질문은 더 단순합니다. <strong>무신사의 마케팅 자동화와 운영 효율화를 위해, 자체 플랫폼인 MATCH에 지속적으로 투자해야 하는가?</strong> 그 답은 '그렇다'이며, 이 문서는 그 근거와 구체적인 실행 방향을 담고 있습니다.</p><h3>MATCH가 이미 만들어 온 것들</h3><p>2025년 3분기 본격 가동된 MATCH는 짧은 시간 안에 측정 가능한 성과를 만들어 냈습니다. 세일즈 캠페인의 클릭률(CTR)은 일평균 0.6%에서 1.0% 이상으로 높아졌고, 2월 기준 거래액 증분은 약 4.1억원으로 추정됩니다. 그러나 숫자보다 더 중요한 변화는 운영 방식입니다. 마케팅 팀이 하나의 개인화 캠페인을 빌딩하는 데 걸리던 시간이 최대 5시간에서 30분 이내로 단축됐습니다. 이는 단순한 속도 개선이 아닙니다. 마케팅 인력이 반복 작업이 아닌 전략적 판단에 집중할 수 있는 구조가 갖춰지기 시작했다는 뜻입니다.</p><h3>MATCH가 앞으로 만들 수 있는 것들 — CRM을 훨씬 넘어서</h3><p>MATCH의 본질은 CRM 발송 도구가 아닙니다. MATCH는 무신사 전체 서비스에 걸쳐 고객 데이터 기반의 의사결정을 자동화하는 플랫폼이며, 지금은 CRM이라는 좁은 입구에서 그 가능성을 검증하고 있는 단계입니다.</p><p>현재 CRM(앱푸시)에서 검증된 성과를 발판으로, MATCH는 여러 도메인으로 확장 중입니다. <strong>앱테크</strong> 영역에서는 출석체크·무퀴즈 등 참여형 서비스의 보상 설계를 ML 모델이 개인화합니다. <strong>쿠폰·혜택</strong> 영역에서는 전사 할인 예산의 효율을 높이기 위해 개인 단위의 최적 발행 타이밍과 조건을 MATCH가 결정합니다. <strong>배너·상품 추천</strong> 영역에서는 앱 내 핵심 지면의 노출 의사결정에 실시간 타겟팅 엔진이 적용됩니다.</p><p>그리고 그 이상의 가능성이 있습니다. MATCH가 축적하는 유저 행동 데이터, 브랜드·카테고리별 선호 스코어, 구매 전환 패턴은 단순한 발송 최적화를 넘어 <strong>Market Intelligence</strong>로서 전략적 가치를 갖습니다. 어떤 카테고리에서 신규 수요가 생겨나고 있는지, 어느 브랜드에 대한 관심이 전환으로 이어지지 않고 있는지, 어떤 유저 집단이 특정 시즌에 활성화되는지 — 이런 인사이트는 MD 전략, 입점 브랜드 육성, 마케팅 예산 배분에 직접 활용될 수 있습니다. 외부 SaaS는 이 데이터를 무신사 안에서 활용할 수 있는 방법을 제공하지 않습니다. MATCH만이 이 자산을 완전하게 제어하고 서비스 전반에 접목할 수 있는 유일한 플랫폼입니다.</p><h3>데이터 주권 — 겉으로 드러나지 않는 핵심 리스크</h3><p>무신사는 오프라인 POS 데이터, PLCC 결제 이력, 케이뱅크 연동 앱테크 정보, 글로벌 플랫폼 크로스 구매 데이터 등 외부 어디에도 없는 독자적인 고객 자산을 보유하고 있습니다. 이 데이터를 외부 AI SaaS에 의존하는 순간, 데이터는 해외 서버로 나가고 무신사는 그 활용에 대한 통제권을 잃습니다. Auxia를 비롯한 대부분의 외부 SaaS는 국내 리전을 제공하지 않아 이 데이터의 연동 자체가 구조적으로 불가능합니다. MATCH는 이 모든 데이터를 내부에서 ML 모델과 결합하여 활용할 수 있는 유일한 경로입니다. 지금 MATCH에 투자하는 것은 단순히 도구를 만드는 것이 아니라, 무신사만이 가질 수 있는 경쟁력의 기반을 쌓는 일입니다.</p><h3>운영 구조 선택과 권장 방향</h3><p>현재 네 가지 운영 구조 옵션이 검토되고 있습니다. 각 옵션의 핵심만 말씀드리면 다음과 같습니다. Braze만 운영하는 Option A는 MATCH 기투자를 포기하고 외부 플랫폼에 종속되는 방향입니다. Auxia와 Braze를 조합하는 Option B는 연간 ~14.6억의 라이선스 비용과 데이터 주권 약화라는 대가를 치릅니다. 세 플랫폼을 모두 유지하는 Option D(현행)는 가장 많은 비용을 쓰면서 방향을 결정하지 않는 상태입니다. 옵션 상세 비교는 본문 6.2를 참조하십시오.</p><p><strong>권장 방향은 Option C — Braze + MATCH 중심 운영입니다.</strong> MATCH가 CRM 타겟팅과 최적화를 주도하고, Braze는 채널 발송 실행과 A/B 테스트를 담당하는 구조입니다. Auxia PoC는 2026년 5월 12일까지 진행되며, 결과를 기반으로 갱신 여부를 4월 14일에 결정합니다. Auxia를 갱신하지 않을 경우 연 ~3.75억원이 절감되고, 이 재원으로 MATCH 고도화 인력을 충원하면 실질적으로 비용 중립 구조에서 팀 역량을 강화할 수 있습니다.</p><h3>결론</h3><p>MATCH는 무신사가 AI 기반 마케팅 운영 체계를 자체적으로 내재화할 수 있는 유일한 경로입니다. 외부 SaaS는 전술적으로 활용할 수 있지만, 무신사 고객에 대한 이해와 그 이해를 기반으로 한 의사결정의 소유권은 MATCH를 통해서만 지킬 수 있습니다. CRM에서 시작된 이 플랫폼이 앱테크, 쿠폰, 추천, Market Intelligence로 확장되는 과정은 무신사가 데이터 기반 기업으로 진화하는 과정과 정확히 일치합니다. 지금의 투자가 2~3년 후 무신사의 마케팅 자동화 경쟁력의 수준을 결정하게 됩니다.</p>"""

# ════════════════════════════════════════════════════════════
# ENHANCED 6.2 옵션별 종합 비교 — 더 상세한 버전
# ════════════════════════════════════════════════════════════

NEW_OPTIONS = """<h2>6.2 옵션별 종합 비교</h2><table data-table-width="1200" data-layout="full-width"><tbody><tr><th><p><strong>구분</strong></p></th><th><p><strong>A — Braze 단독</strong></p></th><th><p><strong>B — Braze + Auxia</strong></p></th><th><p><strong>✅ C — Braze + MATCH</strong><br /><strong>(권장)</strong></p></th><th><p><strong>D — 현행 3중 병행</strong></p></th></tr><tr><td><p><strong>구성</strong></p></td><td><p>Braze만으로 전체 CRM 운영</p></td><td><p>Auxia(AI 타겟팅·발송 최적화) + Braze(채널 실행)</p></td><td><p>MATCH(타겟팅·최적화·자동화 주도) + Braze(채널 실행·A/B)</p></td><td><p>Braze + MATCH + Auxia 3중 병행, 역할 미분리</p></td></tr><tr><td><p><strong>Decision Layer 소유</strong></p></td><td><p>Braze에 전적 위임</p></td><td><p>Auxia에 위임 (외부 AI 종속)</p></td><td><p><strong>MATCH가 주도</strong> (내부 통제)</p></td><td><p>3중 충돌 — 소유자 불명확</p></td></tr><tr><td><p><strong>연간 라이선스 비용</strong></p></td><td><p>Braze ~$724K/yr<br />(약 10.9억)</p></td><td><p>Braze ~$724K + Auxia ~$250K<br />= <strong>~$974K/yr (약 14.6억)</strong></p></td><td><p>Braze ~$724K/yr<br />(약 10.9억)<br />+ MATCH 운영비</p></td><td><p>Braze ~$724K + Auxia ~$250K + MATCH 운영비<br />= <strong>비용 최대</strong></p></td></tr><tr><td><p><strong>비용 절감 기회</strong></p></td><td><p>Auxia ~3.75억/yr 절감<br />MATCH 운영비 절감<br />단, 기술 자산 포기</p></td><td><p>MATCH 운영비 절감 가능<br />단, Auxia 비용 추가로 순비용 증가</p></td><td><p><strong>Auxia 미갱신 시 ~3.75억/yr 절감</strong><br />절감분을 MATCH 인력에 재투자 → 비용 중립 구조</p></td><td><p>절감 없음.<br />현재 비용 구조 유지</p></td></tr><tr><td><p><strong>마케팅/운영 인력 절감 기대</strong></p></td><td><p>자동화 한계.<br />Braze 기본 기능 범위 내에서만 운영 가능</p></td><td><p>AI 타겟팅 일부 자동화.<br />단, 도메인 커버리지 제한 (CRM만)</p></td><td><p>현재: 캠페인 빌딩 5h → 30min 달성<br />향후: 자동화 범위 지속 확대<br />(AI 카피 생성, 소재 선정, 발송 빈도 자동화)</p></td><td><p>3중 운영 복잡도로 오히려 관리 부담 증가</p></td></tr><tr><td><p><strong>도메인 확장성</strong></p></td><td><p>CRM만 지원.<br />앱테크·쿠폰·추천·Market Intelligence 불가</p></td><td><p>CRM만 지원.<br />타 도메인 확장 불가</p></td><td><p><strong>CRM → 앱테크 → 쿠폰/혜택 → 배너/추천 → Market Intelligence로 단계적 확장 중</strong></p></td><td><p>MATCH 담당 도메인은 확장 가능하나 방향이 불명확</p></td></tr><tr><td><p><strong>데이터 주권</strong></p></td><td><p>Braze 종속.<br />무신사 고유 데이터(오프라인 POS, PLCC 등) 연동 제한</p></td><td><p><strong>데이터 주권 약화.</strong><br />Auxia 국내 리전 없어 무신사 고유 데이터 연동 구조적 불가.<br />외부 AI Lock-in 리스크</p></td><td><p><strong>완전한 데이터 내재화.</strong><br />오프라인 POS·PLCC·앱테크·케이뱅크 데이터를 내부 ML 모델과 직접 결합 가능</p></td><td><p>MATCH를 통한 내재화는 가능하나 Auxia와 충돌</p></td></tr><tr><td><p><strong>핵심 리스크</strong></p></td><td><p>MATCH 기투자 낭비.<br />Braze 갱신 시 협상력 소멸.<br />중장기 자동화 경쟁력 포기</p></td><td><p>데이터 주권 외부 이전.<br />Auxia 가격 인상·서비스 중단 시 대응 불가.<br />무신사 고유 데이터 활용 포기</p></td><td><p>MATCH 고도화 속도가 기대에 미치지 못할 경우<br />단기 성과 공백 가능성<br />(Auxia PoC 결과로 조기 검증 가능)</p></td><td><p>방향 없는 비용 증가.<br />책임 분산으로 성과 귀인 불명확.<br />데이터 파편화 심화</p></td></tr><tr><td><p><strong>권장 여부</strong></p></td><td><p>❌<br />전략 자산 포기</p></td><td><p>❌<br />고비용·데이터 주권 약화</p></td><td><p>✅ <strong>권장</strong><br />비용 효율 + 데이터 주권 + 도메인 확장</p></td><td><p>❌<br />현재 상태 유지 = 방향 없는 표류</p></td></tr></tbody></table>"""

# ════════════════════════════════════════════════════════════
# Replace Executive Summary section
# ════════════════════════════════════════════════════════════

# Find the old Executive Summary (from <h1>1. Executive Summary</h1> to the next <h1>)
old_exec_start = content.find('<h1>1. Executive Summary</h1>')
if old_exec_start == -1:
    print("⚠️ Executive Summary 시작 못 찾음")
else:
    # Find the next <h1 (start of section 2)
    next_h1 = content.find('<h1 ', old_exec_start + 10)
    if next_h1 == -1:
        print("⚠️ 다음 h1 못 찾음")
    else:
        old_exec = content[old_exec_start:next_h1]
        content = content[:old_exec_start] + NEW_EXEC_SUMMARY + content[next_h1:]
        print(f"✅ Executive Summary 교체 완료 (구: {len(old_exec)}자 → 신: {len(NEW_EXEC_SUMMARY)}자)")

# ════════════════════════════════════════════════════════════
# Replace 6.2 옵션별 종합 비교
# ════════════════════════════════════════════════════════════

old_opt_start = content.find('<h2>6.2 옵션별 종합 비교</h2>')
if old_opt_start == -1:
    print("⚠️ 6.2 옵션 비교 시작 못 찾음")
else:
    # Find the next h2 after this (6.3 기타 의견)
    next_h2 = content.find('<h2 ', old_opt_start + 10)
    if next_h2 == -1:
        print("⚠️ 다음 h2 못 찾음")
    else:
        old_opt = content[old_opt_start:next_h2]
        content = content[:old_opt_start] + NEW_OPTIONS + content[next_h2:]
        print(f"✅ 6.2 옵션 비교 교체 완료 (구: {len(old_opt)}자 → 신: {len(NEW_OPTIONS)}자)")

# ════════════════════════════════════════════════════════════
# Verify
# ════════════════════════════════════════════════════════════
print("\n=== 검증 ===")
# Check Executive Summary has key phrases
checks = [
    "왜 이 문서를 읽어야 하는가",
    "Market Intelligence",
    "데이터 주권",
    "권장 방향은 Option C",
    "6.2 옵션별 종합 비교",
    "Decision Layer 소유",
]
for phrase in checks:
    found = phrase in content
    print(f"  {'✅' if found else '❌'} '{phrase}'")

OUTPUT.write_text(content, encoding="utf-8")
print(f"\n✅ 저장: {OUTPUT} ({len(content):,} bytes)")
