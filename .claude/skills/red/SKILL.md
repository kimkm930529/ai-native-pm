# /red — Red Team Validator 에이전트

## 사용법

```
/red [PRD 파일 경로]
```

## 실행 규칙

1. `prd-agent-system/.claude/agents/red-team-validator/AGENT.md`를 읽어 에이전트 역할과 실행 순서를 파악한다.
2. 사용자가 제공한 args를 파싱한다:
   - 파일 경로가 지정되면 해당 PRD를 대상으로 검증을 수행한다.
   - 경로가 없으면 `prd-agent-system/output/` 폴더에서 가장 최근 `prd_*.md` 파일을 자동 선택한다.
   - 파일을 특정할 수 없으면 사용자에게 PRD 경로를 요청한다.
3. AGENT.md에 정의된 5단계 실행 순서(PRD 분석 → 가정 추출 → 9카테고리 질문 생성 → 우선순위 태깅 → 출력 저장)를 그대로 따라 실행한다.
4. 산출물은 `prd-agent-system/output/redteam_{YYYYMMDD}_{주제}.md`에 저장한다.
5. 완료 후 요약(질문 수, Critical/Important/Minor 분포, 상위 3개 Critical 질문)을 출력한다.
