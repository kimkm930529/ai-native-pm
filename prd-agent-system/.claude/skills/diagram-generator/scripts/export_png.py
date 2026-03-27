"""
Diagram Generator — PNG 내보내기

렌더링된 .html (또는 .mmd) 파일에서 다이어그램 SVG만 추출하여 PNG로 저장.
Playwright headless Chromium 사용.

사용법:
  python3 export_png.py output/diagrams/campaign_service_flow.html
  python3 export_png.py output/diagrams/campaign_service_flow.mmd   # html 자동 렌더링 후 PNG
  python3 export_png.py --all                                        # output/diagrams/*.mmd 전체
  python3 export_png.py output/diagrams/campaign_service_flow.html --bg "#1e293b" --padding 32
"""

import sys
import argparse
import asyncio
from pathlib import Path

# ─── 경로 설정 ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parents[4]
OUTPUT_DIAGRAMS = PROJECT_ROOT / "output" / "diagrams"

# ─── 기본값 ─────────────────────────────────────────────────────────────────
DEFAULT_BG      = "#1e293b"   # 다이어그램 카드 배경색과 동일
DEFAULT_PADDING = 40          # SVG 주변 여백(px)
DEFAULT_SCALE   = 2           # 레티나 해상도 (2x)


async def _export(html_path: Path, out_path: Path,
                  bg: str, padding: int, scale: int) -> Path:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(device_scale_factor=scale)

        # ── HTML 로드 ──────────────────────────────────────────────────────
        await page.goto(f"file://{html_path.resolve()}", wait_until="networkidle")

        # ── Mermaid SVG 렌더링 대기 ────────────────────────────────────────
        try:
            await page.wait_for_selector(".mermaid svg", timeout=12_000)
        except Exception:
            print(f"⚠️  SVG 렌더링 타임아웃: {html_path.name}")
            await browser.close()
            raise

        # 애니메이션 완료 대기
        await page.wait_for_timeout(600)

        # ── 컨테이너 제약 해제 (PNG는 SVG 원본 크기로) ────────────────────
        await page.evaluate("""
            () => {
                // 16:9 aspect-ratio 및 overflow 제약 제거
                const box = document.querySelector('.diagram-box');
                if (box) {
                    box.style.aspectRatio  = 'unset';
                    box.style.overflow     = 'visible';
                    box.style.width        = 'max-content';
                    box.style.height       = 'max-content';
                    box.style.padding      = '0';
                    box.style.border       = 'none';
                    box.style.boxShadow    = 'none';
                    box.style.borderRadius = '0';
                    box.style.background   = 'transparent';
                }
                const canvas = document.querySelector('.diagram-canvas');
                if (canvas) {
                    canvas.style.position  = 'static';
                    canvas.style.transform = 'none';
                    canvas.style.padding   = '0';
                    canvas.style.width     = 'max-content';
                    canvas.style.height    = 'max-content';
                }
                // 툴바·헤더·소스 블록 숨김
                ['.diagram-toolbar', '.header', 'details'].forEach(sel => {
                    const el = document.querySelector(sel);
                    if (el) el.style.display = 'none';
                });
                document.body.style.padding    = '0';
                document.body.style.background = 'transparent';
            }
        """)

        await page.wait_for_timeout(200)

        # ── SVG 요소 캡처 ──────────────────────────────────────────────────
        svg_el = page.locator(".mermaid svg").first
        box_info = await svg_el.bounding_box()

        if not box_info:
            await browser.close()
            raise RuntimeError("SVG bounding box를 가져올 수 없습니다.")

        # 패딩 포함 스크린샷 영역 계산
        clip = {
            "x":      max(0, box_info["x"] - padding),
            "y":      max(0, box_info["y"] - padding),
            "width":  box_info["width"]  + padding * 2,
            "height": box_info["height"] + padding * 2,
        }

        # 뷰포트를 다이어그램 크기에 맞게 확장
        await page.set_viewport_size({
            "width":  int(clip["x"] + clip["width"])  + 20,
            "height": int(clip["y"] + clip["height"]) + 20,
        })

        await page.screenshot(
            path=str(out_path),
            clip=clip,
            omit_background=False,
        )

        # 배경색이 투명하면 bg로 채우기
        _apply_background(out_path, bg, padding, scale)

        await browser.close()

    print(f"✅ PNG 저장: {out_path}")
    return out_path


def _apply_background(png_path: Path, bg_hex: str, padding: int, scale: int):
    """PNG에 단색 배경을 합성 (Pillow 있는 경우). 없으면 스킵."""
    try:
        from PIL import Image

        r = int(bg_hex.lstrip("#")[0:2], 16)
        g = int(bg_hex.lstrip("#")[2:4], 16)
        b = int(bg_hex.lstrip("#")[4:6], 16)

        src = Image.open(png_path).convert("RGBA")
        bg  = Image.new("RGBA", src.size, (r, g, b, 255))
        out = Image.alpha_composite(bg, src)

        # 추가 패딩 여백을 배경색으로
        padded_w = src.width  + padding * scale * 2
        padded_h = src.height + padding * scale * 2
        canvas   = Image.new("RGBA", (padded_w, padded_h), (r, g, b, 255))
        canvas.paste(out, (padding * scale, padding * scale))
        canvas.convert("RGB").save(png_path, "PNG", optimize=True)

    except ImportError:
        pass   # Pillow 없으면 투명 배경 그대로 저장


def export(html_path, out_path=None,
           bg=DEFAULT_BG,
           padding=DEFAULT_PADDING,
           scale=DEFAULT_SCALE):
    """동기 래퍼."""
    if out_path is None:
        out_path = html_path.with_suffix(".png")
    asyncio.run(_export(html_path, out_path, bg, padding, scale))
    return out_path


def ensure_html(mmd_path: Path) -> Path:
    """.mmd → .html 렌더링 후 경로 반환."""
    html_path = mmd_path.with_suffix(".html")
    if not html_path.exists():
        # render.py와 같은 디렉토리에 있다고 가정
        render_script = Path(__file__).parent / "render.py"
        import subprocess
        result = subprocess.run(
            [sys.executable, str(render_script), str(mmd_path)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"render.py 실패:\n{result.stderr}")
    return html_path


def export_all(bg=DEFAULT_BG, padding=DEFAULT_PADDING, scale=DEFAULT_SCALE):
    mmd_files = list(OUTPUT_DIAGRAMS.glob("*.mmd"))
    if not mmd_files:
        print("내보낼 .mmd 파일이 없습니다.")
        return []
    results = []
    for f in sorted(mmd_files):
        try:
            html = ensure_html(f)
            out  = export(html, bg=bg, padding=padding, scale=scale)
            results.append(out)
        except Exception as e:
            print(f"⚠️  {f.name} PNG 변환 실패: {e}")
    return results


# ─── CLI ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mermaid 다이어그램 → PNG 내보내기")
    parser.add_argument("files", nargs="*",
                        help=".html 또는 .mmd 파일 경로 (없으면 --all 필요)")
    parser.add_argument("--all", action="store_true", dest="all_files",
                        help="output/diagrams/ 내 모든 .mmd 처리")
    parser.add_argument("--out", metavar="PATH",
                        help="출력 PNG 경로 (단일 파일 지정 시)")
    parser.add_argument("--bg", default=DEFAULT_BG, metavar="HEX",
                        help=f"배경색 (기본값: {DEFAULT_BG})")
    parser.add_argument("--padding", type=int, default=DEFAULT_PADDING,
                        help=f"SVG 주변 여백 px (기본값: {DEFAULT_PADDING})")
    parser.add_argument("--scale", type=int, default=DEFAULT_SCALE,
                        help=f"해상도 배율 (기본값: {DEFAULT_SCALE}, 레티나=2)")
    args = parser.parse_args()

    if args.all_files:
        results = export_all(bg=args.bg, padding=args.padding, scale=args.scale)
        if results:
            print(f"\n🖼️  총 {len(results)}개 PNG 내보내기 완료:")
            for r in results:
                print(f"  file://{r}")

    elif args.files:
        for fp in args.files:
            path = Path(fp)
            try:
                if path.suffix == ".mmd":
                    path = ensure_html(path)
                out_path = Path(args.out) if args.out else None
                result = export(path, out_path,
                                bg=args.bg, padding=args.padding, scale=args.scale)
                print(f"🖼️  PNG: file://{result}")
            except Exception as e:
                print(f"⚠️  오류: {e}")

    else:
        parser.print_help()
        sys.exit(1)
