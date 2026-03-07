# slack-notifier — Skill Spec

## 역할

생성된 Slack 요약 텍스트를 Slack Webhook으로 전송하거나, 터미널에 포맷 출력하는 스킬.
`SLACK_WEBHOOK_URL` 환경변수 설정 여부에 따라 자동으로 전송 모드를 결정한다.

---

## 트리거 조건

`minutes-generator` 에이전트가 `output/slack_summary_{YYYYMMDD}.txt` 생성을 완료했을 때 호출.

---

## 스크립트

```
.claude/skills/slack-notifier/scripts/send_slack.py
```

---

## 호출 방법

```bash
python3 .claude/skills/slack-notifier/scripts/send_slack.py \
  --input output/slack_summary_{YYYYMMDD}.txt
```

### 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--input` | 전송할 텍스트 파일 경로 (필수) | — |
| `--webhook-url` | Slack Webhook URL (미지정 시 환경변수 사용) | `$SLACK_WEBHOOK_URL` |
| `--dry-run` | 실제 전송 없이 터미널 출력만 수행 | false |
| `--channel` | 채널 오버라이드 (Webhook URL에 채널이 고정된 경우 무시됨) | — |

---

## 동작 모드

### 모드 1: Webhook 전송 (자동)
`SLACK_WEBHOOK_URL` 환경변수가 설정된 경우:
- Incoming Webhook으로 POST 요청
- 성공: `{"ok": true}` 응답 확인 후 완료 메시지 출력
- 실패: 에러 코드와 함께 모드 2로 폴백

### 모드 2: 터미널 출력 (dry-run / 폴백)
`SLACK_WEBHOOK_URL` 미설정 또는 `--dry-run` 플래그 지정 시:
- 터미널에 포맷된 텍스트 출력
- 수동 복사 안내 메시지 포함

---

## 환경변수

| 변수명 | 용도 |
|--------|------|
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL |

---

## 출력 예시

### 전송 성공 시
```
[slack-notifier] Slack 전송 완료
채널: #{channel}
메시지 미리보기:
---
📢 [차주 아젠다 요약]
• ...
---
```

### dry-run / 폴백 시
```
[slack-notifier] SLACK_WEBHOOK_URL 미설정 — 터미널 출력 모드

=== Slack 복사용 텍스트 ===
📢 [차주 아젠다 요약]
• ...
===========================
위 내용을 Slack에 직접 붙여넣어 주세요.
```

---

## 오류 처리

| 오류 유형 | 처리 |
|----------|------|
| 파일 없음 | "입력 파일을 찾을 수 없습니다: {path}" 후 종료 |
| Webhook 403/404 | "Webhook URL이 유효하지 않습니다." 후 터미널 출력 모드로 폴백 |
| Webhook 500 | "Slack 서버 오류. 잠시 후 재시도하거나 수동으로 전송해주세요." 후 터미널 출력 모드로 폴백 |
| 네트워크 오류 | "네트워크 연결을 확인해주세요." 후 터미널 출력 모드로 폴백 |
