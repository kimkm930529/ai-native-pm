# Rec API (29CM 추천 API) 지식 베이스

> **최종 업데이트**: 2026-03-02
> **정리 기준**: 아래 4개 Confluence 문서를 학습하여 통합 정리. 내용 충돌 시 최신 문서 기준으로 변화 내용을 병기.

---

## 📚 출처 문서

| # | 제목 | Space | 버전 | 링크 |
|---|------|-------|------|------|
| 1 | REC API 메뉴얼 | 29CMRec | v4 | [바로가기](https://musinsa-oneteam.atlassian.net/wiki/spaces/29CMRec/pages/31283513) |
| 2 | Rec-API Global Routing 변경 가이드 (유관부서용) | 29CMRec | v2 | [바로가기](https://musinsa-oneteam.atlassian.net/wiki/spaces/29CMRec/pages/296750255) |
| 3 | PE Weekly — 2026-02-23 | PE | v21 | [바로가기](https://musinsa-oneteam.atlassian.net/wiki/spaces/PE/pages/312935926) |
| 4 | [29CM] 커스텀탭 개인화 rec-api 연동 | PE | v6 | [바로가기](https://musinsa-oneteam.atlassian.net/wiki/spaces/PE/pages/308543700) |

---

## 1. 개요

29CM Rec API는 **Step Function 기반 추천 API**로, MongoDB·Redis·S3 등 다양한 데이터 소스에서 추천 아이템을 조합·필터링하여 클라이언트에 제공하는 시스템입니다.

2026년 Global OneApp 출시를 계기로 **글로벌 라우팅** 기능이 추가되었으며, 기존 KR 전용 경로와 글로벌 경로가 병존하는 상태입니다.

---

## 2. API 엔드포인트

### 2.1 기존 경로 (KR 앱 — 현행 유지)

| 구분 | 엔드포인트 |
|------|-----------|
| 단일 실험 | `GET /rec/v3/{uuid}` |
| Facade (다중 실험) | `POST /rec/facade/v3` |

### 2.2 신규 경로 (글로벌 앱 전용 — 2026-02-03 도입)

| 구분 | 엔드포인트 |
|------|-----------|
| 단일 실험 | `GET /rec/context/v3/{uuid}` |
| Facade (다중 실험) | `POST /rec/context/facade/v3` |

#### 글로벌 경로 요청 파라미터

| 파라미터 | 필수 | 설명 | 예시 |
|---------|------|------|------|
| `countryCode` | Required | ISO 3166-1 alpha-2 국가 코드 | KR, JP, US, TW |
| `languageCode` | Required | BCP 47 언어 태그 | ko-KR, ja-JP, en-US, zh-TW |

**요청 예시:**
```
GET /rec/context/v3/base_experiment?languageCode=ja-JP&countryCode=JP HTTP/1.1
Host: api.example.com
```

> ⚠️ **변경 배경**: 기존 DynamicTargeting 시스템은 languageCode/countryCode를 참조할 수 없어, 별도 Context API 시스템을 신규 구축. 기존 KR 앱 경로(`/rec/v3/*`)는 영향 없음.

---

## 3. REC API Step Function 구조

전체 메뉴얼은 GitHub `doc/api/rec-api-manual-all-in-one.md` 참고.

### 3.1 데이터 소스 타입 (type)

| 타입 | 설명 |
|------|------|
| `api` | 외부 API 호출 |
| `local_cache` | 로컬 캐시 참조 |
| `module` | 내부 모듈 |
| `mongo` | MongoDB 적재 데이터 |
| `none` | 빈 데이터 |
| `redis` | Redis 데이터 |
| `s3` | S3 오브젝트 |
| `service` | 내부 서비스 |
| `static_resource` | 정적 리소스 |

### 3.2 연산자 (operator)

| 연산자 | 설명 |
|--------|------|
| `add` | 아이템 추가 |
| `addWithProps` | 속성 포함 추가 |
| `difference` | 차집합 |
| `drop` | 아이템 제거 |
| `intersection` | 교집합 |
| `multiply` | 곱셈/가중치 |
| `none` | 연산 없음 |
| `shuffle` | 랜덤 셔플 |

### 3.3 주요 설정 항목

- `condition` / `where` — 조건부 실행
- `parentGrouping` — 상위 그룹핑
- `limit` / `filter` — 결과 제한 및 필터
- `cacheable` — 캐시 여부
- `weightCondition` — 가중치 조건
- `stepExecutionCondition` — 스텝 실행 조건
- `stepPostFilter` — 후처리 필터 **(Deprecated)**
- `stepPostProcess` — 후처리 프로세스
- `additionalProps` — 추가 속성
- **실험실**: grouping 확장 기능

---

## 4. 응답 구조

### 4.1 단일 실험 응답

#### 기존 (KR 앱 — `/rec/v3/*`)
```json
{
  "code": "OK",
  "data": {
    "id": 1,
    "bucket": "A",
    "mainTitle": "추천 상품",
    "items": [...]
  }
}
```

#### 신규 (글로벌 앱 — `/rec/context/v3/*`) — 2026-02-03 변경
```json
{
  "code": "OK",
  "data": {
    "logProps": {
      "requestedUuid": "base_experiment",
      "routedUuid": "base_experiment_jp",
      "routed": true,
      "countryCode": "JP",
      "languageCode": "ja-JP"
    },
    "id": 1,
    "bucket": "A",
    "mainTitle": "あなたへのおすすめ",
    "items": [...]
  }
}
```

### 4.2 Facade 응답 (다중 실험) — 글로벌 앱
```json
{
  "code": "OK",
  "data": [
    {
      "requestedUuid": "promoted_rec",
      "routedUuid": "promoted_rec_jp",
      "routed": true,
      "order": 1,
      "result": { ... }
    }
  ]
}
```

### 4.3 logProps 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| `requestedUuid` | String | 클라이언트가 요청한 원본 UUID |
| `routedUuid` | String | 실제 실행된 실험 UUID |
| `routed` | Boolean | 라우팅 발생 여부 (true: 다른 실험으로 라우팅됨) |
| `countryCode` | String | 적용된 국가 코드 (예: KR, JP) |
| `languageCode` | String | 적용된 언어 코드 (예: ko-KR, ja-JP) |

---

## 5. 로그 포맷 변경 (글로벌 앱 기준)

> ⚠️ **충돌 기록**: 기존 KR 앱은 String 형식 로그를 사용하고 있으며, 글로벌 앱 출시 이후 Object 형식이 도입됨. 과도기에는 두 형식이 혼재하며 DS팀에서 타입 분기 처리 적용.

### Before (String 기반 — KR 앱 현행)
```
item_ab_props: "dynamicTargetingExperimentKey:xxx,dynamicTargetingBucketName:yyy"
```

### After (Object/JSON 기반 — 글로벌 앱, 2026-02-03 변경)
```json
{
  "item_ab_props": {
    "contextId": "global_promoted_rec",
    "routedUuid": "promoted_beauty_experiment_jp_woman",
    "countryCode": "JP",
    "languageCode": "ja-JP"
  }
}
```

---

## 6. 커스텀탭 개인화 연동 (29CM)

> 출처: [29CM] 커스텀탭 개인화 rec-api 연동 문서 (PE Space, v6)
> 진행 현황: 2026-02-23 29CM Product/Engineering 팀에 연동 가이드 전달 및 일정 협의 완료 (PE Weekly 확인)

### 6.1 목적

캠페인 배정 모델 결과를 기반으로:
1. MongoDB에 추천 데이터 적재
2. Experiment & Bucket 설정에 따라 REC-API로 제공
3. 로그를 통해 Bucket별 AB Test 성과 측정

### 6.2 MongoDB 데이터 적재

| 환경 | 클러스터 | Connection |
|------|---------|-----------|
| Dev | `dev-dataprd-ocmp` | Querypie 참고 |
| Prod | `prod-ocmp-dataprd` | Querypie 참고 |

#### MongoDB Collection Schema

| Field Name | Type | Description |
|-----------|------|-------------|
| `_id` | ObjectId | MongoDB 기본 PK |
| `key` | String | 사용자 식별자 (requestKey) |
| `value` | String | 커스텀탭 식별자 |
| `score` | Double | 모델 점수 (정렬 기준) |

### 6.3 Experiment & Bucket 설정

- **Experiment**: 추천 시스템 어드민 페이지에서 설정. `experimentUuid + userId` 전달 시 Ratio에 따라 사용자별 Bucket 결정
- **Bucket**: Experiment 내 그룹. 각 Bucket에 서로 다른 모델 결과를 매핑 가능

#### 이번 실험 구성 (ABC Test)
- Bucket: 3개 (A / B / C)
- 각 Bucket → 서로 다른 모델 결과 매핑
- Ratio: 동일 비율 또는 설정값에 따름
- 응답에 반드시 `bucket` 포함 → 서버 로그에 남겨 Bucket별 성과 분석

---

## 7. 팀별 작업 가이드 (Global Routing)

### 7.1 전시개발팀 (BFF) 체크리스트
- [ ] 글로벌 앱용 API 호출 URL 변경 (`/rec/v3/` → `/rec/context/v3/`)
- [ ] `countryCode` 쿼리 파라미터 추가 로직 구현
- [ ] `languageCode` 쿼리 파라미터 추가 로직 구현
- [ ] 응답 DTO에 `logProps` 필드 추가
- [ ] 로그 전달 포맷 Object 형식으로 변경
- [ ] FE팀에 로그 스펙 공유

### 7.2 FE팀 (App) 체크리스트
- [ ] 로그 데이터 타입 변경 처리 (String → Object)
- [ ] 기존 String 파싱 로직 제거 또는 분기 처리
- [ ] 신규 필드(countryCode, languageCode) 이벤트 트래킹에 추가
- [ ] 로그 전송 시 Object 형태로 전달
- [ ] DS팀과 로그 스펙 확인

### 7.3 DS팀 체크리스트
- [ ] 기존 String 파싱 쿼리를 Object 접근으로 수정
- [ ] countryCode/languageCode 필드 추가 분석 쿼리 작성
- [ ] 대시보드에 국가별/언어별 메트릭 추가
- [ ] 하위 호환성 분기 처리 로직 적용 (String/Object 혼재)
- [ ] 파이프라인 테스트 (String/Object 혼재 처리)

#### DS팀 분기 처리 쿼리 예시
```sql
SELECT
  CASE
    WHEN TYPEOF(item_ab_props) = 'STRING' THEN
      REGEXP_EXTRACT(item_ab_props, 'dynamicTargetingExperimentKey:([^,]+)', 1)
    ELSE
      item_ab_props.routedUuid
  END AS experiment_id
FROM recommendation_logs
```

---

## 8. 글로벌 라우팅 의존성 및 타임라인

```
[추천 BE팀]
    │
    ├── API 스펙 확정 ──────────────────────────┐
    │                                           │
    ▼                                           ▼
[전시개발팀 (BFF)]                         [DS팀]
    │                               (대기: 로그 스펙 필요)
    │
    ├── BFF 구현 완료
    │
    ├── 로그 스펙 공유 ─────────────────────────┐
    │                                           │
    ▼                                           ▼
[FE팀 (App)]                               [DS팀]
    │                                (대기: 로그 배포 필요)
    │
    └── 앱 배포 완료 → DS팀 분석 파이프라인 업데이트
```

---

## 9. FAQ

**Q. 기존 한국 앱은 영향 없나요?**
A. 네, 영향 없습니다. 기존 경로(`/rec/v3/*`)는 그대로 유지되며, 글로벌 앱만 새 경로(`/rec/context/v3/*`)를 사용합니다.

**Q. 롤백은 어떻게 하나요?**
A. `/rec/context/*` 경로만 비활성화하면 됩니다. 기존 `/rec/*` 경로는 영향 없이 동작합니다.

**Q. 로그 포맷이 섞여도 괜찮나요?**
A. 과도기에는 String/Object 혼재가 가능합니다. DS팀에서 타입 분기 처리를 적용합니다 (KR: String, 글로벌: Object).

**Q. 번역은 어떻게 처리되나요?**
A. 추천 BE팀에서 자동 처리합니다. 클라이언트는 `languageCode` 파라미터만 전달하면 됩니다.

---

## 10. 변경 이력 / 충돌 기록

| 날짜 | 변경 내용 | 출처 문서 |
|------|----------|----------|
| 2026-02-03 | Global Routing 도입 — API 경로 신규 추가 (`/rec/context/v3/*`), 요청 파라미터 (countryCode, languageCode) 추가 | 문서 2 (v2) |
| 2026-02-03 | 로그 포맷 String → Object 변경 (글로벌 앱 한정) | 문서 2 (v2) |
| 2026-02-23 | [29CM] 커스텀탭 rec-api 연동 가이드 전달 및 일정 협의 완료 | 문서 3 (PE Weekly) |
| 2026-02-23 | [29CM] 커스텀탭 REC-API 가이드 섹션 "추가 작성 후 전달 예정" 상태 확인 | 문서 4 (v6) |

### 충돌 항목 정리

| 항목 | 기존 (KR) | 신규 (글로벌, 2026-02-03~) | 해결 방침 |
|------|-----------|--------------------------|----------|
| API 경로 | `/rec/v3/{uuid}` | `/rec/context/v3/{uuid}` | 두 경로 공존. KR은 기존, 글로벌은 신규 사용 |
| 로그 포맷 | String (`key:val,key:val`) | Object (JSON) | 과도기 혼재. DS팀에서 타입 분기 처리 |
| `item_ab_props` 필드명 | `dynamicTargetingExperimentKey`, `dynamicTargetingBucketName` | `contextId`, `routedUuid`, `countryCode`, `languageCode` | 글로벌 앱은 신규 필드명 사용 |
