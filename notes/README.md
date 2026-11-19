# 코딩테스트 지식 노트

질문하거나 전달한 설명에서 배운 내용을 언어와 개념별로 모읍니다.
같은 주제의 내용은 해당 노트에 합쳐서 정리합니다.

## 날짜 읽는 방법

새 내용은 바로 위에 `> 정리일: 26.11.19`처럼 한국 시간 기준 `YY.MM.DD`로 표시합니다.
날짜는 다음 날짜 표시나 제목 전까지 적용합니다. 기존 내용에 보강하면 추가한 부분에 새 날짜를 붙입니다.
서로 다른 날짜의 내용이 한 문단·예제에 섞여 있으면 정리일과 보강일을 함께 표시합니다.
복습이나 단순 표현·서식 수정만으로 날짜를 바꾸지 않습니다.

과거의 `Git 기록 기준` 날짜는 해당 문단·예제가 저장소에 추가되거나 변경된 기록에서 확인한 날짜입니다.
실제 작성일이나 처음 몰랐던 날을 확정한 날짜는 아닙니다. 과거 내용을 오늘 날짜로 다시 기록하지 않습니다.
확인 가능한 날짜가 없으면 `정리일: 확인 불가`로 두며, 파일 수정 시각으로 추정하지 않습니다.

## 최근 정리

복습을 요청하면 아래 목록과 본문 날짜를 기준으로 최근 내용부터 살펴봅니다.
같은 노트가 여러 날짜에 등장하면 본문의 해당 날짜 부분을 읽습니다. 날짜 미확인 내용은 마지막에 둡니다.
아래 과거 날짜는 모두 Git 기록 기준이며, `26.11.19`는 이번 대화에서 실제로 정리한 날짜입니다.

| 날짜 | 정리·보강한 내용 |
| --- | --- |
| 26.11.19 | [역방향 탐색과 오른쪽 최댓값](algorithms/linear-scan.md#뒤에서부터-순회하며-오른쪽-최댓값-유지하기), [long 누적과 오버플로](java/type-conversion.md#큰-합계를-long으로-누적하기), [개별 import·변수명과 Math.max의 언박싱](java/map.md#선언과-기본-메서드), [Map 키와 List 원소 존재 확인](java/map.md#값으로-list나-set-저장하기) |
| 26.11.10 | [BFS 방문 상태·좌표 범위·경유지](algorithms/bfs.md), [단조 스택](algorithms/monotonic-stack.md), [격자 시뮬레이션](algorithms/simulation.md), [while·continue·break·경계값](java/control-flow.md), [배열 인덱스·변환·Arrays.copyOf](java/list-and-array.md), [재귀 종료와 정답 판정](java/recursion-and-return.md#다음에-처리할-인덱스와-종료-시점), [스택에 인덱스 저장](java/stack-and-queue.md#스택에-값-대신-인덱스-저장하기), [split 구분자](java/string-and-char.md#split의-구분자는-정규표현식이다) |
| 26.11.09 | [BFS 거리와 탐색 범위](algorithms/bfs.md), [DP 상태와 계산 순서](algorithms/dynamic-programming.md), [대상별 차이 비교](algorithms/linear-scan.md#대상별로-차이-비교하기), [Map import·누적·중첩 컬렉션](java/map.md), [Set 중복 처리](java/set.md), [배열 길이·크기·Arrays.fill](java/list-and-array.md), [스택과 큐](java/stack-and-queue.md), [문자열 순회](java/string-and-char.md#문자열을-향상된-for문으로-순회하기), [char와 Character](java/type-conversion.md#char와-character), [빈 컬렉션과 최댓값 초기화](java/control-flow.md#빈-컬렉션과-최댓값-초기화) |
| 26.11.08 | [그래프 인접 리스트](java/adjacency-list.md), [카운트 차이와 구간 집계](algorithms/linear-scan.md#두-횟수의-관계를-차이-하나로-표현하기), [분기·상태 확인·마지막 구간](java/control-flow.md), [반환값과 재귀 호출](java/recursion-and-return.md), [문자 접근·검색·비교](java/string-and-char.md) |
| 26.11.07 | [정수 나눗셈과 올림](java/integer-division.md), [리스트와 배열 변환](java/list-and-array.md), [Map 조회·누적·순회·정렬](java/map.md), [기본형·언박싱·문자열 변환](java/type-conversion.md) |

## Java

| 주제 | 내용 |
| --- | --- |
| [Map 조회와 누적 및 정렬](java/map.md) | import, containsKey, put, getOrDefault, merge, entrySet, List·Set·Map 값, computeIfAbsent, TreeMap |
| [Set 선언과 중복 처리](java/set.md) | HashSet, contains, add 반환값, 중복 제거와 집계 |
| [타입과 문자열 변환](java/type-conversion.md) | int·Integer, char·Character, 제네릭, 박싱·언박싱, long 누적과 오버플로, parseInt, 숫자 문자, 시간 문자열 |
| [정수 나눗셈과 올림](java/integer-division.md) | ceil, floor, round, 형변환 위치, 정수식 올림, 경계조건 |
| [리스트와 배열 변환](java/list-and-array.md) | `List<Integer>`, `Integer[]`, `int[]`, length·length()·size(), Arrays.fill, 인덱스, Stream 변환, 배열 직접 채우기 |
| [그래프 인접 리스트](java/adjacency-list.md) | `List<List<Integer>>`, 초기화, 연결 추가, 이웃 순회, 방향 구분 |
| [문자열 접근과 문자 비교](java/string-and-char.md) | `charAt`, `indexOf`, `toCharArray`, 향상된 for문, `char`의 `==`, `String`의 `equals` |
| [스택과 큐](java/stack-and-queue.md) | LIFO·FIFO, Deque, push·pop·peek·isEmpty, 인덱스 저장, 인접한 같은 값 제거 |
| [반환값과 재귀 호출](java/recursion-and-return.md) | 반환값 저장, 호출별 지역 변수, 재귀 이후 실행, 처리 범위와 중복 집계, 다음 처리 인덱스, 종료 시점과 정답 판정 |
| [조건문과 반복문의 처리 순서](java/control-flow.md) | `if`·`else if`·`while`, boolean 조건과 후위 감소, continue·break와 중첩 반복, 상태 갱신 시점, 빈 컬렉션과 최댓값 초기화, 마지막 처리 |

## 알고리즘

| 주제 | 내용 |
| --- | --- |
| [순차 탐색과 상태 유지](algorithms/linear-scan.md) | 역방향 탐색과 오른쪽 최댓값, 두 횟수의 차이, 대상별 차이 비교, 구간 시작 시 집계, 마지막 구간, 시간·공간 복잡도 |
| [BFS와 거리 제한 탐색](algorithms/bfs.md) | BFS·DFS 선택, 장애물과 도달 가능성, 거리 배열과 방문 표시, 좌표 구분, 탐색 범위 제한 |
| [동적 계획법의 상태 전이와 계산 순서](algorithms/dynamic-programming.md) | DP 상태 정의, 이동 조건, 의존 관계에 따른 순회, 시작 상태 초기화 |
| [단조 스택](algorithms/monotonic-stack.md) | 대기 인덱스 관리, 여러 원소 처리, 같은 값 비교, 가장 가까운 큰 값, 전체 O(n) 분석 |
| [격자 시뮬레이션과 상태 갱신](algorithms/simulation.md) | 격자 크기, 경로 검사, 명령 전체 취소, 시작 상태 복구와 임시 상태 확정 |
