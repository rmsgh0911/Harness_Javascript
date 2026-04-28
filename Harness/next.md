# 작업 목록

## 바로 정렬할 작업

- 대상 JavaScript 프로젝트에 이식할 때 `Harness/config/project.json`의 `required_files`, `required_scripts`, `source_roots`를 실제 구조에 맞게 채운다.
- 대상 프로젝트에서 `python Harness/scripts/verify_project.py`를 실행한다.
- 대상 프로젝트에서 필요한 가장 작은 `Harness/scripts/build_verify.cmd -Mode ...` 검증을 실행한다.
- Windows에서 `python` 명령이 앱 실행 별칭으로 잡혀 있으면 Python PATH를 먼저 정리한다.

## 기능 작업

- 작성 필요: 대상 프로젝트의 기능 단위로 적고, 반복 지시가 있으면 최대 사이클 수와 성공 기준을 함께 적는다.

## 구조 개선 후보

- Codex 또는 Claude Code 쪽에서 추가로 필요한 프로젝트별 지시가 생기면 `AGENTS.md` 또는 `CLAUDE.md`에 짧게 반영한다.

## 수동 검증

- 브라우저 UI, 접근성, 반응형 화면, 실제 API 연동은 대상 프로젝트에서 수동 확인한다.

## 알려진 문제

- 없음
