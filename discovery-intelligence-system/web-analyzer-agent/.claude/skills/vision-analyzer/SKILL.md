# vision-analyzer — 이미지 분석 및 명세 추출 스킬

## 역할

스크린샷 이미지를 Claude Vision으로 분석하여 화면 구성 요소와 기능 명세를 추출한다.
별도 스크립트 없이 LLM(Claude)이 직접 이미지를 읽고 분석한다.

---

## 분석 프롬프트 규약

오케스트레이터(CLAUDE.md)가 이 스킬을 호출할 때 아래 형식을 사용한다:

```
[Vision Analysis Request]

이미지: {screenshot_path}
서비스 URL: {url}
화면 경로: {breadcrumb} (예: 홈 > 상품 > 상세)
분석 목적: 화면 설계서 작성용 UI/UX 명세 추출

아래 항목을 분석하여 JSON으로 반환해줘:

{
  "screen_name": "화면 이름 (간결하게)",
  "screen_purpose": "이 화면의 목적 (1줄)",
  "layout_type": "grid|list|detail|form|dashboard|landing|other",
  "components": [
    {
      "name": "구성 요소 이름",
      "type": "button|link|form|image|text|nav|modal|card|table|other",
      "position": "top|middle|bottom|left|right|center|overlay",
      "function": "추정 기능 설명"
    }
  ],
  "user_actions": [
    "사용자가 할 수 있는 주요 액션 (예: 상품 장바구니 추가)"
  ],
  "key_texts": [
    "화면 내 핵심 텍스트 (헤딩, CTA 버튼 텍스트 등)"
  ],
  "next_exploration": [
    {
      "element": "클릭 추천 요소",
      "reason": "탐색 이유",
      "selector_hint": "CSS selector 힌트 (가능하면)"
    }
  ],
  "notable_patterns": "특이 UX 패턴이나 디자인 관찰 사항"
}
```

---

## 분석 원칙

- **기능 추론 우선**: 버튼 텍스트가 없어도 위치와 아이콘으로 기능을 추론한다.
- **한국 서비스 특화**: 한국 이커머스/패션 서비스의 일반적 패턴(좋아요, 장바구니, 리뷰 등) 인식.
- **Element Capture 트리거**: 분석 중 모달/팝업/드롭다운이 감지되면 별도 캡쳐 필요 여부를 `next_exploration`에 표기.
- **불확실한 경우**: "추정: ..." 접두어를 붙여 명시.

---

## 출력 저장

분석 결과는 오케스트레이터가 `output/analysis_manifest.json`에 누적 저장한다:

```json
{
  "service_url": "...",
  "analysis_date": "YYYYMMDD",
  "screens": [
    {
      "screenshot": "output/screenshots/{파일명}.png",
      "url": "...",
      "breadcrumb": "...",
      "analysis": { ... }  // 위 JSON 형식
    }
  ]
}
```
