# /gtm — GTM Brief Builder 에이전트

## 사용법

```
/gtm [PRD 파일 경로]
```

## 실행 규칙

1. `gtm-agent-system/CLAUDE.md`를 읽어 에이전트 역할과 전체 워크플로우를 파악한다.
2. 사용자가 제공한 args를 파싱한다:
   - 파일 경로가 지정되면 해당 PRD를 사용한다.
   - 경로가 없으면 `gtm-agent-system/input/` 폴더의 `prd_*.md` 파일을 자동 감지한다.
   - 파일도 없으면 사용자에게 PRD 내용을 직접 붙여넣도록 요청한다.
3. CLAUDE.md에 정의된 워크플로우를 그대로 따라 GTM 브리프를 생성한다.
