# 게이트

수치는 rules/rules.json 키로만 가리킨다. 판정은 scripts/judge.py가 한다.

| 지점 | 종류 | 검사 대상 | 통과 조건 | 실패 시 |
|---|---|---|---|---|
| G1 | 기계 | s1-research.md | 개수 `research.refs` · 레퍼런스마다 `research.link_regex` 링크 1개(중복 불가, 링크 속 앱 이름이 제목에 있음) · 반영 포인트 `research.min_points_per_ref` | S1 |
| G1-앱 | judge 에이전트 | 링크 속 앱 이름 | uibowl `filter_by_app`으로 결과 1건 이상 | S1 |
| G2 | 기계 | s2-spec.md | 화면 개수 `spec.screens` · 화면마다 `spec.required_fields` | S2 |
| ★G2-A | 기계 | s2-spec.md | `rule_A.sale_request_text`(공백 무시)가 있는 화면은 권한 `rule_A.sale_request_role` · 자산 상태는 `rule_A.asset_status`만 · `rule_A.phase2_text` 0건 | S2 |
| ★G2-B | 기계 | s2-spec.md | `rule_B.pii_regex` 매칭 0건 | S2 |
| S3 판정 | 기계 | Figma 라이브 덤프 | 저장된 덤프와 동일 · rules.json 디자인 규칙 위반 0 · `frame` 규격·개수 · ★B 0건 | S3 |
| H1 | 사람 | S3 Figma 프레임 | 체크 3개 기록 (아래) | 반려 → S2 |
| S4 판정 | 기계 | Figma 라이브 덤프 | S3 조건 전부 + 변수 미연결 색·모서리 0건 · 변수/컴포넌트 존재 | S4 |

★ = story-service "어기면 안 되는 것" A/B 위반 시 걸림

## H1 사람 승인 (기획자, 1곳)
- [ ] 시안 방향 확정
- [ ] 회사기밀·타인 저작물 없음 (★B의 기계 불가 부분)
- [ ] #f0f0f0 역할 적합 (hairline / field)

결과를 gate-log.md에 `H1 | PASS` 또는 `H1 | FAIL`로 기록하고 메모에 Y/N과 사유를 적는다.

G1 통과 후 s1-research.md는 기획자에게 참고 공유만 (승인 대기 없음).
복귀 한도: `retry_limit`. 다음 단계와 한도 초과 여부는 `judge.py --next <slug>`가 계산한다.

## 기계로 못 잡는 것 (알려진 한계)
- 절대 위치로 배치한 요소 사이의 간격 (auto-layout 간격만 검사)
- 레퍼런스의 화면 패턴이 실제로 그 앱에 있는지 (앱 존재까지만 확인)
- 대비·가독성 같은 시각 품질 (H1에서 본다)
