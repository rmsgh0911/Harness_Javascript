# Harness 폴더

루트 `HARNESS.md`가 작업 규칙의 기준 파일이다. 이 문서는 `Harness/` 폴더의 역할과 표준 명령만 설명한다.

## 읽는 순서

1. 루트 `HARNESS.md`
2. `Harness/state.md`
3. `Harness/next.md`
4. 오늘 날짜의 `Harness/cycles/YYYY-MM-DD.md`
5. 구현 의도나 성공 기준이 불명확하면 `Harness/config/docs.json` 확인 후 관련 문서만 읽는다
6. 현재 요청에 필요한 `package.json`, lockfile, `src/`, `app/`, `lib/`, `packages/`, `test/`, `tests/`, `Harness/scripts/` 파일

## 폴더 역할

- `config/project.json`: JavaScript 프로젝트별 검증 설정
- `config/agents.json`: 지원 작업자와 루트 지시 파일 매핑
- `config/cycle_policy.json`: 단일 작업자 기본 사이클, 작업자 전환, 중단 규칙
- `config/docs.json`: 프로젝트 문서 위치와 에이전트 읽기 정책
- `state.md`: 최신 확정 상태만 유지
- `next.md`: 남은 작업, 보류 리스크, 사람 판단 필요 항목
- `cycles/`: 날짜별 짧은 작업 기록
- `docs/`: 설계 문서, 구현 명세, 성공 기준, 회고록
- `docs/Progress.md`: 한국어 사람용 진행 현황 대시보드
- `doc/`: 기획서, 참고 문서, 원본 자료
- `scripts/`: JavaScript 프로젝트 검증 또는 설정 보조 스크립트
- `scripts/tools/`: 반복 작업을 줄이는 작은 CLI 도구 모음

## 기록 원칙

- `cycles/`는 긴 작업 일지가 아니라 짧은 사이클 로그로 유지한다.
- `state.md`는 누적 작업 일지가 아니며 최신 확정 사실만 둔다.
- `next.md`에는 아직 끝나지 않은 일만 둔다.
- 같은 내용을 `state.md`, `next.md`, `cycles/`에 중복해서 길게 남기지 않는다.

## 프로젝트 문서

설계 문서, 구현 명세, 시나리오, 성공 기준, 회고록은 기본적으로 `Harness/docs/`에 둔다.

`Harness/docs/Progress.md`는 사람용 현황 대시보드다. 작업 일지가 아니다. 주요 기능 완료 후, 커밋 전, 방향 전환 시, 사람 확인이 필요할 때만 간단히 갱신한다.

`Harness/config/docs.json`에 문서 위치와 읽기 정책을 등록한다. 에이전트는 기본적으로 문서를 읽지 않는다. 사용자 요청이나 코드·설정만으로 의도를 파악할 수 없을 때만 읽는다.

## 에이전트 도구

에이전트는 반복적인 탐색, 검증, 요약, 기록 비용을 줄이기 위해 `Harness/scripts/tools/`에 작은 CLI 도구를 추가할 수 있다.

도구 규칙:
- 목적 하나, 기본 동작은 읽기 전용
- 파일 쓰기는 `--write` 같은 명시적 옵션 필요
- 추가·변경 시 `Harness/scripts/tools/tool_manifest.json`에 등록

표준 도구 (있는 경우):

```powershell
python Harness/scripts/tools/harness_context.py
python Harness/scripts/tools/harness_diff_guard.py
python Harness/scripts/tools/harness_cycle.py "작업명" --changed "..." --verified "..." --remaining "..."
python Harness/scripts/tools/harness_state_check.py
python Harness/scripts/tools/harness_handoff.py --request "..."
```

## 검증 도구

- `verify_project.py`: `project.json`, `package.json`, 필수 파일, 필수 scripts 확인
- `build_verify.ps1`: npm/pnpm/yarn 기반 `install`, `check`, `test`, `lint`, `build` 실행
- `build_verify.cmd`: Windows PowerShell 실행 정책을 우회해 `build_verify.ps1` 실행

`verify_project.py`가 통과해도 코드 변경이 있으면 가능한 범위에서 실제 프로젝트 스크립트 검증을 추가한다.

## 표준 명령

프로젝트 구조 검증:

```powershell
python Harness/scripts/verify_project.py
```

의존성 설치:

```powershell
Harness/scripts/build_verify.cmd -Mode Install
```

프로젝트 스크립트 검증:

```powershell
Harness/scripts/build_verify.cmd -Mode Check
Harness/scripts/build_verify.cmd -Mode Test
Harness/scripts/build_verify.cmd -Mode Lint
Harness/scripts/build_verify.cmd -Mode Build
```

사용 가능한 스크립트가 프로젝트마다 다르므로, 필요한 모드는 `Harness/config/project.json`의 `scripts` 설정에 맞춰 조정한다.
