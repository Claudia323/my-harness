# 역할

## 에이전트 (파일 단위 편집, 나머지는 읽기 전용)
| 에이전트 | 단계 | 쓰기 가능 | 도구 |
|---|---|---|---|
| researcher | S1 | runs/<flow>/s1-research.md | uibowl |
| planner | S2 | runs/<flow>/s2-spec.md | — |
| designer | S3, S4 | Figma 파일, runs/<flow>/s3-keyscreens.json, s4-system.json | Figma |
| judge | 전체 판정 | 없음 | Read, Bash(python3 scripts/judge.py *), Figma get_metadata |

- gate-log.md는 오케스트레이터만 쓴다.
- designer는 S3/S4 덤프를 scripts/figma-export.js로만 만든다.
- judge는 덤프의 프레임 ID가 Figma에 실제 있는지 get_metadata로 대조한다.

## 판정 스크립트
- scripts/judge.py (Python 표준 라이브러리만, rules/rules.json만 읽음)
- 실행: `python3 scripts/judge.py <flow> <G1|G2|S3|S4>`
- 출력: `{"gate","pass","violations":[{"node","rule","value"}]}` JSON

## 자연어 트리거
| 말 | 동작 |
|---|---|
| "<플로우> 플로우 돌려줘" | runs/<slug>/ 생성 또는 재개 |
| "H1 승인 Y Y Y" | 체크 3개 기록 → S4 |
| "H1 반려: <사유>" | 사유 기록 → S2 |
| "판정만 <slug> <gate>" | judge.py만 실행 |
| "상태 <slug>" | gate-log 요약 + 다음 단계 |

## 플로우 slug
무료 콘텐츠 탐색 free-content · 유료 자료 열람 paid-library · 스킬 카드 사용 skill-card
미션 제출 mission-submit · 내 자산 등록 asset-register · 판매 신청 sale-request
운영자 검수 admin-review
