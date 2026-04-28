# Harness 설정

이 폴더는 Harness가 재사용할 프로젝트 설정과 에이전트 설정을 둔다.

- `project.json`: JavaScript 프로젝트별 검증 설정
- `agents.json`: 지원 작업자와 각 작업자의 루트 지시 파일 매핑
- `cycle_policy.json`: 단일 작업자 기본 사이클, 작업자 전환, 중단 규칙

이 폴더는 선언적인 설정만 담는다. 사이클 로그, 긴 리뷰, 토큰, API 키, 로컬 인증 정보, ollama 모델명, 포트, 개인 경로는 여기에 저장하지 않는다.

인증과 로컬 모델 실행 설정은 각 사용자의 앱, CLI, 에이전트 환경에서 처리한다. Harness에는 토큰, API 키, 로그인 정보를 저장하지 않는다.

## 주 작업자 변경

goose를 사용하면 `GOOSE.md`가 먼저 적용된다. ollama는 goose가 사용할 수 있는 로컬 LLM 런타임이며 별도 작업자 지시 파일을 두지 않는다.

Codex 앱에서 작업하면 `AGENTS.md`가, Claude Code에서 작업하면 `CLAUDE.md`가 먼저 적용된다.

`agents.json`은 에이전트를 실행하는 설정 파일이 아니라, 어떤 작업자가 어떤 루트 지시 파일을 읽는지 알려주는 참고 설정이다.

주 작업자를 바꾸려면 사람이 사용할 앱 또는 CLI를 바꿔서 새 세션을 시작한다.

작업자 전환은 자동 전환보다 사람이 명시하는 방식을 우선한다. 전환한 경우 오늘 `Harness/cycles/YYYY-MM-DD.md`에 전환 이유와 새 작업자가 먼저 볼 파일 범위를 짧게 기록한다.

## project.json 주요 필드

- `package_json`: 대상 프로젝트의 `package.json` 경로
- `package_manager`: `auto`, `npm`, `pnpm`, `yarn` 중 하나
- `source_roots`: 소스 루트 후보
- `test_roots`: 테스트 루트 후보
- `required_files`: 반드시 존재해야 하는 파일 목록
- `required_package_fields`: `package.json`에서 반드시 필요한 필드 목록
- `required_scripts`: 반드시 존재해야 하는 npm scripts 목록
- `optional_scripts`: 있으면 검증 명령에서 사용할 수 있는 scripts 목록
- `commands`: `build_verify.ps1`에서 사용할 스크립트 이름 매핑
