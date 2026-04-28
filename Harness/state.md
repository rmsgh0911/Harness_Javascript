# 상태

## 프로젝트

- 프로젝트 종류: JavaScript/TypeScript Harness 템플릿
- 프로젝트명: Harness_Javascript
- 기준 저장소: `https://github.com/rmsgh0911/Harness_Javascript.git`
- 주 작업자: goose
- 모델 백엔드: goose가 ollama에 설치된 로컬 LLM 사용
- 보조 작업자: Codex, Claude Code
- 패키지 매니저: 대상 프로젝트 lockfile 기준 자동 감지
- 기준 설정: `Harness/config/project.json`

## 현재 검증된 상태

- 루트 운영 규칙은 JavaScript/TypeScript 프로젝트를 기준으로 한다.
- `Harness/config/agents.json`은 goose를 주 작업자로 두고 ollama를 모델 백엔드로 설명한다.
- `Harness/scripts/verify_project.py`는 Unreal 의존성 없이 `package.json`과 Harness 설정을 검증한다.
- `Harness/scripts/build_verify.ps1`은 npm/pnpm/yarn 기반 프로젝트 스크립트를 실행한다.

## 주요 파일

- `HARNESS.md`
- `AGENTS.md`
- `GOOSE.md`
- `Harness/README.md`
- `Harness/config/project.json`
- `Harness/config/agents.json`
- `Harness/config/cycle_policy.json`
- `Harness/scripts/verify_project.py`
- `Harness/scripts/build_verify.ps1`

## 검증 상태

- 마지막 Harness 설정 검증: 2026-04-28 `python Harness/scripts/verify_project.py`
- 마지막 Harness JSON 파싱 검증: 2026-04-28 `agents.json`, `cycle_policy.json`, `project.json`
- 마지막 프로젝트 스크립트 검증: 대상 JavaScript 프로젝트에 이식 후 실행 필요

## 리스크

- 이 저장소 자체에는 아직 `package.json`이 없을 수 있다. 템플릿 자체 검증은 `package_json` 누락을 경고로 처리한다.
- 대상 프로젝트에 이식한 뒤 `required_scripts`와 `source_roots`를 실제 구조에 맞게 채워야 한다.
