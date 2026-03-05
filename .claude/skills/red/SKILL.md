# /red — Red Team Validator 에이전트

## 사용법

```
/red [PRD 파일 경로]
```

## 실행 규칙

1. `prd-agent-system/.claude/agents/red-team-validator/AGENT.md`를 읽어 에이전트 역할과 실행 순서를 파악한다.
2. 사용자가 제공한 args를 파싱하여 PRD 입력 방식을 결정한다:
   - **Confluence 파일 경로가 지정된 경우**: 해당 파일을 직접 읽어 마크다운으로 변환한 뒤 `prd-agent-system/.claude/agents/red-team-validator/input/`에 저장하고 검증을 진행한다.
   - **경로가 없는 경우**: `confluence-reader` 서브에이전트를 호출하여 관련 PRD를 검색·취득한 뒤 동일 `input/` 폴더에 저장한다. 검색 대상 키워드는 사용자 입력에서 추출하거나, 없으면 사용자에게 주제를 확인한다.
   - **`input/` 폴더에 이미 파일이 있는 경우**: 해당 파일을 재사용하고 사용자에게 어떤 파일을 쓰는지 알린다.
3. AGENT.md에 정의된 Step 0~5 실행 순서(입력 확보 → PRD 분석 → 가정 추출 → 9카테고리 질문 생성 → 우선순위 태깅 → 출력 저장)를 그대로 따라 실행한다.
4. 산출물은 `prd-agent-system/output/redteam_{YYYYMMDD}_{주제}.md`에 저장한다.
5. 완료 후 요약(질문 수, Critical/Important/Minor 분포, 상위 3개 Critical 질문)을 출력한다.
