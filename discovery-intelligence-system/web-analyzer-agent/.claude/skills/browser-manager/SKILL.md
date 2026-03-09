# browser-manager — Playwright 제어 스킬

## 역할

Playwright를 이용해 브라우저를 제어한다.
캡쳐, 클릭, 스크롤, 로그인 대기 등 모든 브라우저 인터렉션을 담당.

---

## 사전 조건

```bash
pip install playwright pillow
playwright install chromium
```

환경변수:
- `WVA_SCREENSHOTS_DIR`: 스크린샷 저장 경로 (기본값: `output/screenshots/`)
- `WVA_USER_DATA_DIR`: Persistent 컨텍스트 데이터 경로 (기본값: `/tmp/wva-browser-profile`)

---

## 함수 목록

### `capture_full_page(page, name: str) → str`
전체 페이지를 스크롤하며 캡쳐. 고유 ID로 저장 후 경로 반환.

**파일명 규칙**: `{YYYYMMDD}_{순번:03d}_{name}.png`

### `capture_element(page, selector: str, name: str) → str`
특정 CSS selector 또는 XPath로 요소를 크롭 캡쳐.

### `interactive_pause(page, message: str) → None`
브라우저를 열어두고 사용자 입력을 대기한다.
콘솔에 `message`를 출력하고 `input()` 호출로 대기.

### `extract_gnb(page) → list[dict]`
메인 네비게이션(GNB) 항목 추출. `[{"text": "...", "href": "...", "selector": "..."}]` 형식 반환.

### `click_and_wait(page, selector: str, timeout_ms: int = 5000) → bool`
요소 클릭 후 네트워크 안정화 대기. 타임아웃 초과 시 `False` 반환.

### `detect_login_required(page) → dict`
현재 화면의 로그인 필요 여부 판단.
반환: `{"required": bool, "type": "none|form|google_oauth|unknown"}`

---

## 호출 예시

```python
# CLAUDE.md에서 스킬 호출 시 스크립트 직접 실행
python3 discovery-intelligence-system/web-analyzer-agent/.claude/skills/browser-manager/scripts/playwright_tools.py \
  --action capture_full_page \
  --url {현재_URL} \
  --output output/screenshots/
```

## 스크립트 위치

`scripts/playwright_tools.py`
