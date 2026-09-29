# 허들링 디자인 하네스

사용자 플로우 1개를 입력받아 리서치 → 화면설계 → 키스크린 → 토큰·컴포넌트까지 만든다.

## 기준 문서 (값은 여기에만 있다. 이 파일에 값을 복사하지 않는다)
- 서비스 기준: @docs/story-service.md (★A, ★B = 어기면 안 되는 것)
- 목적·완료 기준: @docs/purpose.md
- 파이프라인·복귀: @docs/pipeline.md
- 산출물·재개: @docs/artifacts.md
- 게이트: @docs/gates.md
- 역할·트리거: @docs/roles.md
- 검증: @docs/verification.md
- 디자인 원문: docs/design.md / 판정 규칙 SSOT: rules/rules.json

## 트리거
- "<플로우> 플로우 돌려줘" → runs/<slug>/ 생성 또는 재개
- "H1 승인 Y Y Y" / "H1 반려: <사유>"
- "판정만 <slug> <gate>" / "상태 <slug>"

## 실행 순서
1. 트리거에서 slug를 정한다 (roles.md 표).
2. runs/<slug>/gate-log.md의 마지막 PASS를 읽고 다음 단계를 정한다. 없으면 S1.
3. 단계 에이전트 호출: S1 researcher → S2 planner → S3·S4 designer
4. 단계가 끝날 때마다 judge 호출 → 결과 JSON을 gate-log.md에 기록
5. FAIL → pipeline.md의 복귀 단계로. 같은 단계 복귀가 3회를 넘으면 중단하고 사람에게 보고
6. S3 PASS → H1 승인을 요청하고 멈춘다. 사람의 답을 받기 전에는 S4로 가지 않는다.
7. G1 PASS → s1-research.md를 기획자에게 참고로 공유 (기다리지 않음)

## 오케스트레이터 금지 사항
- s1~s4 산출물을 직접 쓰거나 고치지 않는다
- Figma를 직접 수정하지 않는다
- judge 결과를 해석해서 PASS로 바꾸지 않는다
- H1 승인을 대신하지 않는다
- gate-log.md는 오케스트레이터만 쓴다

## Figma
- 작업 파일: (첫 실행 시 designer가 "Huddling Harness" 생성 후 URL 기입)
- 페이지: 플로우당 1개(이름 = slug), 토큰·컴포넌트는 _system 페이지

## 하네스를 고칠 때
- rules.json / judge.py / design.md 변경 → `python3 scripts/judge.py --selftest` 통과 후 반영
- .claude/agents/*.md 변경 → roles.md 쓰기 범위와 tools 일치 확인
- 커밋 메시지에 바꾼 라운드(R2~R8) 명시
