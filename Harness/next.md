# 작업 목록

## 바로 정렬할 작업

- 대상 JavaScript 프로젝트에 이식할 때 `Harness/config/project.json`의 `required_files`, `required_scripts`, `source_roots`를 실제 구조에 맞게 채운다.
- 대상 프로젝트에서 `python Harness/scripts/verify_project.py`를 실행한다.
- 대상 프로젝트에서 필요한 가장 작은 `Harness/scripts/build_verify.cmd -Mode ...` 검증을 실행한다.

## 기능 작업

- 작성 필요: 대상 프로젝트의 기능 단위로 적고, 반복 지시가 있으면 최대 사이클 수와 성공 기준을 함께 적는다.

## 구조 개선 후보

- goose가 실제로 참조하는 프로젝트 지시 파일 이름이 별도로 정해지면 `GOOSE.md` 또는 `agents.json`에 반영한다.
- goose의 ollama 모델 선택 규칙이 팀 표준으로 정해지면, 개인 모델명이나 포트를 제외하고 일반 운영 원칙만 문서화한다.

## 수동 검증

- 브라우저 UI, 접근성, 반응형 화면, 실제 API 연동은 대상 프로젝트에서 수동 확인한다.

## 알려진 문제

- 없음
