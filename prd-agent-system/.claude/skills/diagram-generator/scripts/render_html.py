"""
Diagram Generator — SVG/HTML 렌더러

SVG 파일 또는 인라인 SVG 코드를 표준 다이어그램 HTML 템플릿으로 감싸 .html 파일 생성.
Mermaid 없이 순수 SVG 다이어그램 (아키텍처, 매트릭스, 타임라인, IA 등) 에 사용.

사용법:
  python3 render_html.py --svg output/diagrams/system_arch.svg --name system_arch
  python3 render_html.py --inline-svg "<svg...>" --name system_arch
  python3 render_html.py --svg output/diagrams/system_arch.svg --name system_arch --title "시스템 아키텍처"
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# ─── 경로 설정 ─────────────────────────────────────────────────────────────
PROJECT_ROOT    = Path(__file__).parents[4]
OUTPUT_DIAGRAMS = PROJECT_ROOT / "output" / "diagrams"

# ─── HTML 템플릿 ───────────────────────────────────────────────────────────
HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    :root {{
      --bg:        #0f172a;
      --surface:   #1e293b;
      --surface-2: #334155;
      --border:    #2d3f55;
      --text-1:    #f1f5f9;
      --text-2:    #94a3b8;
      --accent:    #6366f1;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text-1);
      min-height: 100vh;
      padding: 56px 24px 80px;
    }}

    /* ── 헤더 ── */
    .header {{
      text-align: center;
      margin-bottom: 44px;
    }}
    .header h1 {{
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--text-1);
      letter-spacing: -0.025em;
      margin-bottom: 10px;
    }}
    .header .meta {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      font-size: 0.78rem;
      color: var(--text-2);
    }}
    .badge {{
      background: var(--surface-2);
      border: 1px solid var(--border);
      padding: 2px 10px;
      border-radius: 999px;
      font-size: 0.7rem;
      color: var(--text-2);
      letter-spacing: 0.02em;
    }}
    .sep {{ color: var(--border); }}

    /* ── 다이어그램 래퍼 ── */
    .diagram-wrapper {{
      max-width: 1200px;
      margin: 0 auto;
    }}

    /* 툴바 */
    .diagram-toolbar {{
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 6px;
      margin-bottom: 8px;
    }}
    .toolbar-btn {{
      background: var(--surface-2);
      border: 1px solid var(--border);
      color: var(--text-2);
      border-radius: 6px;
      padding: 4px 10px;
      font-size: 0.72rem;
      cursor: pointer;
      transition: color .15s, background .15s;
      user-select: none;
    }}
    .toolbar-btn:hover {{ background: var(--border); color: var(--text-1); }}
    .zoom-label {{
      font-size: 0.72rem;
      color: var(--text-2);
      min-width: 36px;
      text-align: center;
    }}

    /* 카드 */
    .diagram-box {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      box-shadow:
        0 0 0 1px rgba(255,255,255,.03),
        0 8px 32px rgba(0,0,0,.5),
        0 2px 8px rgba(0,0,0,.3);
      overflow: hidden;
      position: relative;
      cursor: grab;
      min-height: 360px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .diagram-box.grabbing {{ cursor: grabbing; }}

    /* 줌/팬 내부 캔버스 */
    .diagram-canvas {{
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      transform-origin: center center;
      transition: transform .05s linear;
      padding: 36px 44px;
    }}
    .diagram-canvas svg {{
      max-width: 100%;
      height: auto;
      display: block;
    }}

    /* ── 소스 코드 토글 ── */
    details {{
      max-width: 1200px;
      margin: 20px auto 0;
    }}
    details > summary {{
      cursor: pointer;
      color: var(--text-2);
      font-size: 0.78rem;
      padding: 10px 4px;
      user-select: none;
      list-style: none;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    details > summary::before {{
      content: '›';
      font-size: 1rem;
      transition: transform .15s;
      display: inline-block;
    }}
    details[open] > summary::before {{ transform: rotate(90deg); }}
    details > summary:hover {{ color: var(--text-1); }}
    .source-block {{
      margin-top: 6px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 20px 24px;
      font-family: "JetBrains Mono", "SF Mono", "Fira Code", monospace;
      font-size: 0.74rem;
      color: #64748b;
      white-space: pre;
      overflow: auto;
      line-height: 1.65;
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>{title}</h1>
    <div class="meta">
      <span class="badge">diagram-generator · svg</span>
      <span class="sep">·</span>
      <span>{generated_at}</span>
    </div>
  </div>

  <div class="diagram-wrapper">
    <div class="diagram-toolbar">
      <button class="toolbar-btn" id="btn-zoom-out">−</button>
      <span class="zoom-label" id="zoom-label">100%</span>
      <button class="toolbar-btn" id="btn-zoom-in">+</button>
      <button class="toolbar-btn" id="btn-reset">Reset</button>
    </div>
    <div class="diagram-box" id="diagram-box">
      <div class="diagram-canvas" id="diagram-canvas">
{svg_content}
      </div>
    </div>
  </div>

  <details>
    <summary>SVG 소스 보기</summary>
    <div class="source-block">{svg_escaped}</div>
  </details>

  <script>
    (function () {{
      const box    = document.getElementById('diagram-box');
      const canvas = document.getElementById('diagram-canvas');
      const label  = document.getElementById('zoom-label');

      let scale = 1, tx = 0, ty = 0;
      let isDragging = false, startX = 0, startY = 0, baseX = 0, baseY = 0;
      const MIN_SCALE = 0.2, MAX_SCALE = 5, STEP = 0.2;

      function applyTransform() {{
        canvas.style.transform = `translate(${{tx}}px, ${{ty}}px) scale(${{scale}})`;
        label.textContent = Math.round(scale * 100) + '%';
      }}

      function clamp(x, y) {{
        const limit = 1200 * scale;
        return [Math.max(-limit, Math.min(limit, x)),
                Math.max(-limit, Math.min(limit, y))];
      }}

      document.getElementById('btn-zoom-in').addEventListener('click', () => {{
        scale = Math.min(MAX_SCALE, Math.round((scale + STEP) * 10) / 10);
        applyTransform();
      }});
      document.getElementById('btn-zoom-out').addEventListener('click', () => {{
        scale = Math.max(MIN_SCALE, Math.round((scale - STEP) * 10) / 10);
        applyTransform();
      }});
      document.getElementById('btn-reset').addEventListener('click', () => {{
        scale = 1; tx = 0; ty = 0; applyTransform();
      }});

      box.addEventListener('wheel', (e) => {{
        e.preventDefault();
        const delta = e.deltaY > 0 ? -STEP : STEP;
        scale = Math.min(MAX_SCALE, Math.max(MIN_SCALE,
                  Math.round((scale + delta) * 10) / 10));
        applyTransform();
      }}, {{ passive: false }});

      box.addEventListener('mousedown', (e) => {{
        if (e.button !== 0) return;
        isDragging = true;
        startX = e.clientX; startY = e.clientY;
        baseX = tx; baseY = ty;
        box.classList.add('grabbing');
      }});
      window.addEventListener('mousemove', (e) => {{
        if (!isDragging) return;
        const [cx, cy] = clamp(baseX + (e.clientX - startX), baseY + (e.clientY - startY));
        tx = cx; ty = cy;
        applyTransform();
      }});
      window.addEventListener('mouseup', () => {{
        isDragging = false;
        box.classList.remove('grabbing');
      }});

      // 터치 팬
      let tStartX = 0, tStartY = 0, tBaseX = 0, tBaseY = 0;
      box.addEventListener('touchstart', (e) => {{
        if (e.touches.length !== 1) return;
        tStartX = e.touches[0].clientX; tStartY = e.touches[0].clientY;
        tBaseX = tx; tBaseY = ty;
      }}, {{ passive: true }});
      box.addEventListener('touchmove', (e) => {{
        if (e.touches.length !== 1) return;
        e.preventDefault();
        const [cx, cy] = clamp(tBaseX + (e.touches[0].clientX - tStartX),
                                tBaseY + (e.touches[0].clientY - tStartY));
        tx = cx; ty = cy;
        applyTransform();
      }}, {{ passive: false }});
    }})();
  </script>
</body>
</html>
"""


def render_svg(svg_content: str, name: str, title: str | None = None) -> Path:
    """SVG 문자열을 받아 output/diagrams/{name}.html로 저장."""
    OUTPUT_DIAGRAMS.mkdir(parents=True, exist_ok=True)

    if title is None:
        title = name.replace("_", " ").replace("-", " ").title()

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    # SVG 들여쓰기 정렬
    indented_svg = "\n".join("        " + line for line in svg_content.strip().splitlines())
    escaped_svg  = svg_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    html_content = HTML_TEMPLATE.format(
        title=title,
        generated_at=generated_at,
        svg_content=indented_svg,
        svg_escaped=escaped_svg,
    )

    out_path = OUTPUT_DIAGRAMS / f"{name}.html"
    out_path.write_text(html_content, encoding="utf-8")
    print(f"✅ 렌더링 완료: {out_path}")
    return out_path


def render_svg_file(svg_path: Path, name: str | None = None, title: str | None = None) -> Path:
    """SVG 파일을 읽어 HTML로 변환."""
    svg_path = svg_path.resolve()
    if not svg_path.exists():
        raise FileNotFoundError(f"SVG 파일 없음: {svg_path}")

    svg_content = svg_path.read_text(encoding="utf-8")
    if name is None:
        name = svg_path.stem
    return render_svg(svg_content, name, title)


# ─── CLI ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SVG → HTML 다이어그램 렌더러")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--svg", metavar="FILE",
                       help=".svg 파일 경로")
    group.add_argument("--inline-svg", metavar="CODE",
                       help="인라인 SVG 코드 문자열")

    parser.add_argument("--name", metavar="NAME", required=True,
                        help="출력 파일명 (확장자 제외, 예: system_arch)")
    parser.add_argument("--title", metavar="TITLE",
                        help="다이어그램 제목 (기본값: name을 Title Case로 변환)")
    args = parser.parse_args()

    try:
        if args.svg:
            out = render_svg_file(Path(args.svg), args.name, args.title)
        else:
            out = render_svg(args.inline_svg, args.name, args.title)

        print(f"📊 HTML: file://{out}")

    except Exception as e:
        print(f"⚠️  오류: {e}")
        sys.exit(1)
