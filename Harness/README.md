# Harness 폴더

루트 `HARNESS.md`가 작업 규칙의 기준 파일이다. 이 문서는 `Harness/` 폴더의 역할과 표준 명령만 설명한다.

## 읽는 순서

1. 루트 `HARNESS.md`
2. `Harness/state.md`
3. `Harness/next.md`
4. 오늘 날짜의 `Harness/cycles/YYYY-MM-DD.md`
5. 현재 요청에 필요한 `package.json`, lockfile, `src/`, `app/`, `lib/`, `packages/`, `test/`, `tests/`, `Harness/scripts/` 파일

## 폴더 역할

- `config/project.json`: JavaScript 프로젝트별 검증 설정
- `config/agents.json`: 지원 작업자와 루트 지시 파일 매핑
- `config/cycle_policy.json`: 단일 작업자 기본 사이클, 작업자 전환, 중단 규칙
- `state.md`: 최신 확정 상태만 유지
- `next.md`: 남은 작업, 보류 리스크, 사람 판단 필요 항목
- `cycles/`: 날짜별 짧은 작업 기록
- `doc/`: 기획서, 참고 문서, 원본 자료
- `scripts/`: JavaScript 프로젝트 검증 또는 설정 보조 스크립트

## 기록 원칙

- `cycles/`는 긴 작업 일지가 아니라 짧은 사이클 로그로 유지한다.
- `state.md`는 누적 작업 일지가 아니며 최신 확정 사실만 둔다.
- `next.md`에는 아직 끝나지 않은 일만 둔다.
- 같은 내용을 `state.md`, `next.md`, `cycles/`에 중복해서 길게 남기지 않는다.

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
