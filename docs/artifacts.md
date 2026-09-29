# 산출물

## 실행 폴더 (플로우 1개 = 폴더 1개)
```
runs/
├── figma-file.txt            Figma 작업 파일 URL 1줄 (전 플로우 공유, 오케스트레이터가 씀)
└── <플로우-slug>/
    ├── s1-research.md        uibowl 레퍼런스 + 반영 포인트
    ├── s2-spec.md            화면별 목적·구성 요소·상태·권한
    ├── s3-keyscreens.json    figma-export.js 덤프 (S3)
    ├── s4-system.json        figma-export.js 덤프 (S4)
    └── gate-log.md           판정·승인 기록 (오케스트레이터만 씀)
```

## gate-log.md 형식 (judge.py --next가 이 형식만 읽는다)
```
| # | 시각 | 단계 | 결과 | 메모 |
|---|---|---|---|---|
| 1 | 2026-09-29 10:00 | G1 | FAIL | refs 4 |
| 2 | 2026-09-29 10:20 | G1 | PASS | |
```
- 단계: `G1` `G2` `S3` `H1` `S4` 중 하나. 결과: `PASS` 또는 `FAIL`.
- 행은 추가만 한다. 고치거나 지우지 않는다.

## 규칙 SSOT
- rules/rules.json 1개. 판정 스크립트는 이 파일만 읽는다. 문서에는 값 대신 키 이름을 적는다.
- design.md를 고치면 rules.json도 같이 고친다 (selftest가 색 동기화를 검사).
- #f0f0f0(hairline-soft = field)은 값만 검사. 역할 적합성은 H1에서 본다.

## 재개
- `python3 scripts/judge.py --next <slug>` 결과의 `next` 단계부터 이어서 한다. 파일 존재 여부로 판단하지 않는다.
- 복귀 횟수는 gate-log.md의 FAIL 행에서 계산하므로 재개 후에도 누적된다. 한도 초과면 `next`가 `STOP`.
