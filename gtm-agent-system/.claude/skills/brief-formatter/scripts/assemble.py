#!/usr/bin/env python3
"""
brief-formatter/scripts/assemble.py
GTM 브리프 조립 스크립트 — messaging_draft.json + strategy_draft.json → GTM_Brief_*.md
--type internal : 8개 섹션 (Stakeholder Map 포함)
--type external : 9개 섹션 (Pricing, Promotion 포함)
"""

import argparse
import json
import os
import sys
from datetime import datetime


def load_json(path: str, label: str) -> dict:
    if not os.path.exists(path):
        print(f"[ERROR] {label} 파일을 찾을 수 없습니다: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] {label} JSON 파싱 실패: {e}", file=sys.stderr)
            sys.exit(1)


def load_template(path: str) -> str:
    if not os.path.exists(path):
        print(f"[ERROR] 템플릿 파일을 찾을 수 없습니다: {path}", file=sys.stderr)
        sys.exit(2)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def tbd(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, list) and len(value) == 0:
        return True
    return False


TBD_BLOCK = "> ⚠️ [TBD] 내용을 확인해주세요."
warnings = []


def get_or_tbd(value, label: str) -> str:
    if tbd(value):
        warnings.append(f"[TBD] '{label}' 항목이 비어있습니다.")
        return TBD_BLOCK
    return value


def personas_to_table(personas: list) -> str:
    if not personas:
        return TBD_BLOCK
    rows = ["| 페르소나 | 직무 | 현재 업무 장면 | 핵심 불편함 |",
            "|---------|------|--------------|-----------|"]
    for p in personas:
        rows.append(
            f"| {p.get('persona', '-')} | {p.get('role', '-')} "
            f"| {p.get('current_scene', '-')} | {p.get('key_pain', '-')} |"
        )
    return "\n".join(rows)


def journey_to_table(journey: list) -> str:
    if not journey:
        return TBD_BLOCK
    rows = ["| 단계 | 터치포인트 | 고객 행동 |",
            "|------|----------|---------|"]
    for j in journey:
        rows.append(
            f"| {j.get('stage', '-')} | {j.get('touchpoint', '-')} | {j.get('action', '-')} |"
        )
    return "\n".join(rows)


def supporting_to_list(supporting: list) -> str:
    if not supporting:
        return TBD_BLOCK
    return "\n".join(f"- {s}" for s in supporting)


def phase_in_to_list(items: list) -> str:
    if not items:
        return TBD_BLOCK
    return "\n".join(f"- {item}" for item in items)


def phase_out_to_list(items: list) -> str:
    if not items:
        return TBD_BLOCK
    lines = []
    for item in items:
        if isinstance(item, dict):
            feature = item.get("feature", "")
            timeline = item.get("timeline", "Phase 2 예정")
            lines.append(f"- {feature} ({timeline})")
        else:
            lines.append(f"- {item} (Phase 2 예정)")
    return "\n".join(lines)


def enablement_to_list(required: list, optional: list) -> str:
    lines = []
    for item in required:
        lines.append(f"- [ ] {item}")
    if optional:
        lines.append("")
        lines.append("*선택 항목:*")
        for item in optional:
            lines.append(f"- [ ] {item}")
    return "\n".join(lines) if lines else TBD_BLOCK


def metrics_to_table(metrics: list) -> str:
    if not metrics:
        return TBD_BLOCK
    # external은 dimension 컬럼 추가
    has_dimension = any(m.get("dimension") for m in metrics)
    if has_dimension:
        rows = ["| 차원 | 지표 | 측정 방법 | 목표 | 측정 시점 |",
                "|------|------|---------|------|---------|"]
        for m in metrics:
            rows.append(
                f"| {m.get('dimension', '-')} | {m.get('metric', '-')} "
                f"| {m.get('formula', '-')} | {m.get('target', '-')} "
                f"| {m.get('measurement_date', 'D+30')} |"
            )
    else:
        rows = ["| 유형 | 지표 | 측정 방법 | 목표 | 측정 시점 |",
                "|------|------|---------|------|---------|"]
        for m in metrics:
            rows.append(
                f"| {m.get('type', '-')} | {m.get('metric', '-')} "
                f"| {m.get('formula', '-')} | {m.get('target', '-')} "
                f"| {m.get('measurement_date', 'D+30')} |"
            )
    return "\n".join(rows)


def stakeholder_map_to_block(stakeholder: dict) -> str:
    if not stakeholder or not stakeholder.get("table_md"):
        return TBD_BLOCK
    return stakeholder["table_md"]


def pricing_distribution_to_block(pricing: dict) -> str:
    if not pricing:
        return TBD_BLOCK
    lines = []
    if pricing.get("model"):
        lines.append(f"**가격 모델**: {pricing['model']}")
    if pricing.get("tiers_md"):
        lines.append("")
        lines.append(pricing["tiers_md"])
    channels = pricing.get("channels", [])
    if channels:
        lines.append("")
        lines.append("**배포 채널**")
        for ch in channels:
            lines.append(f"- {ch}")
    return "\n".join(lines) if lines else TBD_BLOCK


def promotion_plan_to_block(promo: dict) -> str:
    if not promo:
        return TBD_BLOCK
    lines = []
    sections = [
        ("pre_launch", "Pre-launch (출시 전)"),
        ("launch_day", "Launch Day (출시 당일)"),
        ("post_launch", "Post-launch (출시 후)"),
    ]
    for key, title in sections:
        items = promo.get(key, [])
        lines.append(f"**{title}**")
        if items:
            for item in items:
                lines.append(f"- {item}")
        else:
            lines.append(f"- {TBD_BLOCK}")
        lines.append("")
    return "\n".join(lines).rstrip()


def assemble(messaging: dict, strategy: dict, template: str, gtm_type: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")

    replacements = {
        "{{ONE_LINER}}": get_or_tbd(messaging.get("one_liner"), "one_liner"),
        "{{PERSONAS_TABLE}}": personas_to_table(messaging.get("personas", [])),
        "{{CUSTOMER_JOURNEY}}": journey_to_table(messaging.get("customer_journey", [])),
        "{{BEFORE_AFTER_TABLE}}": get_or_tbd(
            strategy.get("before_after", {}).get("table_md"), "before_after.table_md"
        ),
        "{{PRIMARY_MESSAGE}}": get_or_tbd(
            messaging.get("key_message", {}).get("primary"), "key_message.primary"
        ),
        "{{SUPPORTING_MESSAGES}}": supporting_to_list(
            messaging.get("key_message", {}).get("supporting", [])
        ),
        "{{PHASE1_LIMITATION}}": get_or_tbd(
            messaging.get("key_message", {}).get("phase1_limitation"), "phase1_limitation"
        ),
        "{{COMPETITIVE_POSITIONING}}": get_or_tbd(
            messaging.get("key_message", {}).get("competitive_positioning"),
            "competitive_positioning"
        ) if gtm_type == "external" else "",
        "{{PHASE1_IN}}": phase_in_to_list(
            strategy.get("scope", {}).get("phase1_in", [])
        ),
        "{{PHASE2_OUT}}": phase_out_to_list(
            strategy.get("scope", {}).get("phase2_out", [])
        ),
        "{{STAKEHOLDER_MAP}}": stakeholder_map_to_block(
            strategy.get("stakeholder_map")
        ) if gtm_type == "internal" else "",
        "{{PRICING_DISTRIBUTION}}": pricing_distribution_to_block(
            strategy.get("pricing_distribution")
        ) if gtm_type == "external" else "",
        "{{PROMOTION_PLAN}}": promotion_plan_to_block(
            strategy.get("promotion_plan")
        ) if gtm_type == "external" else "",
        "{{ROLLOUT_TABLE}}": get_or_tbd(
            strategy.get("rollout_plan", {}).get("table_md"), "rollout_plan.table_md"
        ),
        "{{ENABLEMENT_LIST}}": enablement_to_list(
            strategy.get("enablement", {}).get("required", []),
            strategy.get("enablement", {}).get("optional", []),
        ) if gtm_type == "internal" else "",
        "{{LAUNCH_METRICS_TABLE}}": metrics_to_table(
            strategy.get("launch_metrics", [])
        ),
        "{{GENERATED_DATE}}": today,
        "{{PRODUCT_TOPIC}}": strategy.get("product_topic", "주제 미입력"),
    }

    result = template
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)

    return result


INTERNAL_SECTIONS = [
    "## 1. One-liner",
    "## 2. Target User",
    "## 3. Before/After",
    "## 4. Key Message",
    "## 5. What's in/out",
    "## 6. Stakeholder Map",
    "## 7. Rollout & Enablement",
    "## 8. Launch Metrics",
]

EXTERNAL_SECTIONS = [
    "## 1. One-liner",
    "## 2. Target User & Journey",
    "## 3. Before/After",
    "## 4. Key Message & Competitive Positioning",
    "## 5. What's in/out",
    "## 6. Pricing & Distribution",
    "## 7. Promotion Plan",
    "## 8. Rollout Plan",
    "## 9. Launch Metrics",
]


def validate(content: str, messaging: dict, strategy: dict, gtm_type: str) -> list:
    issues = []
    required_sections = INTERNAL_SECTIONS if gtm_type == "internal" else EXTERNAL_SECTIONS
    for section in required_sections:
        if section not in content:
            issues.append(f"섹션 누락: {section}")

    one_liner = messaging.get("one_liner", "")
    char_count = len(one_liner)
    if char_count > 50:
        issues.append(f"One-liner 50자 초과: 현재 {char_count}자")

    if gtm_type == "external":
        if not messaging.get("key_message", {}).get("competitive_positioning"):
            issues.append("Competitive Positioning 누락 (external 필수)")
        promo = strategy.get("promotion_plan", {})
        for key in ["pre_launch", "launch_day", "post_launch"]:
            if not promo.get(key):
                issues.append(f"Promotion Plan '{key}' 누락")

    if gtm_type == "internal":
        if not strategy.get("stakeholder_map", {}).get("table_md"):
            issues.append("Stakeholder Map 누락 (internal 필수)")

    return issues


def main():
    parser = argparse.ArgumentParser(description="GTM 브리프 조립 스크립트")
    parser.add_argument("--messaging", required=True)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--template", required=True)
    parser.add_argument("--type", dest="gtm_type", choices=["internal", "external"], required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    messaging = load_json(args.messaging, "messaging_draft.json")
    strategy = load_json(args.strategy, "strategy_draft.json")
    template = load_template(args.template)

    content = assemble(messaging, strategy, template, args.gtm_type)

    issues = validate(content, messaging, strategy, args.gtm_type)
    if issues:
        for issue in issues:
            print(f"[WARN] {issue}", file=sys.stderr)

    if warnings:
        for w in warnings:
            print(f"[WARN] {w}")

    if args.dry_run:
        print(content)
        return

    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)

    section_count = sum(1 for s in (INTERNAL_SECTIONS if args.gtm_type == "internal" else EXTERNAL_SECTIONS)
                        if s in content)
    total = len(INTERNAL_SECTIONS) if args.gtm_type == "internal" else len(EXTERNAL_SECTIONS)
    one_liner = messaging.get("one_liner", "")
    metrics_count = len(strategy.get("launch_metrics", []))

    print(f"[ASSEMBLE] GTM 브리프 생성 완료 [{args.gtm_type.upper()}]")
    print(f"파일: {args.output}")
    print(f"섹션: {section_count}/{total} 완성")
    print(f"One-liner 길이: {len(one_liner)}자 {'✅' if len(one_liner) <= 50 else '❌ (50자 초과)'}")
    print(f"Launch Metrics: {metrics_count}개 ✅")

    if issues:
        print(f"\n[검증 실패 항목]")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)


if __name__ == "__main__":
    main()
