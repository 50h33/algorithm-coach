# 명령·입력 계약

Python 3.9 이상, 표준 라이브러리만 사용한다. 기본 저장소는 스크립트가 있는 프로젝트다.
`python scripts/study.py --root PATH --on YYYY-MM-DD COMMAND ...`로 별도 폴더/날짜에서
시나리오를 확인할 수 있다. 실제 학습에서는 `--on`을 생략한다.

모든 입력 파일은 UTF-8 JSON이다. 상태 변경 명령의 `--request-id`는 영문·숫자·`_.:-`
1–120자다. 새 대화에는 새 ID, 같은 작업의 재실행에는 같은 ID와 입력을 쓴다.
표준 출력은 JSON, 실패는 종료 코드 1과 표준 오류의 JSON이다.

## 등록·본문 보충

```powershell
python scripts/study.py register "https://school.programmers.co.kr/learn/courses/30/lessons/42583"
python scripts/study.py register "https://school.programmers.co.kr/learn/courses/30/lessons/42583" --no-fetch
python scripts/study.py content programmers-42583 --input .temp/content.json --request-id body-001
```

`register --input FILE`은 사용자가 제공한 본문을 사용하여 네트워크 요청을 생략한다.
이미 등록된 URL에는 다시 가져오거나 파일을 덮어쓰지 않는다. 보충·수정은 `content`를 쓴다.
본문 JSON은 아래 네 필드 중 확인한 것만 담아도 된다. 모든 필드가 채워져야 완료할 수 있다.
이미지·불완전한 HTML 등 `content_note`가 있으면 그 내용을 사용자에게 확인받아 보충한다.
`content`는 사용자 확인을 받은 정보에만 사용하며 확인 사유를 대신 추측하지 않는다.

```json
{
  "title": "문제의 실제 제목",
  "description": "확인한 문제 설명 전문",
  "constraints": "확인한 제약조건 전문",
  "examples": "확인한 입력·출력과 예제 설명"
}
```

페이지 파서는 문제 영역만 사용한다. 페이지 형식이 바뀌거나 로그인/연결 실패, 이미지,
본문 누락이 있으면 `needs_content`로 남는다. 빈 항목에 값을 만들어 넣지 않는다.

## 질문·힌트 기록

```powershell
python scripts/study.py log programmers-42583 --input .temp/question-001.json --request-id question-001
```

```json
{
  "question": "왜 이 조건에서 끝나면 틀릴까?",
  "hint": "반복문이 끝나는 조건과 문제의 완료 상태를 각각 문장으로 적어볼까요?",
  "level": 1,
  "topic": "termination",
  "facts": ["현재 조건은 대기 중인 항목 수만 확인한다."],
  "hypotheses": ["진행 중인 상태와 완료 상태를 같은 것으로 취급했을 수 있다."],
  "issue": "implementation",
  "explicit_request": false,
  "line_start": 5,
  "line_end": 12
}
```

`line_start`, `line_end`는 1부터 시작하는 포함 범위다. 생략하면 파일 전체를 기록한다.
원본 또는 현재 복습 파일에서 읽은 코드 스냅샷이 이벤트에 들어간다.
`topic`은 같은 막힘에 대해 유지한다. 다른 문제/복습 시도는 별도의 힌트 진행 상태다.

| level | 도움 | 조건 |
| --- | --- | --- |
| 0 | 문법/API 답변 | 질문 범위만 직접 설명 |
| 1 | 점검 질문 | 새 주제의 첫 알고리즘 힌트 |
| 2 | 작은 반례·상태 추적 | 앞 단계 뒤 후속 요청 |
| 3 | 핵심 방향 | 앞 단계 뒤 후속 요청 |
| 4 | 의사코드·부분 구현 | 앞 단계 + `explicit_request: true` |
| 5 | 전체 해설·정답 | 명시적 전체 해설 요청 + `explicit_request: true` |

`issue`는 `approach`, `implementation`, `edge_case`, `full_solution`, `other` 중 하나다.
수준은 프로그램이 단계 건너뛰기를 검사하지만, 자연어 힌트의 실제 내용·명시적 발화의
진위는 에이전트가 책임진다. 수준 5는 명시적 요청 시 앞 단계를 생략할 수 있다.

## 완료 선언

```powershell
python scripts/study.py complete programmers-42583 --input .temp/complete.json --request-id complete-001
```

```json
{
  "declaration": "프로그래머스 통과했어. 정리하자.",
  "local_examples": {"status": "unknown", "source": "not_checked", "evidence": ""},
  "submission": {"status": "passed", "source": "user_report", "evidence": "프로그래머스 통과했어."}
}
```

`status`: `unknown`, `passed`, `failed`. `unknown`의 출처는 `not_checked`다.
나머지는 비어 있지 않은 증거가 필요하다. 로컬 예제의 출처는 `user_report` 또는
`agent_run`, 제출 결과는 `user_report`만 허용한다. 실행 근거에는 실행 명령과 결과를
남긴다. Python은 C++ 컴파일·실행이나 프로그래머스 제출을 대신하지 않는다.

## 회고 초안·수정·확인

```powershell
python scripts/study.py draft programmers-42583 --input .temp/draft.json --request-id draft-001
```

```json
{
  "initial_approach": "학습자가 실제로 처음 시도한 접근",
  "stuck_points": ["기록에서 확인한 막힌 지점"],
  "facts": ["코드/대화/실행 결과에서 확인한 사실"],
  "hypotheses": ["사용자 확인이 필요한 원인 후보"],
  "help_received": "점검 질문 1회. 전체 해설은 보지 않음.",
  "correction_principle": "",
  "review_task": {"kind": "partial", "prompt": "문제의 완료 상태를 설명하고 핵심 반복문을 빈 파일에 작성하세요."}
}
```

`kind`: `explain`, `partial`, `counterexample`, `full`.
전체 해설(level 5) 기록이 있으면 `full`만 허용한다. 복습 중 전체 해설을 참고한 경우도
다음 과제부터 전체 재풀이로 전환한다. 나머지 과제는 확인된 회고에서 선택한다.
초안은 보여준 뒤 사용자 수정을 반영해 새 요청 ID로 다시 `draft`한다. 버전이 증가하고
이전 버전은 이력에 남는다. 사용자 확인 전에는 일정이 생성되지 않는다.

```powershell
python scripts/study.py confirm programmers-42583 --input .temp/confirm.json --request-id confirm-001
```

```json
{
  "draft_version": 1,
  "principle": "다음에 비슷한 문제를 만나면, 코드를 쓰기 전에 완료 상태부터 확인하겠다.",
  "confirmation": "초안 확인했어. 이 원칙으로 저장해줘."
}
```

현재 버전의 사용자 확인 발화와 사용자 자신의 교정 원칙이 필요하다.
초기 복습일은 **완료 선언일 + 1일**이다. 확정이 늦으면 이미 연체일 수 있다.

## 복습·새 세션

```powershell
python scripts/study.py due
python scripts/study.py review-start programmers-42583
python scripts/study.py resume programmers-42583
python scripts/study.py context programmers-42583
python scripts/study.py review-finish programmers-42583 --input .temp/result.json --request-id review-001-result
```

`due`는 제목·기한·연체 일수·진행 여부만 반환한다. `review-start`는 과제, 문제 경로와
새 복습 파일을 반환한다. 기존 진행 중인 시도가 있으면 같은 파일을 반환한다.
`resume`은 미완료 상태, 증거, 일정, 현재 시도와 경로를 반환하고 생성 문서를 복구한다.
기존 힌트·정답은 출력하지 않는다. 일반 풀이 재개 시 에이전트가 로그를 읽고,
복습 재개 시 현재 복습 파일과 과제만 사용한다.

`context`는 **질문을 받은 후에만** 실행한다. 현재 풀이 또는 현재 복습 시도의 질문·힌트·
당시 코드 스냅샷을 반환해 새 세션에서 도움 단계를 이어간다. 복습 중에는 원본 풀이와
이전 복습 시도의 도움 이력을 제외한다. `due`, `review-start`, `resume`은 도움 본문을 출력하지 않는다.

```json
{
  "attempt": 1,
  "success": true,
  "hint_used": false,
  "source": "user_report",
  "evidence": "기존 코드와 힌트 없이 핵심 반복문을 다시 작성했다고 사용자가 보고함."
}
```

`source`: `user_report` 또는 실제 평가에 근거한 `agent_observed`.
해당 복습에 기록된 힌트가 있으면 `hint_used: false`를 입력해도 사용한 것으로 처리한다.
외부 힌트·해설 사용도 `hint_used: true`로 알려야 한다.
독립 성공 시 실제 복습 완료일 기준 3일 → 7일 → 14일 → 14일 반복.
실패하거나 도움을 받으면 다음 날, 단계 0으로 초기화한다.
`independent_successes`는 과제 성공 횟수, `independent_full_successes`는 그중 전체
재풀이 성공 횟수다. 부분 재구현 성공을 전체 문제의 독립 재풀이 성공으로 표시하지 않는다.

## 저장·검증·복구

```powershell
python scripts/study.py validate
python scripts/study.py resume
python -m unittest discover -s tests -v
```

- JSON 로드/저장 모두 스키마·상태를 검증하고, 중복 키·NaN·잘못된 날짜를 거부한다.
- OS 파일 잠금으로 동시 변경을 차단한다. 다른 실행 중이면 그 실행이 끝난 뒤 재실행한다.
  프로세스 종료 시 잠금은 OS가 해제하므로 남은 `.study.lock`을 지울 필요가 없다.
- 같은 폴더의 임시 파일에 쓴 뒤 `flush`/`fsync`/`os.replace`로 인덱스를 교체한다.
  인덱스 커밋 뒤 Markdown이 중단되면 `resume`이 JSON 이력에서 재생성한다.
- JSON이 손상되면 자동 초기화하지 않는다. 작업을 멈추고 백업을 복구해야 한다.
  `data/`와 `problems/`를 함께 백업한다. 자동 백업/동기화 기능은 없다.
- Markdown은 생성 결과이므로 직접 편집한 내용을 보존하지 않는다. 회고 수정은
  확인 전 `draft`, 본문 보충은 `content`, 새 질문은 `log`로 누적한다.
- 복습 파일 경로 충돌 시 기존 파일을 덮어쓰거나 지우지 않고 오류로 멈춘다.
  기록 없는 기존 파일의 출처를 먼저 확인한다.
