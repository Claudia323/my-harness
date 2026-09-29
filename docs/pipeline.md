# 파이프라인

입력: 사용자 플로우 1개 (purpose.md 참조). 수치는 rules/rules.json의 키로만 가리킨다.

| 단계 | 원본 문장(story-work) | 입력 | 출력 |
|---|---|---|---|
| S1 리서치 | 1, 2 | 플로우명, prd.md, story-service.md | uibowl 레퍼런스(개수 `research.refs`) + 레퍼런스별 반영 포인트(`research.min_points_per_ref`) |
| G1 | 1의 기획자 컨펌 → 기계 판정 + 기획자 참고 공유로 대체 (R5) | | |
| S2 화면설계 | 3 | S1 출력, prd.md, story-service.md | 화면별(개수 `spec.screens`) 필수 항목(`spec.required_fields`) |
| G2 | | | |
| S3 키스크린 | 4, 5 | S2 출력, design.md | Figma 키스크린(`frame`) → H1 기획자 확정 |
| S4 토큰·컴포넌트 | 6 | S3 확정 프레임, design.md | Figma 변수·컴포넌트 세트 + 적용 화면 |

story-work 7(가이드 위반 검토)은 단계가 아니라 판정 스크립트가 담당.

## 되돌아가기

| 실패 지점 | 복귀 |
|---|---|
| G1 실패 | S1 |
| G2 실패 (설계 누락 / ★A·B 위반) | S2 |
| S3 판정 실패 | S3 |
| H1 반려 | S2 |
| S4 판정 실패 | S4 |

같은 단계 복귀 한도는 `retry_limit`. 초과 시 중단하고 사람에게 보고.
이 표는 scripts/judge.py의 `ON_PASS`/`ON_FAIL`과 같아야 한다.
