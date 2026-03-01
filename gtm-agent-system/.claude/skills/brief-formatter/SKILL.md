# brief-formatter — Skill 호출 규약

## 개요

`messaging_draft.json`과 `strategy_draft.json` 두 JSON 파일을 `gtm_template.md` 구조에 맞춰 결합하여
최종 `GTM_Brief_YYYYMMDD_주제.md` 파일을 생성하는 마크다운 조립 스킬.

---

## 스크립트 호출 방법

```bash
python3 .claude/skills/brief-formatter/scripts/assemble.py \
  --messaging output/messaging_draft.json \
  --strategy  output/strategy_draft.json \
  --template  references/gtm_template.md \
  --output    output/GTM_Brief_{YYYYMMDD}_{주제}.md
```

### 파라미터

| 파라미터 | 필수 | 기본값 | 설명 |
|---------|------|--------|------|
| `--messaging` | ✅ | — | messaging_draft.json 경로 |
| `--strategy` | ✅ | — | strategy_draft.json 경로 |
| `--template` | ✅ | — | gtm_template.md 경로 |
| `--output` | ✅ | — | 최종 산출물 저장 경로 |
| `--dry-run` | ❌ | false | 파일 저장 없이 stdout만 출력 |

---

## 출력 (stdout)

성공 시:
```
[ASSEMBLE] GTM 브리프 생성 완료
파일: output/GTM_Brief_20260302_캠페인메타엔진.md
섹션: 8/8 완성
One-liner 길이: 38자 ✅
Before/After 테이블: 포함 ✅
Launch Metrics: 4개 ✅
```

실패 시:
```
[ERROR] messaging_draft.json 파싱 실패: 'one_liner' 키 없음
```

---

## 반환 코드

| 코드 | 의미 |
|------|------|
| `0` | 성공 — 파일 생성 완료 |
| `1` | JSON 파싱 오류 또는 필수 키 누락 |
| `2` | 템플릿 파일 없음 |
| `3` | 출력 디렉토리 접근 불가 |

---

## 섹션 매핑 규칙

`gtm_template.md`의 플레이스홀더와 JSON 키의 매핑:

| 템플릿 플레이스홀더 | 소스 | JSON 키 |
|------------------|------|---------|
| `{{ONE_LINER}}` | messaging | `one_liner` |
| `{{PERSONAS_TABLE}}` | messaging | `personas[]` → 마크다운 테이블 변환 |
| `{{BEFORE_AFTER_TABLE}}` | strategy | `before_after.table_md` |
| `{{PRIMARY_MESSAGE}}` | messaging | `key_message.primary` |
| `{{SUPPORTING_MESSAGES}}` | messaging | `key_message.supporting[]` |
| `{{PHASE1_LIMITATION}}` | messaging | `key_message.phase1_limitation` |
| `{{PHASE1_IN}}` | strategy | `scope.phase1_in[]` |
| `{{PHASE2_OUT}}` | strategy | `scope.phase2_out[]` |
| `{{ROLLOUT_TABLE}}` | strategy | `rollout_plan.table_md` |
| `{{ENABLEMENT_LIST}}` | strategy | `enablement.required[]` + `enablement.optional[]` |
| `{{LAUNCH_METRICS_TABLE}}` | strategy | `launch_metrics[]` → 마크다운 테이블 변환 |
| `{{GENERATED_DATE}}` | 자동 | 현재 날짜 (YYYY-MM-DD) |

---

## TBD 처리 규칙

JSON 값이 `null`, 빈 문자열(`""`), 빈 배열(`[]`)인 경우:
- 해당 섹션에 `> ⚠️ [TBD] 내용을 확인해주세요.` 삽입
- stdout에 경고 메시지 출력
- 반환 코드는 `0` (파일 생성은 완료)

---

## 오류 처리

1. JSON 파싱 실패 → 반환 코드 `1` + 오류 위치 stderr 출력
2. 템플릿 파일 없음 → 반환 코드 `2`
3. 출력 디렉토리 없음 → 자동 생성 후 재시도 (`mkdir -p`)
4. 필수 플레이스홀더 누락 → 해당 섹션 `[TBD]` 처리 후 완료
