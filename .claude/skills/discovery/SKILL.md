# /discovery — Product Discovery Intelligence 에이전트

## 사용법

```
/discovery [탐색 주제] [옵션]

옵션:
  --ref all          외부 벤더 레퍼런스 전체 수집 (Amplitude + Braze + Shopify 자동 선택)
  --ref amplitude    Amplitude GitHub Docs만 수집
  --ref braze        Braze GitHub Docs만 수집
  --ref shopify      Shopify App Store 벤치마크만 수집
  --initiative TM-XXXX  이니셔티브 컨텍스트 로드
```

## 실행 규칙

1. `discovery-intelligence-system/CLAUDE.md`를 읽어 에이전트 역할과 전체 워크플로우를 파악한다.
2. 사용자가 제공한 args를 파싱한다:
   - 탐색 주제가 없으면 시장/제품 도메인과 해결하려는 문제를 사용자에게 요청한다.
   - `TM-XXXX` 형식이 포함되면 `input/initiatives/` 폴더에서 해당 이니셔티브 컨텍스트를 로드한다.
   - `--ref` 옵션이 있으면 Phase 0(외부 지식 수집)을 먼저 실행한다. 없으면 Phase 1부터 시작한다.
3. CLAUDE.md에 정의된 워크플로우를 그대로 따라 실행한다:
   - `--ref` 옵션 있음: Phase 0(외부 레퍼런스) → Phase 1~5(시장 분석 → 가상 인터뷰 → 인사이트 합성 → 보고서)
   - `--ref` 옵션 없음: Phase 1~5만 실행

## 예시

```
/discovery 무신사 앱 리텐션 향상을 위한 개인화 푸시 전략 --ref all
/discovery 패션 버티컬 커머스 상품 추천 화이트스페이스 --ref amplitude --initiative TM-2061
/discovery 한국 리셀 시장 분석 (외부 레퍼런스 없이 빠른 실행)
```
