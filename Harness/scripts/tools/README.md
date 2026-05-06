# Harness 도구 폴더

반복적인 탐색, 검증, 요약, 기록 비용을 줄이기 위해 에이전트가 추가하는 작은 CLI 도구를 여기에 둔다.

## 도구를 추가할 때

- 같은 탐색, 검증, 요약, 기록 작업이 반복될 때
- 결과를 짧은 텍스트나 JSON으로 출력할 수 있을 때
- 프로젝트별 값은 `Harness/config/project.json`이나 커맨드라인 인수로 받을 때
- 기본 동작이 읽기 전용이고, 파일 쓰기는 명시적 옵션이 있을 때

## 도구를 추가하지 않을 때

- 일회성 변환 작업
- 판단이 많이 필요한 리팩터
- 불안정한 외부 상태에 의존하는 작업
- 기존 스크립트에 옵션 하나 추가로 충분한 경우

## 등록 규칙

도구를 추가하거나 변경할 때는 `tool_manifest.json`에 다음 항목을 등록한다:

- `name`: 도구 이름
- `path`: 저장소 루트 기준 상대 경로
- `purpose`: 이 도구가 줄이는 반복 비용
- `inputs`: 주요 입력
- `outputs`: 주요 출력
- `writes_files`: 기본 실행 시 파일을 쓰는지, 아니면 명시적 옵션 필요인지
- `safe_by_default`: 기본 실행이 읽기 전용이고 실패해도 안전한지
- `verify`: 최소 검증 명령

## 권장 인터페이스

```powershell
python Harness/scripts/tools/example_tool.py --help
python Harness/scripts/tools/example_tool.py --json
python Harness/scripts/tools/example_tool.py --write
```

도구는 작게 유지한다. 커지면 목적별로 분리한다.

## 표준 도구

- `harness_common.py`: 공유 헬퍼 (다른 도구에서 import)
- `harness_context.py`: 작업 시작용 Harness 현황 요약 출력
- `harness_diff_guard.py`: 변경 파일과 JavaScript 리스크 신호 요약
- `harness_cycle.py`: 사이클 로그 항목 생성; `--write` 옵션으로만 파일에 씀
- `harness_state_check.py`: state/next/cycles가 너무 크거나 오래됐는지 확인
- `harness_handoff.py`: 작업자 전환용 최소 브리핑 생성; `--write` 옵션으로만 파일에 씀

예시:

```powershell
python Harness/scripts/tools/harness_context.py
python Harness/scripts/tools/harness_context.py --request "로그인 기능 추가"
python Harness/scripts/tools/harness_diff_guard.py
python Harness/scripts/tools/harness_diff_guard.py --json
python Harness/scripts/tools/harness_cycle.py "입력 처리 수정" --changed "..." --verified "..." --remaining "..."
python Harness/scripts/tools/harness_cycle.py "입력 처리 수정" --changed "..." --write
python Harness/scripts/tools/harness_state_check.py
python Harness/scripts/tools/harness_handoff.py --request "로그인 이어서 작업"
```

Windows에서 `python`이 Microsoft Store 별칭으로 해석되면 실제 Python 3 실행 파일 경로를 사용한다.
