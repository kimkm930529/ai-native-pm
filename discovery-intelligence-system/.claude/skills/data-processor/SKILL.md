# data-processor — 로컬 데이터 처리 스킬

## 개요

`--input` 옵션으로 제공된 로컬 파일(CSV, md, txt, png/jpg)을
분석 에이전트가 사용할 수 있는 구조화된 데이터로 변환한다.

---

## 스크립트 목록

| 스크립트 | 용도 | 입력 | 출력 |
|---------|------|------|------|
| `formatter.py` | CSV → 마크다운 테이블 변환 | *.csv | temp_table_{name}.md |
| `sentiment_aggregator.py` | 리뷰 CSV 감정 집계 | *.csv (리뷰/별점) | temp_sentiment.json |

---

## formatter.py 호출 규약

```bash
python3 discovery-intelligence-system/.claude/skills/data-processor/scripts/formatter.py \
  --input {csv_파일_경로} \
  --output discovery-intelligence-system/output/temp_table_{파일명}.md \
  [--max-rows 50]     # 기본값: 전체
  [--columns col1,col2]  # 특정 컬럼만 선택
```

**출력 형식:**
```markdown
## {파일명} 데이터 ({N}행)

| 컬럼1 | 컬럼2 | 컬럼3 |
|------|------|------|
| ... | ... | ... |

> 원본: {파일_경로} | 총 {N}행 중 {M}행 표시
```

---

## sentiment_aggregator.py 호출 규약

리뷰 데이터 CSV에서 별점 분포와 키워드 빈도를 집계한다.

```bash
python3 discovery-intelligence-system/.claude/skills/data-processor/scripts/sentiment_aggregator.py \
  --input {csv_파일_경로} \
  --output discovery-intelligence-system/output/temp_sentiment.json \
  [--rating-col "rating"]     # 별점 컬럼명 (기본값: rating, score, stars 자동 감지)
  [--text-col "review_text"]  # 리뷰 텍스트 컬럼명 (기본값: review, text, content 자동 감지)
  [--top-n 10]                # 상위 키워드 수 (기본값: 10)
```

**출력 JSON 스키마:**
```json
{
  "source": "파일명.csv",
  "total_reviews": 1250,
  "rating_distribution": {
    "5": 420, "4": 310, "3": 180, "2": 210, "1": 130
  },
  "avg_rating": 3.6,
  "sentiment_ratio": {
    "positive": 0.58,
    "neutral": 0.14,
    "negative": 0.28
  },
  "top_complaints": [
    {"keyword": "느려요", "count": 87, "sample": "앱이 너무 느려요..."},
    {"keyword": "오류", "count": 64, "sample": "결제 중 오류가..."}
  ],
  "top_praises": [
    {"keyword": "편리", "count": 112, "sample": "정말 편리하게..."},
    {"keyword": "디자인", "count": 89, "sample": "UI 디자인이 깔끔..."}
  ],
  "warning_signals": [
    "결제 오류 언급 64건 — 즉각 확인 필요",
    "앱 속도 불만 87건 — 성능 개선 필요"
  ]
}
```

---

## input_manifest.json 생성

`--input` 폴더 스캔 후 아래 형식으로 파일 분류 결과를 저장한다.

```json
{
  "scanned_at": "2026-03-08T10:00:00",
  "input_folder": "input/",
  "files": [
    {
      "path": "input/reviews_competitor_A.csv",
      "type": "csv",
      "assigned_to": "sentiment_aggregator",
      "status": "ready"
    },
    {
      "path": "input/feature_comparison.md",
      "type": "markdown",
      "assigned_to": "direct_context",
      "status": "ready"
    },
    {
      "path": "input/screenshot_01.png",
      "type": "image",
      "assigned_to": "reference-explorer",
      "status": "ready"
    },
    {
      "path": "input/unknown_file.xlsx",
      "type": "unknown",
      "assigned_to": null,
      "status": "escalate",
      "note": "사용자에게 용도 문의 필요"
    }
  ]
}
```

---

## 오류 처리

| 오류 | 처리 방법 |
|------|---------|
| CSV 인코딩 오류 | UTF-8 → EUC-KR 재시도, 실패 시 파일 경로 안내 |
| 별점/리뷰 컬럼 미감지 | 컬럼명 목록 출력 후 사용자에게 지정 요청 |
| 빈 CSV (0행) | "데이터 없음" 표기 + 파일 확인 안내 |
| 이미지 처리 불가 | reference-explorer에 직접 전달 (멀티모달 분석) |
| 미지원 파일 형식 | input_manifest.json의 status를 "escalate"로 설정 |
