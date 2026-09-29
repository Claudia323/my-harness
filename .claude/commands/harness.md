---
description: 허들링 디자인 하네스 실행. 인자 없이 쓰면 사용법과 진행 중인 플로우를 보여준다.
argument-hint: "[플로우 이름 | H1 승인 Y Y Y | H1 반려: 사유 | 상태 <slug> | 판정만 <slug> <gate>]"
---

CLAUDE.md의 허들링 디자인 하네스 오케스트레이터로 동작한다.

입력: $ARGUMENTS

- 입력이 비어 있으면: runs/ 아래 플로우 폴더마다 `python3 scripts/judge.py --next <slug>`를 실행해 진행 상황 표를 보여주고, docs/roles.md의 자연어 트리거 표와 플로우 slug 목록을 보여준 뒤 멈춘다.
- 입력이 플로우 이름(또는 slug)만이면: "<플로우> 플로우 돌려줘" 트리거로 처리한다.
- 그 외에는 CLAUDE.md의 트리거 규칙대로 처리한다.
