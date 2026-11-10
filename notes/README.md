# 코딩테스트 지식 노트

질문하거나 전달한 설명에서 배운 내용을 언어와 개념별로 모읍니다.
같은 주제의 내용은 해당 노트에 합쳐서 정리합니다.

## Java

| 주제 | 내용 |
| --- | --- |
| [Map 조회와 누적 및 정렬](java/map.md) | import, containsKey, put, getOrDefault, merge, entrySet, List·Set·Map 값, computeIfAbsent, TreeMap |
| [Set 선언과 중복 처리](java/set.md) | HashSet, contains, add 반환값, 중복 제거와 집계 |
| [타입과 문자열 변환](java/type-conversion.md) | int·Integer, char·Character, 제네릭, 박싱·언박싱, parseInt, 숫자 문자, 시간 문자열 |
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
| [순차 탐색과 카운트 차이](algorithms/linear-scan.md) | 두 횟수의 차이, 대상별 차이 비교, 구간 시작 시 집계, 마지막 구간, 시간·공간 복잡도 |
| [BFS와 거리 제한 탐색](algorithms/bfs.md) | BFS·DFS 선택, 장애물과 도달 가능성, 거리 배열과 방문 표시, 좌표 구분, 탐색 범위 제한 |
| [동적 계획법의 상태 전이와 계산 순서](algorithms/dynamic-programming.md) | DP 상태 정의, 이동 조건, 의존 관계에 따른 순회, 시작 상태 초기화 |
| [단조 스택](algorithms/monotonic-stack.md) | 대기 인덱스 관리, 여러 원소 처리, 같은 값 비교, 가장 가까운 큰 값, 전체 O(n) 분석 |
| [격자 시뮬레이션과 상태 갱신](algorithms/simulation.md) | 격자 크기, 경로 검사, 명령 전체 취소, 시작 상태 복구와 임시 상태 확정 |
