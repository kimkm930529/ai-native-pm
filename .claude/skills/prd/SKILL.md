# /prd — PRD 생성 에이전트

## 사용법

```
/prd [rough note 또는 이니셔티브 ID]
```

## 실행 규칙

1. `prd-agent-system/CLAUDE.md`를 읽어 에이전트 역할과 전체 워크플로우를 파악한다.
2. 사용자가 제공한 args를 **Rough Note**로 처리한다.
   - args가 없으면 사용자에게 기능 배경/해결 문제를 요청한다.
   - `TM-XXXX` 형식이면 `initiatives/` 폴더에서 해당 이니셔티브 컨텍스트를 먼저 로드한다.
3. CLAUDE.md에 정의된 워크플로우를 그대로 따라 PRD를 생성한다.
4. 산출물은 `prd-agent-system/output/prd_{YYYYMMDD}_{주제}.md`에 저장한다.
