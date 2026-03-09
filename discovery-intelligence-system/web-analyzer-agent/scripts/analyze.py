"""
Auxia Console — Web Vision Analyzer (Deep Mode)
실행: python3 scripts/analyze.py
탐색: GNB → 탭 클릭 → 주요 항목 1 depth
"""
import sys
sys.path.insert(0, '/Users/musinsa/Library/Python/3.9/lib/python/site-packages')

from playwright.sync_api import sync_playwright
import time, json
from pathlib import Path
from datetime import datetime

BASE   = Path(__file__).parent.parent
SS_DIR = BASE / 'output' / 'screenshots'
OUT    = BASE / 'output'
SS_DIR.mkdir(parents=True, exist_ok=True)

DATE = datetime.now().strftime('%Y%m%d')
TARGET_URL = 'https://console.auxia.app/?companyId=5047'
screens = []  # 전체 캡쳐 결과


# ── 유틸 ──────────────────────────────────────

def shot(page, name):
    safe = ''.join(c if c.isalnum() or c in '-_' else '_' for c in name)[:40]
    path = str(SS_DIR / f'{DATE}_{safe}.png')
    page.screenshot(path=path, full_page=True)
    rel  = f'screenshots/{DATE}_{safe}.png'
    print(f'    📸 {rel}')
    return rel

def wait(page, ms=1500):
    try:
        page.wait_for_load_state('networkidle', timeout=ms)
    except:
        pass
    time.sleep(0.8)

def body_text(page):
    try:
        return page.evaluate('document.body.innerText')
    except:
        return ''

def is_app_loaded(page):
    url = page.url
    if 'accounts.google.com' in url:
        return False
    if not url.startswith('https://console.auxia.app'):
        return False
    t = body_text(page)
    login_signs = ['sign in to get started', 'welcome to auxia!',
                   'sign in with email', 'sign in with google', '이메일을 잊으셨나요']
    return not any(s in t.lower() for s in login_signs) and len(t.strip()) > 100

def structure(page):
    return page.evaluate("""
        () => ({
            headings: Array.from(document.querySelectorAll('h1,h2,h3,h4'))
                        .map(e=>e.textContent?.trim()).filter(Boolean).slice(0,10),
            buttons:  Array.from(document.querySelectorAll('button'))
                        .map(e=>e.textContent?.trim()).filter(t=>t&&t.length<60).slice(0,15),
            table_headers: Array.from(document.querySelectorAll('th,[role=columnheader]'))
                        .map(e=>e.textContent?.trim()).filter(Boolean).slice(0,15),
            body_preview: document.body.innerText.slice(0,600),
        })
    """)

def get_tabs(page):
    """현재 페이지의 탭 목록 추출"""
    return page.evaluate("""
        () => {
            // MUI Tabs, 일반 탭, 버튼 탭 패턴 탐지
            const sels = [
                '[role=tab]',
                '[class*=Tab] button', '[class*=tab] button',
                '.MuiTab-root', '.MuiButtonBase-root[role=tab]',
                'button[aria-selected]',
            ];
            for (const sel of sels) {
                const els = Array.from(document.querySelectorAll(sel));
                if (els.length >= 2) {
                    return els.map(e => ({
                        text: e.textContent?.trim(),
                        selected: e.getAttribute('aria-selected') === 'true' ||
                                  e.classList.contains('active') ||
                                  e.getAttribute('tabindex') === '0'
                    })).filter(x => x.text && x.text.length < 60);
                }
            }
            return [];
        }
    """)

def click_tab(page, tab_text):
    """탭 텍스트로 탭 클릭"""
    try:
        # role=tab 먼저 시도
        tab = page.locator(f'[role=tab]:has-text("{tab_text}")').first
        if tab.count() == 0:
            tab = page.locator(f'button:has-text("{tab_text}")').first
        tab.click(timeout=4000)
        wait(page)
        return True
    except Exception as e:
        print(f'      ⚠ 탭 클릭 실패 ({tab_text}): {e}')
        return False

def get_nav(page):
    return page.evaluate("""
        () => {
            const sels = ['nav a','aside a','[class*=sidebar] a','[class*=Sidebar] a',
                          '[class*=SideNav] a','[class*=sidenav] a',
                          '[class*=menu] a','[class*=Menu] a',
                          '[class*=nav] a','[class*=Nav] a'];
            for (const sel of sels) {
                const items = Array.from(document.querySelectorAll(sel))
                    .map(e=>({text:e.textContent?.trim(), href:e.href||e.getAttribute('href')||''}))
                    .filter(x=>x.text&&x.text.length>1&&x.text.length<80);
                if (items.length>=3) return {selector:sel, items:items.slice(0,30)};
            }
            const all = Array.from(document.querySelectorAll('a'))
                .map(e=>({text:e.textContent?.trim(), href:e.href||''}))
                .filter(x=>x.text&&x.text.length>1&&x.text.length<60);
            return {selector:'a (fallback)', items:all.slice(0,20)};
        }
    """)

def add_screen(name, page, ss_path, parent=None):
    s = structure(page)
    tabs = get_tabs(page)
    entry = {
        'name': name,
        'url': page.url,
        'screenshot': ss_path,
        'structure': s,
        'tabs': [t['text'] for t in tabs],
        'parent': parent,
    }
    screens.append(entry)
    print(f'      ✓ Headings: {s["headings"][:4]}')
    if s['table_headers']:
        print(f'      ✓ Table: {s["table_headers"][:6]}')
    if tabs:
        print(f'      ✓ Tabs: {[t["text"] for t in tabs]}')
    return entry


# ── 메인 ──────────────────────────────────────

def main():
    print('='*60)
    print('  Auxia Console — Web Vision Analyzer (Deep Mode)')
    print('='*60)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir='/tmp/wva-auxia-v3',
            headless=False,
            viewport={'width': 1280, 'height': 900},
        )
        page = browser.pages[0] if browser.pages else browser.new_page()

        print(f'\n[접속] {TARGET_URL}')
        page.goto(TARGET_URL, wait_until='domcontentloaded', timeout=15000)
        time.sleep(2)

        # ── 로그인 대기 ──
        if not is_app_loaded(page):
            print('\n[로그인 필요] 브라우저 창에서 로그인 후 대기합니다...')
            for i in range(100):
                time.sleep(3)
                if is_app_loaded(page):
                    print(f'✅ 로그인 완료 ({(i+1)*3}s)')
                    break
                if i % 5 == 0:
                    print(f'  대기 중... {(i+1)*3}s')
            else:
                print('시간 초과'); browser.close(); return

        time.sleep(2)

        # ── GNB 메뉴 수집 ──
        nav = get_nav(page)
        menu_items = nav['items']
        print(f'\n[GNB] {len(menu_items)}개 메뉴 감지 ({nav["selector"]})')

        # ── Step 1: 홈 대시보드 ──
        print('\n━━━ [1] Home — 대시보드')
        ss = shot(page, '01_home_dashboard')
        add_screen('Home / Dashboard', page, ss)

        # ── Step 2: 각 GNB 메뉴 순회 ──
        visited = {page.url}
        menu_count = 0

        for item in menu_items[:10]:
            href = item['href']
            text = item['text']
            if not href or href in visited:
                continue
            if 'console.auxia.app' not in href and href.startswith('http'):
                continue

            menu_count += 1
            print(f'\n━━━ [{menu_count+1}] {text}')

            try:
                page.goto(href, wait_until='domcontentloaded', timeout=10000)
                wait(page)
                visited.add(page.url)

                # ── 2-A: 메뉴 메인 화면 캡쳐 ──
                safe_menu = f'{menu_count:02d}_{text}'
                ss_main = shot(page, safe_menu)
                entry = add_screen(text, page, ss_main)

                # ── 2-B: 탭이 있으면 각 탭 클릭 ──
                tabs = get_tabs(page)
                if tabs:
                    print(f'    → 탭 {len(tabs)}개 발견, 순환 탐색')
                    for tab_idx, tab in enumerate(tabs):
                        tab_text = tab['text']
                        if tab.get('selected'):
                            print(f'    [탭 {tab_idx+1}/{len(tabs)}] {tab_text} (이미 활성)')
                            continue

                        print(f'    [탭 {tab_idx+1}/{len(tabs)}] {tab_text}')
                        if click_tab(page, tab_text):
                            safe_tab = f'{menu_count:02d}_{text}_tab_{tab_text}'
                            ss_tab = shot(page, safe_tab)
                            add_screen(f'{text} > {tab_text}', page, ss_tab, parent=text)

                # ── 2-C: 테이블 행이 있으면 첫 번째 행 클릭 (1 depth) ──
                # 행 클릭 가능한 요소 탐지
                row_links = page.evaluate("""
                    () => {
                        // 테이블 행 내의 클릭 가능한 링크/버튼
                        const rows = Array.from(document.querySelectorAll('tr td a, tr td button'));
                        return rows.slice(0, 3).map(e => ({
                            text: e.textContent?.trim(),
                            tag: e.tagName,
                            href: e.href || '',
                        })).filter(x => x.text && x.text.length > 0);
                    }
                """)
                if row_links:
                    first = row_links[0]
                    print(f'    → 행 클릭 탐색: "{first["text"]}"')
                    try:
                        if first['href'] and 'console.auxia.app' in first['href']:
                            page.goto(first['href'], wait_until='domcontentloaded', timeout=8000)
                        else:
                            page.locator(f'tr td >> text="{first["text"]}"').first.click(timeout=4000)
                        wait(page)
                        safe_row = f'{menu_count:02d}_{text}_detail'
                        ss_row = shot(page, safe_row)
                        add_screen(f'{text} > {first["text"]} (상세)', page, ss_row, parent=text)
                        page.go_back()
                        wait(page)
                    except Exception as e:
                        print(f'      ⚠ 행 클릭 스킵: {e}')

            except Exception as e:
                print(f'    ⚠ 메뉴 스킵: {e}')

        # ── 결과 저장 ──
        result = {
            'service_url': TARGET_URL,
            'analysis_date': DATE,
            'nav': nav,
            'screens': screens,
            'total': len(screens),
        }
        with open(OUT / 'analysis_manifest.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f'\n{"="*60}')
        print(f'✅ 분석 완료! 총 {len(screens)}개 화면')
        print(f'   스크린샷 → output/screenshots/')
        print(f'   매니페스트 → output/analysis_manifest.json')
        browser.close()

if __name__ == '__main__':
    main()
