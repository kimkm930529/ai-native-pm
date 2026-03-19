"""
Markdown → Confluence Storage Format 변환 + 일괄 업로드 스크립트
"""
import re
import sys
import subprocess
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent


def md_to_confluence(text: str) -> str:
    lines = text.split("\n")
    html_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # ── 수평선 ──────────────────────────────────────────
        if re.match(r"^-{3,}$", line.strip()):
            html_lines.append("<hr/>")
            i += 1
            continue

        # ── 표 (테이블) ─────────────────────────────────────
        if "|" in line and i + 1 < len(lines) and re.match(r"^\|[-| :]+\|", lines[i + 1]):
            table_lines = []
            while i < len(lines) and "|" in lines[i]:
                table_lines.append(lines[i])
                i += 1
            html_lines.append(render_table(table_lines))
            continue

        # ── 헤더 ────────────────────────────────────────────
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        if m:
            level = len(m.group(1))
            content = inline(m.group(2))
            html_lines.append(f"<h{level}>{content}</h{level}>")
            i += 1
            continue

        # ── 인용구 ───────────────────────────────────────────
        if line.startswith(">"):
            quote_lines = []
            while i < len(lines) and lines[i].startswith(">"):
                quote_lines.append(lines[i].lstrip("> "))
                i += 1
            inner = " ".join(quote_lines)
            html_lines.append(f"<blockquote><p>{inline(inner)}</p></blockquote>")
            continue

        # ── 순서 없는 목록 ────────────────────────────────────
        if re.match(r"^[-*+]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^[-*+]\s+", lines[i]):
                content = re.sub(r"^[-*+]\s+", "", lines[i])
                # 중첩 항목 처리 (들여쓰기)
                items.append(f"<li>{inline(content)}</li>")
                i += 1
            html_lines.append("<ul>" + "".join(items) + "</ul>")
            continue

        # ── 순서 있는 목록 ────────────────────────────────────
        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                content = re.sub(r"^\d+\.\s+", "", lines[i])
                items.append(f"<li>{inline(content)}</li>")
                i += 1
            html_lines.append("<ol>" + "".join(items) + "</ol>")
            continue

        # ── 빈 줄 ────────────────────────────────────────────
        if line.strip() == "":
            html_lines.append("")
            i += 1
            continue

        # ── 일반 단락 ────────────────────────────────────────
        html_lines.append(f"<p>{inline(line)}</p>")
        i += 1

    return "\n".join(html_lines)


def render_table(table_lines: list) -> str:
    rows = []
    for idx, line in enumerate(table_lines):
        cells = [c.strip() for c in line.strip("|").split("|")]
        if idx == 1 and all(re.match(r"^[-: ]+$", c) for c in cells):
            continue  # 구분 행 스킵
        is_header = idx == 0
        tag = "th" if is_header else "td"
        row_html = "".join(f"<{tag}><p>{inline(c)}</p></{tag}>" for c in cells)
        rows.append(f"<tr>{row_html}</tr>")
    return f'<table><tbody>{"".join(rows)}</tbody></table>'


def inline(text: str) -> str:
    # Bold italic
    text = re.sub(r"\*\*\*(.*?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    # Bold
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
    # Inline code
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # Links [text](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    # Strikethrough ~~text~~
    text = re.sub(r"~~(.*?)~~", r"<s>\1</s>", text)
    # HTML escape for < > & (but preserve already converted tags)
    # Actually keep as-is since we're generating HTML
    return text


def upload(title: str, draft_path: Path, space: str = "membership", parent_id: str = "336920647"):
    script = Path(__file__).parents[1] / ".claude/skills/confluence-tool/scripts/upload.py"
    cmd = [
        sys.executable, str(script),
        "--title", title,
        "--space", space,
        "--parent-id", parent_id,
        "--draft", str(draft_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).parents[1]))
    print(result.stdout)
    if result.returncode != 0:
        print(f"[ERROR] {result.stderr}", file=sys.stderr)
    return result.returncode


FILES = [
    ("flash_20260105.md", "Auxia x Musinsa — Weekly Flash Report (26-01-05)"),
    ("flash_20260115.md", "Auxia x Musinsa — Weekly Flash Report (26-01-15)"),
    ("flash_20260123.md", "Auxia x Musinsa — Weekly Flash Report (26-01-23)"),
    ("flash_20260130.md", "Auxia x Musinsa — Weekly Flash Report (26-01-30)"),
    ("flash_20260206.md", "Auxia x Musinsa — Weekly Flash Report (26-02-06)"),
    ("flash_20260213.md", "Auxia x Musinsa — Weekly Flash Report (26-02-13)"),
    ("flash_20260227.md", "Auxia x Musinsa — Weekly Flash Report (26-02-27)"),
]

if __name__ == "__main__":
    results = []
    for filename, title in FILES:
        md_path = OUTPUT_DIR / filename
        if not md_path.exists():
            print(f"[SKIP] 파일 없음: {md_path}")
            continue

        print(f"\n{'='*60}")
        print(f"처리 중: {title}")

        md_text = md_path.read_text(encoding="utf-8")
        html = md_to_confluence(md_text)

        draft_path = OUTPUT_DIR / f"draft_{filename.replace('.md', '.html')}"
        draft_path.write_text(html, encoding="utf-8")

        rc = upload(title, draft_path)
        results.append((title, rc))

    print(f"\n{'='*60}")
    print("완료 결과:")
    for title, rc in results:
        status = "✅ 성공" if rc == 0 else "❌ 실패"
        print(f"  {status} — {title}")
