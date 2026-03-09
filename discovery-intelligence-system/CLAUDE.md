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
| 분석 모드 | `--mode competitor` / `--mode reference` (기본값: competitor) | 선택 |
| 입력 데이터 | `--input {폴더경로}` — 로컬 파일(CSV/md/png) 제공 시 | 선택 |
| 이니셔티브 참조 | TM-XXXX 또는 이니셔티브 이름 | 선택 |
| 타겟 사용자 힌트 | 연령대, 직군, 사용 맥락 등 | 선택 |
| 핵심 가설 | PM이 검증하고 싶은 가정 목록 | 선택 |
| 인터뷰 수 | 가상 인터뷰 목표 건수 (기본값: 5건) | 선택 |

**탐색 주제가 없을 경우** 작업을 중단하고 재확인:
> "어떤 문제나 시장을 탐색할까요? 예: '한국 패션 리셀 시장의 화이트스페이스' 또는 '무신사 앱 내 스타일링 기능 사용 행태'"

---

## 1-A. 분석 모드 결정

**두 가지 모드**로 분기한다. 명시 없으면 입력 내용으로 자동 판단.

| 모드 | 트리거 | 담당 에이전트 |
|------|--------|------------|
| **Competitor** | "경쟁사 비교", "시장 조사", "화이트스페이스", 기본값 | `market-analyst` |
| **Reference** | "벤치마킹", "레퍼런스 분석", "UX 패턴", "Best Practice" | `reference-explorer` |
| **Web Analysis** | "화면 분석", "UI 분석", "화면 설계서", "서비스 분석", URL 직접 입력 | `web-analyzer-agent` |

자동 판단이 모호하면 사용자에게 확인:
> "경쟁사 비교 분석(Competitor)과 레퍼런스/UX 패턴 분석(Reference) 중 어떤 모드로 진행할까요?"

---

## 1-B. 입력 데이터 스캔 (--input 옵션 있을 때)

`--input {폴더}` 옵션이 있으면 파일을 먼저 분류하고 `data-processor` 스킬을 호출한다:

```
input/ 폴더 스캔
├── *.csv        → sentiment-aggregator.py 호출 (리뷰/평점 데이터)
├── *.md / *.txt → 직접 컨텍스트로 로드
└── *.png / *.jpg → 이미지 메타데이터 추출 + 스크린샷 설명 요청
```

분류 결과를 `output/input_manifest.json`에 저장 후 해당 에이전트에 전달.

---

## 2. 이니셔티브 컨텍스트 로딩

사용자 입력에 TM-XXXX 또는 이니셔티브 키워드가 포함되면:
1. `../input/initiatives/index.md`에서 매칭 이니셔티브를 찾는다.
2. 해당 이니셔티브의 `context.md`와 `references.json`을 읽어 배경 가설을 파악한다.
3. 로딩된 컨텍스트를 Phase 1 시장 분석의 출발점으로 사용한다.
4. 최종 산출물은 해당 이니셔티브의 `output/` 폴더에도 복사한다.

---

## 3. 전체 워크플로우

### Competitor Mode (기본)
```
PM 요청 (탐색 주제 + 가설 + 옵션)
        │
        ▼
[1-A/B: 모드 결정 + 입력 파일 스캔]
   → --input 있으면 data-processor 스킬 먼저 실행
        │
        ▼
[Phase 0: 외부 지식 수집] ──▶ discovery-analyst  ← --ref 옵션 있을 때만
        │
        ├─ Amplitude / Braze / Shopify 레퍼런스 수집
        │ 출력: output/ext_summary_{YYYYMMDD}_{주제}.md
        ▼
[Phase 1: 시장 분석] ──▶ market-analyst (3개 분석 병렬 실행)
        │
        ├─ [Agent A] Sentiment 분석 — 리뷰/평점 데이터 감정 집계
        ├─ [Agent B] Feature/Pricing 매트릭스 — 기능·가격 비교표
        └─ [Agent C] Strategic Context — 화이트스페이스·TAM/SAM/SOM
        │
        ├─ 교차 검증: A/B/C 결과 간 모순 감지 및 조정
        │ 출력: output/market-intel.md
        ▼
[Phase 2: 페르소나 생성] ──▶ market-analyst
        │ 출력: personas/{persona-id}.json
        ▼
[Phase 3: 가상 인터뷰] ──▶ user-simulator (페르소나 수만큼 반복)
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
        │ 출력: output/FINAL-DISCOVERY-REPORT.md
        ▼
[PM 리뷰 & HITL 루프]
```

### Reference Mode (`--mode reference`)
```
PM 요청 (벤치마킹 대상 + 분석 포인트)
        │
        ▼
[1-A/B: 모드 결정 + 입력 파일 스캔]
        │
        ▼
[Phase 0: 외부 지식 수집] ──▶ discovery-analyst (--ref 옵션 있을 때)
        │
        ▼
[Phase R: 레퍼런스 분석] ──▶ reference-explorer
        │
        ├─ Best Practice 패턴 추출
        ├─ UI/UX 구현 방식 요약
        ├─ 도입 시 고려사항 및 리스크
        └─ 자사 적용 시 Gap 분석
        │ 출력: output/reference-report_{YYYYMMDD}_{주제}.md
        ▼
[PM 리뷰 & 적용 방안 논의]
```

### Web Analysis Mode (`--mode web-analysis`)
```
PM 요청 (대상 URL + 탐색 옵션)
        │
        ▼
[1-C: 모드 결정]
  → URL 유무 확인, 탐색 깊이(--depth) 파싱
        │
        ▼
[Phase W: 웹 화면 분석] ──▶ web-analyzer-agent (CLAUDE.md)
        │
        ├─ 브라우저 초기화 (Playwright)
        ├─ 로그인 상태 판단 + Semi-Auto 처리
        ├─ GNB 추출 + 순환 탐색
        ├─ Vision 분석 (화면별)
        └─ 화면 설계서 합성 (documenter)
        │ 출력: web-analyzer-agent/output/screen_spec.md
        │       web-analyzer-agent/output/screenshots/*.png
        ▼
[PM 리뷰 & (선택) Reference 분석 연결]
  → `/discovery --mode reference --input web-analyzer-agent/output/screenshots/` 연계 가능
```

---

## 4. Phase별 에이전트 호출 규약

### Phase 0 — discovery-analyst 호출 (--ref 옵션 있을 때만)

```
Task: 아래 탐색 주제에 대한 외부 벤더 레퍼런스를 수집하고 Phase 0 요약을 생성해줘.

탐색 주제: {사용자_탐색_주제}
이니셔티브 컨텍스트: {context.md 내용 또는 "없음"}
외부 참조 범위: {--ref 옵션값: all | amplitude | braze | shopify}

references/vendor_endpoints.json의 routing_rules를 참조하여 관련 벤더를 자동 선택하고,
scripts/ 폴더의 fetch_amplitude.py / fetch_braze.py / search_shopify.py를 호출할 것.

결과를 output/ext_summary_{YYYYMMDD}_{주제}.md에 저장할 것.
```

### Phase 1 — market-analyst 호출 (Competitor Mode)

```
Task: 아래 탐색 주제에 대한 시장 분석을 수행해줘.

탐색 주제: {사용자_탐색_주제}
이니셔티브 컨텍스트: {context.md 내용 또는 "없음"}
외부 벤더 레퍼런스: {output/ext_summary_*.md 경로 또는 "없음 — Phase 0 스킵됨"}
로컬 데이터: {output/input_manifest.json 경로 또는 "없음"}

수행 범위 (3개 분석 병렬 실행 후 교차 검증):
[Agent A] Sentiment: 리뷰/평점 CSV 기반 주요 불만·강점 감정 분석
[Agent B] Feature/Pricing: 기능 비교 매트릭스 + 가격 정책 비교표
[Agent C] Strategic: TAM/SAM/SOM + 화이트스페이스 도출

교차 검증: A/B/C 결과에 모순이 있으면 조정 근거를 명시하고 합의된 내용으로 작성.

결과를 output/market-intel.md에 저장할 것.
```

### Phase R — reference-explorer 호출 (Reference Mode)

```
Task: 아래 벤치마킹 대상의 레퍼런스 분석을 수행해줘.

탐색 주제: {사용자_탐색_주제}
분석 포인트: {PM이 파악하려는 기능/UX/전략 포인트}
입력 데이터: {output/input_manifest.json 또는 "없음"}
외부 레퍼런스: {output/ext_summary_*.md 경로 또는 "없음"}

수행 범위:
1. Best Practice 패턴 추출 (업계 표준 구현 방식)
2. UI/UX 패턴 요약 (스크린샷 또는 텍스트 기반)
3. 도입 시 고려사항 및 예상 리스크
4. 자사 현황 대비 Gap 분석

결과를 output/reference-report_{YYYYMMDD}_{주제}.md에 저장할 것.
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
| 모드 판단 불가 | 사용자에게 Competitor / Reference 선택 요청 |
| 분류 불가 파일 (`--input`) | 사용자에게 파일 용도 문의 후 진행 |
| CSV 파싱 오류 | data-processor 1회 재시도, 실패 시 파일 경로 안내 + 수동 확인 요청 |
| 매트릭스 필수 항목 누락 | 누락 항목 재추출 자동 재시도 (최대 2회) |
| 교차 검증 모순 | 모순 내용과 조정 근거를 보고서에 명시 ("데이터 충돌 — A 근거 채택") |
| 화이트스페이스 3개 미만 | "분석 범위 내 공백 부족" 명시 + 탐색 범위 확장 제안 |
| 시장 데이터 부족 | "공개 데이터 한계 명시 후 Conservative 추정값 사용, 가정 명시" |
| 페르소나 생성 0개 | 타겟 사용자 힌트 재요청 후 재실행 |
| 인터뷰 품질 낮음 (Yes-man 감지) | user-simulator에 재실행 지시 + 비판적 시각 강화 프롬프트 추가 |
| JTBD 도출 불가 | insight-synthesizer에 인터뷰 추가 요청 (Phase 3 부분 재실행) |
| 보고서 통합 오류 | 해당 섹션 누락 표시 후 나머지 섹션으로 보고서 완성 |
