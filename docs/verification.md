# 검증과 리뷰

## 판정자 셀프테스트
`python3 scripts/judge.py --selftest`
- tests/fixtures/ 의 *-pass 는 전부 PASS, *-fail* 은 지정된 규칙으로 FAIL 이어야 통과
- 라이브 덤프 = 저장 덤프면 PASS, 다르면 dump_mismatch
- gate-log 픽스처로 --next 계산 검증
- design.md 에 나오는 hex 가 전부 rules.json colors 에 있어야 통과

| 픽스처 | 기대 | 내용 |
|---|---|---|
| G1-pass / G1-fail | PASS / refs | 레퍼런스 7개 / 4개 |
| G1-fail-link | duplicate_link, link_app_mismatch | 같은 링크 재사용, 제목과 다른 앱 링크 |
| G2-pass | PASS | 판매 신청 화면 권한: seller |
| G2-fail-A / -A-space | rule_A | 권한: paid / "판매신청" 붙여 쓰기 |
| G2-fail-B / -B-space | rule_B | 010-1234-5678 / +82 10 1234 5678 |
| S3-pass / S3-fail | PASS / radius, shadow | radius 16 / radius 12 + shadow |
| S3-fail-cta | accent_on_cta | 컴포넌트 아닌 "Submit Button"에 #0066ff |
| S4-pass / S4-fail | PASS / unbound_color | 변수 연결 / #0066ff 하드코딩 |
| gate-log-resume / -stop / -empty | H1 / STOP / S1 | S3 PASS 후 / S3 FAIL 4회 / 기록 없음 |

## 첫 실전 테스트: sale-request
runs/sale-request/gate-log.md 끝에 기록
- [ ] S1→S4 한 번 완주
- [ ] G1·G2·S3·S4 판정 각 1회 이상 실행
- [ ] FAIL 1회 이상 발생 → 복귀 동작
- [ ] 중단 후 재개 시 --next가 가리킨 단계부터 이어짐

## 변경 리뷰
| 변경 대상 | 반영 전 통과 조건 |
|---|---|
| rules/rules.json, scripts/judge.py | --selftest 전부 통과 |
| docs/design.md | design.md hex ⊂ rules.json colors (selftest 포함) |
| .claude/agents/*.md | roles.md 쓰기 범위 = 에이전트 tools |
| docs/*.md | 수치 대신 rules.json 키 이름 사용 |
| 모든 변경 | 커밋 메시지에 바꾼 라운드(R2~R8) 명시 |
