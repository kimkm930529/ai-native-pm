#!/usr/bin/env python3
"""
batch_interview.py — 가상 인터뷰 배치 실행 보조 스크립트

역할: 여러 페르소나 JSON을 읽어 인터뷰 템플릿을 초기화하고
     user-simulator 에이전트가 채워야 할 녹취록 파일을 생성한다.

실제 인터뷰 내용(응답 생성)은 user-simulator 에이전트(LLM)가 수행한다.
이 스크립트는 파일 구조 초기화 및 메타데이터 관리에 집중한다.
"""

import argparse
import json
import os
from datetime import date
from pathlib import Path


TEMPLATE = """\
# 가상 인터뷰: {name} ({persona_id})
> 인터뷰 일시: {date} | 탐색 주제: {topic} | 인터뷰어: Lead Researcher (AI)

## 페르소나 프로파일 요약
- 이름: {name} / {age}세 / {occupation}
- 거주: {location}
- 핵심 특징: {frustrations_summary}

> ⚠️  이 파일은 user-simulator 에이전트가 채워야 합니다.
>    아래 섹션을 인터뷰 녹취록으로 완성해주세요.

---

## 인터뷰 녹취록

### [Warm-up]

**Q:** (user-simulator가 작성)

**A:** (user-simulator가 작성)

---

### [Problem Probe]

**Q:** 마지막으로 관련 문제를 겪었을 때 어떤 상황이었는지 자세히 들려주실 수 있어요?

**A:** (user-simulator가 작성)

---

### [Hypothesis Test]

**Q:** (PM 가설 기반 질문 — hypotheses 파라미터 참조)
> 검증할 가설: {hypotheses}

**A:** (user-simulator가 작성)

---

### [Solution Probe]

**Q:** 지금 방식에서 딱 하나만 바꿀 수 있다면 무엇을 바꾸시겠어요?

**A:** (user-simulator가 작성)

---

## 인터뷰 메타데이터

| 항목 | 내용 |
|------|------|
| 검증된 Pain Points | (user-simulator가 작성) |
| 기각 신호 | (user-simulator가 작성) |
| 새로운 발견 | (user-simulator가 작성) |
| 후속 탐색 추천 | (user-simulator가 작성) |
"""


def load_persona(persona_path: Path) -> dict:
    with open(persona_path, encoding="utf-8") as f:
        return json.load(f)


def build_frustrations_summary(persona: dict) -> str:
    frustrations = persona.get("frustrations", [])
    if not frustrations:
        return "정보 없음"
    return frustrations[0][:60] + "..." if len(frustrations[0]) > 60 else frustrations[0]


def init_interview_file(persona: dict, output_path: Path, topic: str, hypotheses: str) -> None:
    content = TEMPLATE.format(
        persona_id=persona["id"],
        name=persona["name"],
        age=persona["age"],
        occupation=persona.get("occupation", "미상"),
        location=persona.get("location", "미상"),
        frustrations_summary=build_frustrations_summary(persona),
        date=date.today().strftime("%Y%m%d"),
        topic=topic,
        hypotheses=hypotheses or "자유 탐색 인터뷰 (가설 없음)",
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ 초기화 완료: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="가상 인터뷰 배치 파일 초기화")
    parser.add_argument("--personas", required=True, help="페르소나 폴더 또는 단일 JSON 경로")
    parser.add_argument("--hypotheses", default="", help="검증할 가설 (| 구분)")
    parser.add_argument("--topic", default="탐색 주제 미입력", help="탐색 주제")
    parser.add_argument("--output", required=True, help="인터뷰 파일 저장 폴더")
    args = parser.parse_args()

    personas_path = Path(args.personas)
    output_dir = Path(args.output)

    # 단일 파일 또는 폴더 처리
    if personas_path.is_file():
        persona_files = [personas_path]
    elif personas_path.is_dir():
        persona_files = sorted(personas_path.glob("*.json"))
        persona_files = [p for p in persona_files if not p.name.startswith("_")]
    else:
        print(f"❌ 경로를 찾을 수 없습니다: {personas_path}")
        return

    if not persona_files:
        print("❌ 페르소나 JSON 파일이 없습니다.")
        return

    print(f"\n🎙️  가상 인터뷰 파일 초기화 ({len(persona_files)}건)")
    print(f"   탐색 주제: {args.topic}")
    print(f"   검증 가설: {args.hypotheses or '없음 (자유 탐색)'}")
    print()

    for persona_file in persona_files:
        persona = load_persona(persona_file)
        persona_id = persona.get("id", persona_file.stem)
        output_path = output_dir / f"{persona_id}_interview.md"
        init_interview_file(persona, output_path, args.topic, args.hypotheses)

    print(f"\n✅ {len(persona_files)}건 초기화 완료.")
    print(f"   다음 단계: user-simulator 에이전트가 각 파일의 녹취록을 완성합니다.")


if __name__ == "__main__":
    main()
