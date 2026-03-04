# /discovery — Product Discovery Intelligence 에이전트

## 사용법

```
/discovery [탐색 주제] [이니셔티브 참조(선택)] [타겟 사용자 힌트(선택)]
```

## 실행 규칙

1. `discovery-intelligence-system/CLAUDE.md`를 읽어 에이전트 역할과 전체 워크플로우를 파악한다.
2. 사용자가 제공한 args를 파싱한다:
   - 탐색 주제가 없으면 시장/제품 도메인과 해결하려는 문제를 사용자에게 요청한다.
   - `TM-XXXX` 형식이 포함되면 `initiatives/` 폴더에서 해당 이니셔티브 컨텍스트를 로드한다.
3. CLAUDE.md에 정의된 워크플로우(시장 분석 → 가상 인터뷰 → 인사이트 합성 → 보고서 생성)를 그대로 따라 실행한다.
