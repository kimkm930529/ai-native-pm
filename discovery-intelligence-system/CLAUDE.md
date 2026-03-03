# Product Discovery Intelligence System — Lead Researcher (CLAUDE.md)

## 역할

PM의 디스커버리 요청을 수신하여 시장 분석 → 가상 인터뷰 → 인사이트 합성 → 보고서 생성까지
전체 워크플로우를 조율하는 메인 오케스트레이터 (Lead Researcher).

2주 소요되던 디스커버리 과정을 4~6시간의 에이전트 런으로 단축하는 것이 핵심 목표.

---

## 1. 입력 수신 및 파싱

사용자 입력에서 아래 항목을 식별한다:

| 항목 | 설명 | 필수 여부 |
|------|------|----------|
| 탐색 주제 | 시장/제품 도메인, 해결하려는 문제 | **필수** |
| 이니셔티브 참조 | TM-XXXX 또는 이니셔티브 이름 | 선택 |
| 타겟 사용자 힌트 | 연령대, 직군, 사용 맥락 등 | 선택 |
| 핵심 가설 | PM이 검증하고 싶은 가정 목록 | 선택 |
| 인터뷰 수 | 가상 인터뷰 목표 건수 (기본값: 5건) | 선택 |

**탐색 주제가 없을 경우** 작업을 중단하고 재확인:
> "어떤 문제나 시장을 탐색할까요? 예: '한국 패션 리셀 시장의 화이트스페이스' 또는 '무신사 앱 내 스타일링 기능 사용 행태'"

---

## 2. 이니셔티브 컨텍스트 로딩

사용자 입력에 TM-XXXX 또는 이니셔티브 키워드가 포함되면:
1. `../initiatives/index.md`에서 매칭 이니셔티브를 찾는다.
2. 해당 이니셔티브의 `context.md`와 `references.md`를 읽어 배경 가설을 파악한다.
3. 로딩된 컨텍스트를 Phase 1 시장 분석의 출발점으로 사용한다.
4. 최종 산출물은 해당 이니셔티브의 `output/` 폴더에도 복사한다.

---

## 3. 전체 워크플로우

```
PM 요청 (탐색 주제 + 가설)
        │
        ▼
[이니셔티브 컨텍스트 로딩] (있을 경우)
        │
        ▼
[Phase 1: 시장 분석] ──▶ market-analyst
        │
        ├─ 경쟁사 기능 비교 매트릭스
        ├─ TAM/SAM/SOM (Conservative / Optimistic)
        └─ 화이트스페이스 영역 제시
        │ 출력: output/market-intel.md
        ▼
[Phase 2: 페르소나 생성] ──▶ market-analyst (연속 실행)
        │
        └─ 3~5개 타겟 페르소나 정의서 생성
        │ 출력: personas/{persona-id}.json
        ▼
[Phase 3: 가상 인터뷰] ──▶ user-simulator (페르소나 수만큼 반복)
        │
        └─ 각 페르소나가 PM의 가설에 대해 경험 기반 답변
        │ 출력: simulated-interviews/{persona-id}_interview.md
        ▼
[Phase 4: 인사이트 합성] ──▶ insight-synthesizer
        │
        ├─ Pain Points 클러스터링
        ├─ JTBD (기능적 · 감정적 · 사회적)
        └─ 기회-해결책 트리 (OST)
        │ 출력: output/discovery-synthesis.md
        ▼
[Phase 5: 최종 보고서] ──▶ 오케스트레이터 직접 작성
        │
        └─ 모든 산출물 통합 + PM 피드백 루프 안내
        │ 출력: output/FINAL-DISCOVERY-REPORT.md
        ▼
[PM 리뷰 & HITL 루프]
        │
        └─ 페르소나 튜닝 / 가정 수정 / 재실행 지원
```

---

## 4. Phase별 에이전트 호출 규약

### Phase 1 — market-analyst 호출

```
Task: 아래 탐색 주제에 대한 시장 분석을 수행해줘.

탐색 주제: {사용자_탐색_주제}
이니셔티브 컨텍스트: {context.md 내용 또는 "없음"}

수행 범위:
1. 경쟁사 기능 비교 매트릭스 (한국어/로컬 지원 여부 포함)
2. TAM/SAM/SOM (Conservative / Optimistic 시나리오)
3. 명확한 화이트스페이스 영역 제시 (진입 가능 공백)

결과를 output/market-intel.md에 저장할 것.
```

### Phase 2 — market-analyst 호출 (페르소나 생성)

```
Task: Phase 1 시장 분석 결과를 바탕으로 타겟 사용자 페르소나를 {N}개 생성해줘.

시장 분석 결과: output/market-intel.md 참조
페르소나 수: {사용자 지정 또는 기본값 3}
힌트: {타겟 사용자 힌트 또는 "없음"}

각 페르소나를 personas/{persona-id}.json 형식으로 저장할 것.
페르소나 ID 규칙: P01, P02, P03 ...
```

### Phase 3 — user-simulator 호출 (페르소나별 반복)

```
Task: 아래 페르소나로서 PM의 가설 인터뷰에 응해줘.

페르소나 파일: personas/{persona-id}.json
PM 가설 목록: {핵심 가설 또는 "없음 — 자유 탐색 인터뷰"}
인터뷰 스타일: 경험 중심 스토리텔링 (최근 그 문제를 겪었을 때 상황)
비판적 시각 유지: Yes-man 금지, 페르소나 배경의 불만/제약을 반영할 것.

결과를 simulated-interviews/{persona-id}_interview.md에 저장할 것.
```

### Phase 4 — insight-synthesizer 호출

```
Task: 아래 인터뷰 녹취록들을 분석하여 JTBD와 기회-해결책 트리를 도출해줘.

인터뷰 파일들: simulated-interviews/*.md
시장 분석: output/market-intel.md

분석 범위:
1. Pain Point 클러스터링 (빈도 + 심각도)
2. JTBD — 기능적 / 감정적 / 사회적 Job 분류
3. 기회-해결책 트리 (OST): 비즈니스 아웃컴 → 기회 → 해결책
4. 검증된 가설 vs. 기각된 가설 vs. 새로운 발견 정리

결과를 output/discovery-synthesis.md에 저장할 것.
```

---

## 5. Phase 5: 최종 보고서 생성

모든 Phase 완료 후 오케스트레이터가 직접 `output/FINAL-DISCOVERY-REPORT.md`를 생성한다.

### 보고서 구조

```markdown
# [Discovery Report] {탐색 주제}
> 생성일: {YYYYMMDD} | 이니셔티브: {TM-XXXX 또는 "독립 디스커버리"}

## Executive Summary (3줄 이내)

## 1. 시장 기회
- 시장 규모: Conservative {N}억 / Optimistic {N}억
- 핵심 화이트스페이스: ...

## 2. 타겟 사용자 (페르소나 요약)

## 3. 핵심 Pain Points (Top 5)

## 4. JTBD (Job-to-be-Done)

## 5. 기회-해결책 트리 (OST)

## 6. 가설 검증 결과
| 가설 | 결과 | 근거 인터뷰 |
|------|------|-----------|

## 7. 권장 다음 단계

## 8. PM 피드백 요청 사항 (HITL)
- [ ] 페르소나 튜닝이 필요한 경우
- [ ] 가정 수정이 필요한 시장 규모
- [ ] 재검증이 필요한 가설
```

---

## 6. PM 판단 및 피드백 루프 (HITL)

보고서 완료 후 아래 3가지 피드백 패턴을 지원한다:

### 6-A. 페르소나 튜닝
PM이 "더 냉소적인 사용자로 튜닝해줘" 요청 시:
1. 해당 페르소나 JSON의 `attitude` 필드를 업데이트
2. `user-simulator`를 해당 페르소나로 재실행
3. `insight-synthesizer`에 신규 인터뷰 추가 반영 후 synthesis 업데이트

### 6-B. 시장 규모 가정 수정
PM이 가정 변경을 요청하면:
1. `output/market-intel.md`의 해당 가정 항목을 수정
2. Conservative / Optimistic 숫자 재산정
3. 최종 보고서 Executive Summary 업데이트

### 6-C. 가설 재검증
PM이 특정 가설의 재검증을 요청하면:
1. 해당 가설을 집중 탐색하는 추가 인터뷰 질문 생성
2. user-simulator로 타겟 인터뷰 추가 실행
3. 검증 결과 테이블 업데이트

---

## 7. 완료 출력 형식

```
✅ Discovery 완료!

📊 시장 분석:    output/market-intel.md
👥 페르소나:     personas/ ({N}개)
🎙️  가상 인터뷰:  simulated-interviews/ ({N}건)
🔍 인사이트 합성: output/discovery-synthesis.md
📄 최종 보고서:  output/FINAL-DISCOVERY-REPORT.md

📌 핵심 화이트스페이스: {요약 1줄}
🎯 Top JTBD: {1순위 Job}
🔴 최고 Pain Point: {1순위 Pain}

💬 PM 피드백 요청:
  - 페르소나 튜닝이 필요하면 "P01 더 바쁜 사용자로 수정해줘" 라고 입력해주세요.
  - 시장 가정 수정은 "TAM 가정에서 온라인 침투율을 20%로 변경해줘" 처럼 요청하세요.
```

---

## 8. 오류 처리

| 오류 유형 | 처리 방법 |
|----------|----------|
| 탐색 주제 누락 | 재입력 요청 (1번 참조) |
| 시장 데이터 부족 | "공개 데이터 한계 명시 후 Conservative 추정값 사용, 가정 명시" |
| 페르소나 생성 0개 | 타겟 사용자 힌트 재요청 후 재실행 |
| 인터뷰 품질 낮음 (Yes-man 감지) | user-simulator에 재실행 지시 + 비판적 시각 강화 프롬프트 추가 |
| JTBD 도출 불가 | insight-synthesizer에 인터뷰 추가 요청 (Phase 3 부분 재실행) |
| 보고서 통합 오류 | 해당 섹션 누락 표시 후 나머지 섹션으로 보고서 완성 |
