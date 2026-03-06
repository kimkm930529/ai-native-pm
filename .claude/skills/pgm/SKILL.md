# /pgm — Weekly Flash Report 에이전트

## 사용법

```
/pgm [Jira 프로젝트 키] [메모 텍스트]
```

## 실행 규칙

1. `pgm-agent-system/CLAUDE.md`를 읽어 에이전트 역할과 전체 워크플로우를 파악한다.
2. args를 파싱하여 Jira 프로젝트 키와 메모 텍스트를 분리한다.
   - args가 없으면 사용자에게 Jira 프로젝트 키와 추가 메모를 요청한다.
   - 프로젝트 키 형식: `MATCH`, `CME`, `TM` 등 대문자 알파벳.
   - 메모 텍스트는 키 이후의 나머지 내용 전체로 처리한다.
3. CLAUDE.md에 정의된 워크플로우(Step 1~4)를 순서대로 실행한다.
4. 산출물은 `pgm-agent-system/output/flash_{YYYYMMDD}.md`에 저장한다.
