#!/usr/bin/env python3
"""
formatter.py — CSV → 마크다운 테이블 변환 스크립트
Usage: python3 formatter.py --input file.csv --output output.md [--max-rows 50] [--columns col1,col2]
"""

import argparse
import csv
import os
import sys


def csv_to_markdown(input_path: str, output_path: str, max_rows: int = None, columns: list = None) -> dict:
    result = {"success": False, "rows": 0, "cols": 0, "error": None}

    try:
        # 인코딩 자동 감지 (UTF-8 → EUC-KR)
        for encoding in ["utf-8-sig", "utf-8", "euc-kr", "cp949"]:
            try:
                with open(input_path, encoding=encoding, newline="") as f:
                    reader = csv.DictReader(f)
                    headers = reader.fieldnames
                    if not headers:
                        result["error"] = "컬럼 헤더를 찾을 수 없습니다."
                        return result

                    # 컬럼 필터링
                    if columns:
                        selected = [c for c in columns if c in headers]
                        if not selected:
                            result["error"] = f"지정한 컬럼이 없습니다. 사용 가능: {headers}"
                            return result
                    else:
                        selected = list(headers)

                    rows = []
                    for i, row in enumerate(reader):
                        if max_rows and i >= max_rows:
                            break
                        rows.append([str(row.get(col, "")) for col in selected])

                break  # 인코딩 성공
            except UnicodeDecodeError:
                continue
        else:
            result["error"] = "파일 인코딩을 인식할 수 없습니다."
            return result

        # 마크다운 생성
        file_name = os.path.basename(input_path)
        total_rows = len(rows)

        lines = [f"## {file_name} 데이터 ({total_rows}행)\n"]
        lines.append("| " + " | ".join(selected) + " |")
        lines.append("|" + "|".join(["---"] * len(selected)) + "|")
        for row in rows:
            safe_row = [cell.replace("|", "\\|").replace("\n", " ") for cell in row]
            lines.append("| " + " | ".join(safe_row) + " |")

        note = f"\n> 원본: `{input_path}` | 총 {total_rows}행 표시"
        lines.append(note)

        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        result.update({"success": True, "rows": total_rows, "cols": len(selected)})
        return result

    except FileNotFoundError:
        result["error"] = f"파일을 찾을 수 없습니다: {input_path}"
        return result
    except Exception as e:
        result["error"] = str(e)
        return result


def main():
    parser = argparse.ArgumentParser(description="CSV → 마크다운 테이블 변환")
    parser.add_argument("--input", required=True, help="입력 CSV 파일 경로")
    parser.add_argument("--output", required=True, help="출력 마크다운 파일 경로")
    parser.add_argument("--max-rows", type=int, default=None, help="최대 출력 행 수")
    parser.add_argument("--columns", default=None, help="선택할 컬럼명 (쉼표 구분)")
    args = parser.parse_args()

    columns = args.columns.split(",") if args.columns else None
    result = csv_to_markdown(args.input, args.output, args.max_rows, columns)

    if result["success"]:
        print(f"[OK] 변환 완료: {result['rows']}행 × {result['cols']}열 → {args.output}")
    else:
        print(f"[ERROR] {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
