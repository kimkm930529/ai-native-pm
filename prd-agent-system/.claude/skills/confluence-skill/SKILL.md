# Confluence Skill — PRD Builder용 호출 규약

## 개요

기존 `pm-studio` 프로젝트의 Confluence 스크립트를 재사용하여
PRD 작성을 위한 배경 자료를 검색하고, 완성된 PRD를 Confluence에 업로드한다.

---

## 스크립트 위치

```
/Users/musinsa/Documents/agent_project/pm-studio/
└── .claude/skills/confluence-tool/scripts/
    ├── client.py    # 공통 인증/통신 (자동 1회 재시도)
    ├── search.py    # CQL 기반 문서 검색
    └── upload.py    # 페이지 생성 및 업데이트
```

상세 사용법: `/Users/musinsa/Documents/agent_project/pm-studio/.claude/skills/confluence-tool/SKILL.md` 참조

---

## 필수 환경변수

| 변수명 | 설명 |
|--------|------|
| `CONFLUENCE_URL` | `https://musinsa-oneteam.atlassian.net` |
| `CONFLUENCE_EMAIL` | Atlassian 계정 이메일 |
| `CONFLUENCE_API_TOKEN` | Atlassian API 토큰 |

---

## search.py 호출 규약

**실행 위치:** 반드시 `pm-studio/` 루트에서 실행 (config/spaces.json 경로 의존)

```bash
cd /Users/musinsa/Documents/agent_project/pm-studio && \
python3 .claude/skills/confluence-tool/scripts/search.py \
  --query "{PRD 주제 관련 키워드}" \
  [--space SPACE_KEY] \
  [--limit 10]
```

**PRD Builder 사용 패턴:**
- `--space` 미지정 → `config/spaces.json`의 priority 순서대로 전체 검색 (배경 자료 수집)
- `--space membership` → 멤버십 팀 Space만 검색
- `--space PE` → PE Space만 검색

**출력:**
- stdout: JSON 형식 검색 결과
- 파일: `output/context.json` (pm-studio/output/ 기준)

---

## upload.py 호출 규약

PRD 초안을 `output/draft.html`에 저장한 후 실행.

```bash
cd /Users/musinsa/Documents/agent_project/pm-studio && \
python3 .claude/skills/confluence-tool/scripts/upload.py \
  --title "[{YYYYMM}] {기능명} PRD" \
  --space ~7120209bbd1f66a6e34385957b56995ea34f89
```

**기본 업로드 대상 Space:**
- Space Key: `~7120209bbd1f66a6e34385957b56995ea34f89` (개인 Space)
- Parent Folder: `개인 노트`

**성공 출력 예시:**
```
[CREATE] 페이지 생성 완료
URL: https://musinsa-oneteam.atlassian.net/wiki/spaces/~712.../pages/123456
```

---

## PRD → XHTML 변환 규칙

`upload.py` 실행 전 PRD Markdown을 `output/draft.html`에 XHTML로 변환:

```xml
<!-- 마크다운 → XHTML 변환 규칙 -->
# 제목        → <h1>제목</h1>
## 소제목     → <h2>소제목</h2>
**볼드**      → <strong>볼드</strong>
| 표 |        → <table><tbody>...</tbody></table>
- 항목        → <ul><li>항목</li></ul>
```

**Mermaid 차트 처리:** `output/draft.html`에는 Mermaid 코드를 코드 블록으로 포함:
```xml
<ac:structured-macro ac:name="code">
  <ac:parameter ac:name="language">mermaid</ac:parameter>
  <ac:plain-text-body><![CDATA[
  flowchart TD
      ...
  ]]></ac:plain-text-body>
</ac:structured-macro>
```

**페이지 하단 필수 추가:**
```xml
<hr/>
<p><em>이 페이지는 PRD Builder Agent에 의해 자동 생성되었습니다. ({YYYY-MM-DD})</em></p>
```

---

## 오류 처리

| 오류 코드 | 원인 | 처리 방법 |
|----------|------|----------|
| 401 | API 토큰 만료 또는 오류 | "Confluence API 토큰을 확인해주세요." 후 중단 |
| 404 | Space 키 미존재 | Space Key 재확인 요청 |
| 검색 0건 | 관련 문서 없음 | 오케스트레이터에 보고 → 키워드 수정 후 재시도 |
| 업로드 실패 | 네트워크 또는 포맷 오류 | `output/draft.html` 경로 안내 + 수동 업로드 안내 |
