# GOOSE.md

이 저장소는 Harness 운영 방식을 사용한다.

작업 전 루트 `HARNESS.md`를 먼저 읽고 따른다.

사용자가 기능 구현, 버그 수정, 검증, 사이클, 반복, 최대 N회 작업을 요청하면 `HARNESS.md`의 작업 루프와 기록 규칙을 적용한다.

## goose 주 작업자 동작

- goose는 이 저장소의 기본 주 작업자다.
- goose는 ollama에 설치된 로컬 LLM을 모델 백엔드로 사용할 수 있다.
- ollama 모델명, 포트, 개인 로컬 경로, 인증 정보는 Harness에 기록하지 않는다.
- 작업 시작 시 긴 이전 대화보다 `Harness/state.md`, `Harness/next.md`, 오늘 `Harness/cycles/`, 현재 `git status/diff`를 우선 읽는다.
- JavaScript 프로젝트에서는 `package.json`, lockfile, 관련 소스와 테스트만 필요한 만큼 읽는다.
- 패키지 매니저는 lockfile 또는 `Harness/config/project.json`을 기준으로 하나만 사용한다.
- 작업자 전환 기록이 필요하면 `HARNESS.md`의 작업자 전환 규칙을 따른다.

## 프로젝트별 추가 규칙

프로젝트별 추가 규칙이 필요하면 이 파일 아래에 짧게 덧붙인다.
