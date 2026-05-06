# JavaScript Harness 템플릿

이 저장소는 Codex, Claude Code 같은 AI 에이전트를 JavaScript/TypeScript 프로젝트의 주 작업자로 사용할 때 쓰는 Harness 운영 템플릿이다.

에이전트가 직접 따라야 하는 운영 지침은 이식 안정성을 위해 영어로 작성한다. 예를 들어 `HARNESS.md`, `AGENTS.md`, `CLAUDE.md`, `Harness/README.md`, `Harness/config/*.json`, `Harness/state.md`, `Harness/next.md`는 영어를 기본으로 한다.

반대로 이 루트 `README.md`는 사람이 템플릿을 이해하고 이식할 때 보는 안내 문서이므로 한국어로 작성한다. `Harness/docs/Progress.md`도 사람이 보는 진행 현황판이므로 한국어로 작성한다.

기준 저장소는 `https://github.com/rmsgh0911/Harness_Javascript.git`이다.

## 빠른 시작

```powershell
# 1. Harness 구조와 설정을 점검한다.
python Harness/scripts/tools/harness_doctor.py

# 2. 에이전트 작업 시작 전 짧은 브리핑을 확인한다.
python Harness/scripts/tools/harness_context.py

# 3. 문서 읽기 정책과 문서 루트를 점검한다.
python Harness/scripts/tools/harness_docs_check.py

# 4. 가벼운 최종 점검 묶음을 실행한다.
python Harness/scripts/tools/harness_verify_all.py
```

- 작업 규칙의 기준 파일은 `HARNESS.md`다.
- 에이전트는 `HARNESS.md`, `Harness/state.md`, `Harness/next.md` 순서로 읽는다.
- 도구 설명은 `Harness/README.md`와 `Harness/scripts/tools/README.md`에 있다.

## 목적

이 템플릿은 두 가지 상황을 지원한다.

1. 새 JavaScript/TypeScript 프로젝트에 Harness를 처음 초기화한다.
2. 이미 Harness를 쓰는 프로젝트를 새 템플릿 버전으로 올리되, 프로젝트별 상태, 문서, 스크립트, 기록은 잃지 않는다.

## 사용 요청 예시

- `"이 프로젝트 기준으로 Harness를 초기화해줘"`
- `"JavaScript 프로젝트용 Harness로 이식해줘"`
- `"템플릿 버전 업 해서 이식해줘"`
- `"이 작업을 최대 10사이클로 개선해줘"`

## 기본 구조

- `HARNESS.md`: 모든 작업자가 먼저 읽는 운영 규칙
- `AGENTS.md`: Codex 계열 작업자를 위한 얇은 라우터
- `CLAUDE.md`: Claude Code 작업자를 위한 얇은 라우터
- `Harness/state.md`: 최신 확정 상태
- `Harness/next.md`: 남은 작업과 수동 판단 항목
- `Harness/cycles/`: 날짜별 짧은 작업 기록
- `Harness/docs/`: 설계 문서, 구현 명세, 성공 기준, 회고록의 기본 위치
- `Harness/docs/Progress.md`: 한국어 사람용 진행 현황판
- `Harness/config/project.json`: JavaScript 프로젝트 검증 설정
- `Harness/config/agents.json`: 지원 작업자와 지시 파일 매핑
- `Harness/config/cycle_policy.json`: 사이클, 기록, 도구, 중단 규칙
- `Harness/config/docs.json`: 프로젝트 문서 위치와 읽기 정책
- `Harness/scripts/verify_project.py`: `package.json`과 필수 파일/스크립트 확인
- `Harness/scripts/build_verify.ps1`: 패키지 매니저 기반 검증 명령 실행
- `Harness/scripts/tools/`: 반복 작업을 줄이는 작은 CLI 도구

## 초기화 방법

1. 대상 JavaScript 프로젝트 루트에 이 템플릿의 `Harness/`를 복사한다.
2. 루트 `HARNESS.md`를 복사한다.
3. 루트 `AGENTS.md`가 없으면 템플릿의 `AGENTS.md`를 복사한다.
4. 루트 `AGENTS.md`가 이미 있으면 `HARNESS.md`를 읽으라는 짧은 라우팅 문구만 병합한다.
5. Claude Code를 사용할 프로젝트라면 `CLAUDE.md`도 복사하거나, 기존 `CLAUDE.md`에 `HARNESS.md` 라우팅 문구만 병합한다.
6. 프로젝트용 루트 `README.md`는 기존 프로젝트 내용을 우선한다.
7. 실제 JavaScript 프로젝트 기준으로 `Harness/config/project.json`을 채운다.
8. 프로젝트 문서는 기본적으로 `Harness/docs/`에 둔다. 외부 문서 폴더를 쓸 때만 `Harness/config/docs.json`에 등록한다.
9. `Harness/state.md`에 현재 확인된 프로젝트 상태를 적는다.
10. `Harness/next.md`에 다음 작업과 수동 검증 필요 항목을 적는다.
11. 실제 프로젝트 작업 기록이 필요할 때만 `Harness/cycles/YYYY-MM-DD.md`를 만든다.

## 이식할 때 보존할 것

대상 프로젝트에 이미 Harness가 있다면 아래 항목은 보존한다.

- `Harness/state.md`
- `Harness/next.md` 또는 기존 후속 작업 문서의 의미
- `Harness/cycles/`
- `Harness/docs/`, `ProjectDocs/`, `Docs/`, `DesignDocs/` 같은 프로젝트 문서
- 프로젝트별 `Harness/config/project.json`
- 프로젝트별 `Harness/config/docs.json`
- 프로젝트별 스크립트와 표준 스크립트에 추가된 커스텀 로직
- 루트 `AGENTS.md`, `CLAUDE.md`의 저장소별 규칙
- 프로젝트 루트 `README.md`

템플릿에서 가져오거나 병합할 것은 아래 항목이다.

- `HARNESS.md`
- `AGENTS.md`, `CLAUDE.md`의 Harness 라우팅 문구
- `Harness/config/agents.json`
- `Harness/config/cycle_policy.json`의 새 필드와 정책
- `Harness/config/docs.json`의 새 필드와 정책
- `Harness/config/README.md`
- `Harness/scripts/` 아래 표준 스크립트와 도구
- 템플릿 문서에 추가된 새 운영 규칙

## 검증

가장 작은 구조 검증:

```powershell
python Harness/scripts/tools/harness_doctor.py
```

표준 가벼운 점검:

```powershell
python Harness/scripts/tools/harness_verify_all.py
```

대상 프로젝트에 이식한 뒤에는 아래 검증도 실행한다.

```powershell
python Harness/scripts/verify_project.py
Harness/scripts/build_verify.cmd -Mode Check
Harness/scripts/build_verify.cmd -Mode Test
Harness/scripts/build_verify.cmd -Mode Build
```

패키지 매니저는 `Harness/config/project.json`의 `package_manager` 값을 우선 사용한다. 값이 `auto`이면 lockfile 기준으로 `pnpm`, `yarn`, `npm` 순서로 감지한다.

Windows에서 `python`이 Microsoft Store 별칭으로 해석되면 실제 Python 3 실행 파일 경로나 작업 공간 런타임 Python을 사용한다.
