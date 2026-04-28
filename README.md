# JavaScript Harness 템플릿

이 저장소는 JavaScript/TypeScript 프로젝트에 이식해서 사용하는 `Harness` 운영 템플릿이다.

기준 저장소는 `https://github.com/rmsgh0911/Harness_Javascript.git`이다.

목표는 두 가지다.

1. 새 JavaScript 프로젝트에 `Harness`를 빠르게 초기화한다.
2. goose를 주요 작업자로 두고, ollama에 설치된 로컬 LLM을 goose가 사용하는 구조로 작업 상태와 검증 흐름을 이어받게 한다.

## 사용 시나리오

이 템플릿은 아래 같은 요청에 맞춰 사용한다.

- `"이 프로젝트 기준으로 Harness를 초기화해줘"`
- `"JavaScript 프로젝트용 Harness로 이식해줘"`
- `"goose + ollama 로컬 모델 기준으로 구조를 바꿔줘"`

## 기본 구조

- `HARNESS.md`: 모든 작업자가 먼저 읽는 운영 규칙
- `AGENTS.md`: Codex 계열 작업자를 위한 얇은 라우터
- `GOOSE.md`: goose 작업자를 위한 얇은 라우터
- `Harness/state.md`: 최신 확정 상태
- `Harness/next.md`: 남은 작업과 수동 판단 항목
- `Harness/cycles/`: 날짜별 짧은 작업 기록
- `Harness/config/project.json`: JavaScript 프로젝트 검증 설정
- `Harness/config/agents.json`: 지원 작업자와 지시 파일 매핑
- `Harness/scripts/verify_project.py`: `package.json`과 필수 파일/스크립트 확인
- `Harness/scripts/build_verify.ps1`: 패키지 매니저 기반 검증 명령 실행

## 초기화 방법

1. 대상 JavaScript 프로젝트 루트에 이 템플릿의 `Harness/`를 복사한다.
2. 루트 `HARNESS.md`, `AGENTS.md`, `GOOSE.md`를 복사하거나 기존 지시 파일에 라우팅 문구를 병합한다.
3. `Harness/config/project.json`을 실제 프로젝트 기준으로 채운다.
4. `Harness/state.md`에 현재 프로젝트 상태를 기록한다.
5. `Harness/next.md`에 다음 작업 후보와 수동 검증 필요 항목을 기록한다.
6. 작업 시작 날짜의 `Harness/cycles/YYYY-MM-DD.md`를 만들고 초기화 내용을 남긴다.

## 검증

가장 작은 검증은 아래 순서로 수행한다.

```powershell
python Harness/scripts/verify_project.py
```

빌드, 테스트, 린트 같은 프로젝트 스크립트 검증은 아래 명령을 사용한다.

```powershell
Harness/scripts/build_verify.cmd -Mode Check
Harness/scripts/build_verify.cmd -Mode Test
Harness/scripts/build_verify.cmd -Mode Build
```

패키지 매니저는 `Harness/config/project.json`의 `package_manager` 값을 우선 사용한다. 값이 `auto`이면 lockfile 기준으로 `pnpm`, `yarn`, `npm` 순서로 감지한다.

## 작업자 운영

기본 주 작업자는 goose다. goose는 ollama에 설치된 로컬 LLM을 모델 백엔드로 사용할 수 있다. Codex와 Claude Code는 보조 또는 이식 작업자로 계속 사용할 수 있다.

작업자를 바꿀 때는 자동 전환하지 않고 사람이 명시한다. 새 작업자는 긴 이전 대화보다 아래 파일을 먼저 읽는다.

- `HARNESS.md`
- `Harness/state.md`
- `Harness/next.md`
- 오늘 날짜의 `Harness/cycles/YYYY-MM-DD.md`
- `git status --short`
- `git diff`
