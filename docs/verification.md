# 검증과 리뷰

## 판정자 셀프테스트
`python3 scripts/judge.py --selftest`
- tests/fixtures/ 의 *-pass 는 전부 PASS, *-fail* 은 전부 FAIL 이어야 통과
- design.md 에 나오는 hex 가 전부 rules.json colors 에 있어야 통과

| 픽스처 | 기대 | 내용 |
|---|---|---|
| G1-pass.md / G1-fail.md | PASS / FAIL | 레퍼런스 7개 / 4개 |
| G2-pass.md | PASS | 판매 신청 화면 권한: seller |
| G2-fail-A.md | FAIL | 판매 신청 화면 권한: paid (★A) |
| G2-fail-B.md | FAIL | 더미 010-1234-5678 (★B) |
| S3-pass.json / S3-fail.json | PASS / FAIL | radius 16 / radius 12 + shadow 1건 |
| S4-pass.json / S4-fail.json | PASS / FAIL | 변수 연결 / #0066ff 하드코딩 |

## 첫 실전 테스트: sale-request
runs/sale-request/gate-log.md 끝에 기록
- [ ] S1→S4 한 번 완주
- [ ] G1·G2·S3·S4 판정 각 1회 이상 실행
- [ ] FAIL 1회 이상 발생 → 복귀 동작
- [ ] 중단 후 재개 시 마지막 PASS 다음 단계부터 이어짐

## 변경 리뷰
| 변경 대상 | 반영 전 통과 조건 |
|---|---|
| rules/rules.json, scripts/judge.py | --selftest 전부 통과 |
| docs/design.md | design.md hex ⊂ rules.json colors (selftest 포함) |
| .claude/agents/*.md | roles.md 쓰기 범위 = 에이전트 tools |
| 모든 변경 | 커밋 메시지에 바꾼 라운드(R2~R8) 명시 |
