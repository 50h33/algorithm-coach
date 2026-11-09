# algorithm-coach

C++·Java 코딩테스트를 공부하며 질문한 내용과 외부에서 받은 설명을
언어·개념별 지식 노트로 모으는 저장소입니다.

## 사용 방법

평소 편한 편집기나 프로그래머스 웹에서 코드를 작성하면 됩니다.
이 프로젝트의 에이전트 대화에 질문하거나, 받은 답변을 붙여 넣고 정리를 요청하세요.

프로그래머스 문제 링크와 함께 “이 문제 풀어볼게”라고 말하면,
에이전트는 짧게 응답하며 기본 코드를 자동으로 가져오거나 연습장 파일을 변경하지 않습니다.
기본 틀 준비나 기본 코드로 초기화를 명시적으로 요청하면 해당 문제의 공식 기본 코드를 준비합니다.
이때 지정한 언어나 최근 대화의 언어를 사용하며, 별도 정보가 없으면 Java를 사용합니다.
Java는 [problem/Solution.java](problem/Solution.java), C++는 `problem/solution.cpp`를 사용합니다.

`problem/`은 한 문제씩 푸는 연습장입니다. 풀이 질문을 하면 에이전트가 이 파일을 직접 읽습니다.
문제를 시작하거나 이어 푼다는 말만으로 코드를 초기화하거나 수정하지 않습니다.
문제별 풀이 파일이나 코드 백업은 남기지 않습니다.

```text
이 Java 답변을 노트로 정리해줘.
[답변 내용]
```

여러 메시지로 나눠 보낼 때는 마지막에 “다 보냈어”라고 알려주세요.
에이전트는 같은 주제의 기존 노트에 내용을 합치거나 새 주제의 노트를 만듭니다.

“다 풀었어”, “이제 통과했어”라고 알려주면, 대화에서 질문하거나 새로 배운 내용을
별도 요청 없이 `notes/`에 정리합니다. 기존 노트와 겹치는 설명은 생략하고 새 내용만 합칩니다.
이미 모두 정리된 내용이면 노트 파일을 변경하지 않습니다. 노트 정리가 끝나면 완료한 연습장 파일은
내용 없는 0바이트 파일로 비워 둡니다. 노트 저장이나 코드 비우기를 원하지 않으면 함께 알려주세요.

노트에는 개념 설명, 사용법, 짧은 코드 예제와 주의점을 담습니다.
별도 요청이 없으면 출처는 적지 않습니다. 문제별 회고나 AI 복습은 진행하지 않습니다.

## 노트 찾기

[지식 노트 목차](notes/README.md)에서 주제별 내용을 찾아볼 수 있습니다.

- [Java Map](notes/java/map.md)
- [Java 타입과 문자열 변환](notes/java/type-conversion.md)
- [Java 정수 나눗셈과 올림](notes/java/integer-division.md)
- [Java 리스트와 배열 변환](notes/java/list-and-array.md)

## 코딩테스트 준비

시험 대비 유형, 추천 문제, 학습 계획은 루트의 `preparation/`에 정리합니다.
`notes/`에는 공부하면서 새로 알게 된 개념·문법·API를 정리합니다.

- [소프티어 부트캠프 대비](preparation/softeer-bootcamp.md)

## 파일 구조

```text
algorithm-coach/
├─ README.md
├─ AGENTS.md
├─ .agents/skills/algorithm-coach/SKILL.md
├─ notes/
│  ├─ README.md
│  ├─ java/
│  └─ algorithms/
├─ preparation/
│  └─ softeer-bootcamp.md
├─ problem/
│  └─ Solution.java
└─ template/
   ├─ README.md
   ├─ cpp/
   └─ java/
```

`notes/`의 Markdown 파일이 노트 원본입니다. 직접 읽고 수정할 수 있으며,
노트 정리에 Python 설치나 별도 프로그램 실행은 필요하지 않습니다.
이전 학습 관리 도구의 `data/`, `scripts/`, `tests/`는 더 이상 사용하지 않으며,
노트 정리 과정에서 이 디렉토리나 Python 캐시를 생성하지 않습니다.

`template/`는 직접 작성한 C++·Java 템플릿을 보관하는 공간입니다.
에이전트는 노트를 정리하면서 풀이·템플릿 소스를 대신 구현하거나 수정하지 않습니다.

에이전트의 정리 방식은 [스킬](.agents/skills/algorithm-coach/SKILL.md),
프로젝트 규칙은 [AGENTS.md](AGENTS.md)에 있습니다.
