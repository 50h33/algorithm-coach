# 명령·입력 계약

Python 3.15와 표준 라이브러리만 사용한다. 기본 루트는 프로젝트 폴더다.
Windows에서는 `py -3.15`, 다른 환경에서는 `python3.15`로 실행 버전을 명시한다.
`--root PATH`와 테스트 전용 `--on YYYY-MM-DD`로 임시 시나리오를 실행할 수 있다.
실제 학습에서는 `--on`을 사용하지 않는다.

입력 파일은 UTF-8 JSON이다. 상태 변경 명령의 `--request-id`는 영문·숫자·`_.:-`
1–120자다. 새 사용자 발화에는 새 ID, 실패한 명령 재실행에는 같은 ID와 입력을 쓴다.
표준 출력은 JSON, 실패는 종료 코드 1과 표준 오류의 JSON이다.
요청 내용의 지문을 저장해 같은 언어 범위의 같은 ID와 같은 입력은 재실행으로 처리하고,
같은 ID의 내용이 바뀌면 거부한다. 공유 `content` 요청은 공통 언어 범위에서 판정한다.

## 언어 선택

지원 언어는 `cpp`, `java`다. `register`에서 생략하면 `cpp`다.

- `log`, `complete`, `draft`, `confirm`, `context`, `review-start`, `review-finish`는
  해당 문제에 학습 언어가 하나면 생략할 수 있다. 둘이면 `--language`가 필요하다.
- `resume`, `due`의 `--language`는 선택 필터다. 생략하면 언어가 표시된 전체 결과를 반환한다.
- `content`는 공유 문제 본문을 변경하므로 `--language`를 받지 않는다.
- 응답의 학습 항목에는 `language`가 포함된다. 언어 선택 오류는 쓰기 전에 거부한다.

## 등록·본문 보충

```powershell
py -3.15 scripts/study.py register "https://school.programmers.co.kr/learn/courses/30/lessons/42583" --language java
py -3.15 scripts/study.py register "https://school.programmers.co.kr/learn/courses/30/lessons/42583" --language cpp --no-fetch
py -3.15 scripts/study.py content programmers-42583 --input .temp/content.json --request-id body-001
```

`register --input FILE`은 사용자가 제공한 본문을 사용하고 네트워크 조회를 생략한다.
같은 문제·언어를 다시 등록하면 기존 항목과 소스를 보존한다. 같은 문제의 다른 언어는
저장된 본문을 재사용하고 새 언어 학습만 만든다.

본문 JSON은 아래 네 필드 중 확인한 것만 담을 수 있다. 모든 필드가 채워져야 완료할 수 있다.

```json
{
  "title": "문제의 실제 제목",
  "description": "확인한 문제 설명 전문",
  "constraints": "확인한 제약조건 전문",
  "examples": "확인한 입력·출력과 예제 설명"
}
```

페이지 접근 실패, 로그인, 이미지 또는 본문 누락은 `needs_content`로 남긴다.
`content_note`가 있으면 사용자가 확인한 정보만 `content`로 보충하고 빈 내용을 추측하지 않는다.

## 질문·힌트 기록

```powershell
py -3.15 scripts/study.py log programmers-42583 --language java --input .temp/question-001.json --request-id question-001
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

행 범위는 1부터 시작하며 생략하면 현재 언어의 원본 또는 복습 파일 전체를 기록한다.
도움 단계와 `topic` 진행 상태는 문제·언어·복습 시도별로 분리한다.

| level | 도움 | 조건 |
| --- | --- | --- |
| 0 | 문법/API 답변 | 질문 범위만 직접 설명 |
| 1 | 점검 질문 | 새 주제의 첫 알고리즘 힌트 |
| 2 | 작은 반례·상태 추적 | 앞 단계 뒤 후속 요청 |
| 3 | 핵심 방향 | 앞 단계 뒤 후속 요청 |
| 4 | 의사코드·부분 구현 | 앞 단계 + `explicit_request: true` |
| 5 | 전체 해설·정답 | 명시적 전체 해설 요청 + `explicit_request: true` |

`issue`는 `approach`, `implementation`, `edge_case`, `full_solution`, `other` 중 하나다.

## 완료·회고

```powershell
py -3.15 scripts/study.py complete programmers-42583 --language java --input .temp/complete.json --request-id complete-001
```

```json
{
  "declaration": "프로그래머스 통과했어. 정리하자.",
  "local_examples": {"status": "unknown", "source": "not_checked", "evidence": ""},
  "submission": {"status": "passed", "source": "user_report", "evidence": "프로그래머스 통과했어."}
}
```

`status`는 `unknown`, `passed`, `failed`다. `unknown`의 출처는 `not_checked`다.
로컬 결과 출처는 `user_report` 또는 `agent_run`, 제출 결과 출처는 `user_report`만 허용한다.
확인된 결과는 비어 있지 않은 근거가 필요하다. 도구는 컴파일·실행이나 제출을 대신하지 않는다.

```powershell
py -3.15 scripts/study.py draft programmers-42583 --language java --input .temp/draft.json --request-id draft-001
py -3.15 scripts/study.py confirm programmers-42583 --language java --input .temp/confirm.json --request-id confirm-001
```

```json
{
  "initial_approach": "학습자가 실제로 처음 시도한 접근",
  "stuck_points": ["기록에서 확인한 막힌 지점"],
  "facts": ["코드와 대화에서 확인한 사실"],
  "hypotheses": ["사용자 확인이 필요한 원인 후보"],
  "help_received": "점검 질문 1회",
  "correction_principle": "",
  "review_task": {"kind": "partial", "prompt": "문제의 완료 상태를 설명하고 핵심 반복문을 작성하세요."}
}
```

`draft`의 `review_task.kind`는 `explain`, `partial`, `counterexample`, `full` 중 하나다.
전체 해설(level 5)을 참고했다면 `full`만 허용한다. 초안을 실제로 보여주고 수정 요청은
새 요청 ID로 다시 기록한다.

```json
{
  "draft_version": 1,
  "principle": "다음에 비슷한 문제를 만나면 완료 상태부터 확인하겠다.",
  "confirmation": "이 초안을 확인했어."
}
```

회고 JSON 형식과 도움 단계 규칙은 언어와 무관하며 회고 버전·승인·일정은 언어별이다.
초기 복습일은 해당 언어의 완료 선언일 + 1일이다.

## 복습·재개

```powershell
py -3.15 scripts/study.py due
py -3.15 scripts/study.py due --language java
py -3.15 scripts/study.py resume programmers-42583
py -3.15 scripts/study.py resume programmers-42583 --language cpp
py -3.15 scripts/study.py review-start programmers-42583 --language java
py -3.15 scripts/study.py context programmers-42583 --language java
py -3.15 scripts/study.py review-finish programmers-42583 --language java --input .temp/result.json --request-id review-001-result
```

`due`는 언어, 제목, 기한, 연체 일수, 진행 여부만 반환한다. `resume`은 생성 문서를 복구하고
언어별 상태와 경로를 반환한다. 두 명령은 코드와 도움 본문을 반환하지 않는다.

`review-start`는 현재 언어의 과제와 새 복습 파일을 반환하며 진행 중이면 같은 파일을 반환한다.
C++ 파일은 `cpp/reviews/attempt-NNN.cpp`, Java 파일은
`java/reviews/attempt-NNN/Solution.java`다. 기존 v1 C++ 항목은 원래 경로를 유지한다.

`context`는 질문을 받은 뒤에만 실행한다. 현재 언어와 현재 풀이 또는 복습 시도의 도움
이력만 반환한다. 원본·다른 언어·이전 복습의 코드와 힌트를 섞지 않는다.

```json
{
  "attempt": 1,
  "success": true,
  "hint_used": false,
  "source": "user_report",
  "evidence": "기존 코드와 힌트 없이 다시 구현했다고 사용자가 보고함."
}
```

복습 중 에이전트 힌트, 외부 해설, 템플릿 또는 다른 언어 풀이를 실제로 참고했다면
`hint_used: true`다. 독립 성공 일정은 3일 → 7일 → 14일 → 14일이고 실패 또는 도움
사용 시 다음 날과 단계 0으로 돌아간다.
`source`는 사용자 보고인 `user_report` 또는 실제 평가에 근거한 `agent_observed`다.
해당 언어의 현재 복습 시도에 힌트 기록이 있으면 입력이 `hint_used: false`여도 도움을
사용한 것으로 처리한다. 부분 과제의 독립 성공과 전체 재풀이의 독립 성공 횟수는 구분한다.

## v1 전환

```powershell
py -3.15 scripts/study.py migrate --dry-run
py -3.15 scripts/study.py migrate
```

`--dry-run`은 전환 가능 여부와 대상만 보여주고 쓰지 않는다. `migrate`는 잠금 아래에서
v1 검증, `data/index.v1.backup.json` 배타적 백업, v2 변환·검증, 원자적 저장 순서로 처리한다.
기존 C++ 학습과 이벤트는 `cpp`로 분류하고 기존 소스·문서 경로는 옮기지 않는다.

일반 명령은 v1을 몰래 전환하지 않는다. 먼저 명시적 전환을 안내한다. v2에 다시 실행하면
변경 없이 완료하고 기존 백업 내용이 다르면 덮어쓰지 않는다.

## 저장·검증·복구

```powershell
py -3.15 scripts/study.py validate
py -3.15 -m unittest discover -s tests -v
```

`validate`는 v1과 v2의 스키마·상태 불변식을 검사하고 중복 JSON 키, NaN, 잘못된 날짜와
증거 조합을 거부한다. 상태 변경은 OS 파일 잠금으로 직렬화하고 같은 폴더의 임시 파일에
쓴 뒤 `flush`, `fsync`, 원자적 교체를 사용한다. 인덱스 저장 뒤 문서 생성만 실패하면
`resume`으로 재생성한다.

JSON 이력이 저장 원본이고 Markdown은 재생성 가능한 결과다. Markdown 직접 수정은 다음
동기화에서 보존되지 않는다. `data/`와 `problems/`를 함께 백업한다. 소스와 사용자 템플릿은
덮어쓰지 않으며 충돌한 경로가 있으면 보존한 채 중단한다.
