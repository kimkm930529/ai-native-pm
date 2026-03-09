#!/usr/bin/env python3
"""
sentiment_aggregator.py — 리뷰 CSV 감정 집계 스크립트
Usage: python3 sentiment_aggregator.py --input reviews.csv --output temp_sentiment.json
       [--rating-col rating] [--text-col review_text] [--top-n 10]
"""

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime


# 한국어 감정 키워드 사전 (기본)
POSITIVE_KEYWORDS = [
    "좋아", "좋은", "편리", "편하", "빠르", "깔끔", "유용", "만족", "추천", "완벽",
    "최고", "훌륭", "친절", "쉬운", "직관", "깔끔", "디자인", "깔끔해", "잘됨"
]
NEGATIVE_KEYWORDS = [
    "느려", "오류", "버그", "불편", "어려", "복잡", "최악", "별로", "실망", "화남",
    "짜증", "안됨", "안돼", "문제", "튕겨", "느림", "충돌", "에러", "불만", "개선"
]


def detect_column(headers: list, candidates: list) -> str | None:
    """컬럼명 자동 감지"""
    lower_headers = {h.lower(): h for h in headers}
    for candidate in candidates:
        if candidate.lower() in lower_headers:
            return lower_headers[candidate.lower()]
    return None


def classify_sentiment(rating: float | None, text: str) -> str:
    """별점 + 텍스트 기반 감정 분류"""
    if rating is not None:
        if rating >= 4.0:
            return "positive"
        elif rating <= 2.0:
            return "negative"
        else:
            return "neutral"

    # 별점 없을 때 텍스트 기반
    pos = sum(1 for kw in POSITIVE_KEYWORDS if kw in text)
    neg = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text)
    if pos > neg:
        return "positive"
    elif neg > pos:
        return "negative"
    return "neutral"


def extract_keywords(texts: list, keyword_list: list, top_n: int) -> list:
    """키워드 빈도 집계"""
    counter = Counter()
    samples = {}
    for text in texts:
        for kw in keyword_list:
            if kw in text:
                counter[kw] += 1
                if kw not in samples:
                    # 첫 50자만 샘플로
                    idx = text.find(kw)
                    samples[kw] = text[max(0, idx - 10):idx + 40].strip()

    return [
        {"keyword": kw, "count": cnt, "sample": samples.get(kw, "")}
        for kw, cnt in counter.most_common(top_n)
    ]


def aggregate(input_path: str, output_path: str, rating_col_hint: str,
              text_col_hint: str, top_n: int) -> dict:

    result = {"success": False, "error": None}

    try:
        rows_raw = []
        headers = []

        for encoding in ["utf-8-sig", "utf-8", "euc-kr", "cp949"]:
            try:
                with open(input_path, encoding=encoding, newline="") as f:
                    reader = csv.DictReader(f)
                    headers = reader.fieldnames or []
                    rows_raw = list(reader)
                break
            except UnicodeDecodeError:
                continue
        else:
            result["error"] = "파일 인코딩 인식 불가"
            return result

        if not rows_raw:
            result["error"] = "데이터가 없습니다 (0행)"
            return result

        # 컬럼 자동 감지
        rating_col = detect_column(headers, [rating_col_hint, "rating", "score", "stars", "별점", "평점"])
        text_col = detect_column(headers, [text_col_hint, "review_text", "review", "text", "content", "리뷰", "내용"])

        if not text_col:
            result["error"] = f"리뷰 텍스트 컬럼을 찾을 수 없습니다. 사용 가능한 컬럼: {headers}"
            return result

        # 데이터 추출
        ratings = []
        texts = []
        rating_dist = Counter()

        for row in rows_raw:
            text = str(row.get(text_col, "")).strip()
            texts.append(text)

            rating = None
            if rating_col:
                try:
                    rating = float(row.get(rating_col, 0))
                    star = min(5, max(1, round(rating)))
                    rating_dist[str(star)] += 1
                    ratings.append(rating)
                except (ValueError, TypeError):
                    pass

        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

        # 감정 분류
        sentiments = []
        for text, *rest in zip(texts, ratings if ratings else [None] * len(texts)):
            rating = rest[0] if rest else None
            sentiments.append(classify_sentiment(rating, text))

        total = len(sentiments)
        sentiment_ratio = {
            "positive": round(sentiments.count("positive") / total, 2),
            "neutral": round(sentiments.count("neutral") / total, 2),
            "negative": round(sentiments.count("negative") / total, 2),
        }

        # 부정 리뷰에서 불만 키워드, 긍정 리뷰에서 강점 키워드
        neg_texts = [t for t, s in zip(texts, sentiments) if s == "negative"]
        pos_texts = [t for t, s in zip(texts, sentiments) if s == "positive"]

        top_complaints = extract_keywords(neg_texts, NEGATIVE_KEYWORDS, top_n)
        top_praises = extract_keywords(pos_texts, POSITIVE_KEYWORDS, top_n)

        # 경고 신호: 100건 이상 또는 전체의 5% 이상 반복 불만
        warning_signals = []
        for item in top_complaints:
            threshold = max(10, total * 0.05)
            if item["count"] >= threshold:
                warning_signals.append(
                    f"'{item['keyword']}' 언급 {item['count']}건 ({round(item['count']/total*100)}%) — 확인 필요"
                )

        output_data = {
            "source": os.path.basename(input_path),
            "analyzed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "total_reviews": total,
            "rating_distribution": dict(rating_dist) if rating_dist else "별점 데이터 없음",
            "avg_rating": avg_rating,
            "sentiment_ratio": sentiment_ratio,
            "top_complaints": top_complaints,
            "top_praises": top_praises,
            "warning_signals": warning_signals if warning_signals else ["특이 경고 신호 없음"],
        }

        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        result.update({"success": True, "total": total, "avg_rating": avg_rating})
        return result

    except FileNotFoundError:
        result["error"] = f"파일을 찾을 수 없습니다: {input_path}"
        return result
    except Exception as e:
        result["error"] = str(e)
        return result


def main():
    parser = argparse.ArgumentParser(description="리뷰 CSV 감정 집계")
    parser.add_argument("--input", required=True, help="입력 CSV 파일 경로")
    parser.add_argument("--output", required=True, help="출력 JSON 파일 경로")
    parser.add_argument("--rating-col", default="rating", help="별점 컬럼명")
    parser.add_argument("--text-col", default="review_text", help="리뷰 텍스트 컬럼명")
    parser.add_argument("--top-n", type=int, default=10, help="상위 키워드 수")
    args = parser.parse_args()

    result = aggregate(args.input, args.output, args.rating_col, args.text_col, args.top_n)

    if result["success"]:
        print(f"[OK] 집계 완료: {result['total']}건 분석 → {args.output}")
        if result["avg_rating"]:
            print(f"     평균 별점: {result['avg_rating']}/5.0")
    else:
        print(f"[ERROR] {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
