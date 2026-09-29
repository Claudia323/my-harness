# 산출물

## 실행 폴더 (플로우 1개 = 폴더 1개)
```
runs/<플로우-slug>/
├── s1-research.md        레퍼런스 5~10개 + 레퍼런스별 반영 포인트 ≥1줄
├── s2-spec.md            화면 2~3개별 목적·구성 요소·상태
├── s3-keyscreens.json    Figma 프레임 ID + 노드 속성 덤프
├── s4-system.json        변수·컴포넌트 목록 + 적용 화면 노드 덤프
└── gate-log.md           게이트 PASS/FAIL 기록, 단계별 복귀 횟수
```

## 규칙 SSOT
- rules/rules.json 1개. 판정 스크립트는 이 파일만 읽는다.
- design.md를 고치면 rules.json도 같이 고친다.
- #f0f0f0(hairline-soft = field)은 값만 검사. 역할 적합성은 사람 승인에서 본다.

## 재개
- gate-log.md의 마지막 PASS 다음 단계부터 이어서 한다. 파일 존재 여부로 판단하지 않는다.
- 복귀 횟수는 gate-log.md에 누적. 재개 후에도 3회 한도 유지.
