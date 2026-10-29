# algorithm-coach

VS Code에서 C++ 또는 Java로 코딩테스트 문제를 직접 풀면서 막힌 순간을 기록하고,
다음 공부 때 도움 없이 다시 구현하는 개인용 학습 도구입니다. 사용자는 대화와 구현을,
에이전트는 단계별 힌트와 회고를, Python은 파일 저장과 복습 일정을 담당합니다.

같은 문제를 두 언어로 풀 수 있습니다. 문제 본문은 공유하고 질문, 완료, 회고, 복습 일정은
언어별로 독립 관리합니다. 로컬 파일만 사용하며 웹서버, 로그인, 외부 DB, 예약 알림과
상시 감시는 없습니다. 프로그래머스 링크를 처음 등록할 때만 문제 페이지를 가져옵니다.

## 시작하기

Python 3.15, VS Code와 Skill을 사용할 수 있는 코딩 에이전트가 필요합니다.
추가 Python 패키지는 없습니다. C++와 Java 실행은 평소 사용하는 환경을 사용합니다.

`.python-version`에는 `3.15`를 지정합니다. 아래 Windows 명령은 `py -3.15`로 실행 버전을
명시합니다. 다른 환경에서는 `python3.15`를 사용합니다.

```powershell
py -3.15 --version
py -3.15 scripts/study.py validate
```

새 Codex 대화에서 언어와 링크를 함께 말하면 됩니다.

```text
$algorithm-coach https://school.programmers.co.kr/learn/courses/30/lessons/42583 Java로 등록해줘.
```

명령의 `--language`는 `cpp` 또는 `java`이며 등록 시 생략하면 `cpp`입니다.

```powershell
py -3.15 scripts/study.py register "https://school.programmers.co.kr/learn/courses/30/lessons/42583" --language java
```

새 C++ 풀이 파일은 `problems/programmers-42583/cpp/solution.cpp`, Java 풀이 파일은
`problems/programmers-42583/java/Solution.java`입니다. 문제별 함수·메서드 서명과 구현은
직접 작성합니다. 에이전트는 질문 전에는 풀이에 개입하지 않습니다.

Skill은 [`.agents/skills/algorithm-coach/SKILL.md`](.agents/skills/algorithm-coach/SKILL.md),
프로젝트 규칙은 [AGENTS.md](AGENTS.md), 세부 명령은 [명령·입력 계약](docs/commands.md)에 있습니다.

## 언어별 학습

같은 URL을 다른 언어로 다시 등록하면 문제 본문을 재사용하고 새 언어 학습만 추가합니다.
언어가 하나뿐인 문제는 `log`, `complete`, `draft`, `confirm`, `context`, `review-start`,
`review-finish`에서 언어를 생략할 수 있습니다. 두 언어가 등록된 문제는 잘못된 기록을
수정하지 않도록 `--language`를 지정해야 합니다.

```powershell
py -3.15 scripts/study.py resume programmers-42583 --language java
py -3.15 scripts/study.py due --language cpp
py -3.15 scripts/study.py review-start programmers-42583 --language java
```

`resume`과 `due`에서 언어를 생략하면 언어가 표시된 전체 목록을 반환합니다.
본문 보충은 두 언어에 공통이므로 `content`에는 언어 옵션을 사용하지 않습니다.

## 대화 흐름

```text
나: $algorithm-coach 문제 링크를 Java로 등록해줘.
AI: Java 풀이를 등록했어요. java/Solution.java에서 직접 작성하면 됩니다.

나: 반복문이 왜 잘못 끝나는지 모르겠어. 지금 Java 코드를 봐줘.
AI: 반복문이 끝나는 조건과 문제의 완료 상태를 각각 문장으로 적어볼까요?
    해당 언어의 코드와 질문·힌트를 기록했어요.

나: 프로그래머스 통과했어. 정리하자.
AI: Java 제출 통과를 사용자 보고로 기록했어요. 회고 초안을 확인해 주세요.
```

질문은 한 번에 한 단계만 돕습니다. 더 직접적인 도움을 요청하면 점검 질문 → 작은 반례
→ 핵심 방향 → 의사코드 순으로 강화합니다. 전체 해설과 정답은 명시적 요청 때만 대화로
제공하며 풀이 파일에는 쓰지 않습니다.

## 복습 규칙

| 결과 | 다음 복습 |
| --- | --- |
| 최초 풀이 완료 후 회고 확인 | 풀이 완료 다음 날 |
| 도움 없이 성공 | 실제 복습 완료일 + 3일 → 7일 → 14일 |
| 14일 단계 이후 독립 성공 | 14일 간격 반복 |
| 실패 또는 힌트 사용 | 다음 날, 간격 단계 처음부터 |
| 기한 경과 | 완료하지 않고 다음 공부 때 다시 제시 |

회고 초안은 사용자가 확인하기 전까지 미확정이며 확인 후에만 복습 일정이 생깁니다.
한 번의 제출 통과, 부분 과제의 독립 성공, 전체 재풀이의 독립 성공은 서로 다른 상태로 기록합니다.
템플릿이나 다른 언어의 풀이를 실제 복습에 참고했다면 도움 사용으로 기록합니다.
복습을 시작할 때 원본 풀이, 다른 언어 풀이, 과거 힌트와 템플릿 내용은 먼저 열지 않습니다.
일정은 `Asia/Seoul` 기준입니다. 시간대 DB가 없는 Windows에서는 현대 서울의 UTC+09:00을
사용하며 2000년 이전의 역사적 시간대 계산은 지원하지 않습니다.

## 파일 구조

```text
algorithm-coach/
├─ AGENTS.md
├─ .agents/skills/algorithm-coach/SKILL.md
├─ scripts/
├─ data/index.json
├─ docs/commands.md
├─ template/
│  ├─ README.md
│  ├─ cpp/.gitkeep
│  └─ java/.gitkeep
└─ problems/programmers-42583/
   ├─ problem.md
   ├─ cpp/
   │  ├─ solution.cpp
   │  ├─ learning-log.md
   │  └─ reviews/attempt-001.cpp
   └─ java/
      ├─ Solution.java
      ├─ learning-log.md
      └─ reviews/attempt-001/Solution.java
```

`template/cpp`와 `template/java`는 사용자가 원하는 구조와 이름으로 알고리즘 템플릿을
직접 저장하는 공간입니다. 도구는 이 파일을 생성·수정하거나 풀이에 자동 삽입하지 않습니다.

기존 v1 C++ 문제의 `solution.cpp`, `reviews/attempt-NNN.cpp`와 생성 문서 경로는 그대로
보존됩니다. 새 구조로 옮기거나 복사하지 않습니다.

## 기존 데이터 전환

v1 기록은 읽기 과정에서 자동 전환하지 않습니다. 먼저 변경 내용을 확인한 뒤 명시적으로
전환합니다.

```powershell
py -3.15 scripts/study.py migrate --dry-run
py -3.15 scripts/study.py migrate
py -3.15 scripts/study.py validate
```

전환 전 인덱스는 `data/index.v1.backup.json`에 배타적으로 보존합니다. 같은 백업이 있으면
재사용하고 내용이 다르면 덮어쓰지 않고 중단합니다. 기존 C++ 소스와 이력은 유지됩니다.

## 보호 범위와 검증

- C++·Java 풀이와 복습 소스는 학습자가 작성합니다. 스크립트는 빈 시작 파일만 배타적으로
  생성하며 기존 파일을 덮어쓰지 않습니다.
- JSON 이력이 저장 원본이고 Markdown은 생성 결과입니다. Markdown을 직접 수정한 내용은
  다음 동기화에서 보존되지 않으므로 상태 변경은 `study.py`를 사용합니다. `data/`와
  `problems/`는 함께 백업합니다.
- 인덱스는 엄격한 상태 검증과 중복 JSON 키·NaN 거부를 거친 뒤 저장합니다. OS 파일 잠금으로
  동시 변경을 막고 같은 폴더의 임시 파일을 원자적으로 교체합니다. 인덱스 저장 뒤 문서 생성만
  실패하면 `resume`으로 복구합니다.
- 프로젝트는 OS ACL이나 에이전트 샌드박스를 변경하지 않습니다. 쓰기 권한이 있는 다른
  도구의 직접 수정을 막는 보안 경계는 아닙니다.
- 프로그래머스 제출과 소스 실행을 자동화하지 않습니다. 실행 결과와 사용자 보고를 구분합니다.

```powershell
py -3.15 -m unittest discover -s tests -v
py -3.15 -m py_compile scripts/study.py scripts/programmers.py
```

테스트는 임시 폴더와 합성 데이터로 C++·Java 독립 상태, 기존 v1 전환, 등록부터 복습까지의
흐름, 파일 보존과 복구를 확인합니다. 실제 학습 기록은 테스트 데이터로 사용하지 않습니다.
