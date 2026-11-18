# SSAFY 17기 전공자 코딩테스트 대비 — Java 3일 계획

## 준비 방향

**남은 3일은 SWEA D2~D3를 중심으로 구현·시뮬레이션·완전탐색을 연습한다.**
어려운 알고리즘을 새로 공부하기보다, 제한 시간 안에 Java로 정확하게 구현하는 데 집중한다.

우선순위는 **구현 → 2차원 배열 → 완전탐색·DFS → 그리디 → BFS·기초 DP**다.

## 시험 일정 — 1차수

| 항목 | 일정 |
| --- | --- |
| 시험일 | 2026년 11월 21일(토) |
| 당일 안내(OT) | 12:30~13:30 |
| 코딩테스트 | **13:30~14:50, 80분** |
| 준비 기간 | 11/18(수)~11/20(금) |
| 연습 환경 | Java, SWEA D2~D3 |

## 연습 환경

- 코드 복사·붙여넣기, 테스트, 최종 제출까지 제한 시간 안에 마치는 연습을 한다.

## 3일 문제 풀이 계획

총 **15문제 = 유형별 연습 13문제 + 실전 모의고사 2문제**다.
모의고사 2문제는 처음 푸는 상태로 남겨둔다.

### Day 1. 11/18(수) — D2 구현 기본기

목표: **5문제, 약 2~3시간**

| 순서 | SWEA 문제 | 핵심 유형 |
| --- | --- | --- |
| 1 | [1859. 백만 장자 프로젝트](https://swexpertacademy.com/main/code/problem/problemDetail.do?contestProbId=AV5LrsUaDxcDFAXc) | 그리디, 역순 탐색 |
| 2 | [2001. 파리 퇴치](https://swexpertacademy.com/main/code/problem/problemDetail.do?contestProbId=AV5PzOCKAigDFAUq) | 2차원 배열, 완전탐색 |
| 3 | [1954. 달팽이 숫자](https://swexpertacademy.com/main/code/problem/problemDetail.do?contestProbId=AV5PobmqAPoDFAUq) | 방향 배열, 시뮬레이션 |
| 4 | [1974. 스도쿠 검증](https://swexpertacademy.com/main/code/problem/problemDetail.do?contestProbId=AV5Psz16AYEDFAUq) | 2차원 배열, 중복 검사 |
| 5 | [1979. 어디에 단어가 들어갈 수 있을까](https://swexpertacademy.com/main/code/problem/problemDetail.do?contestProbId=AV5PuPq6AaQDFAUq) | 배열 탐색, 연속 구간 |

특히 **1954. 달팽이 숫자**와 **1979. 어디에 단어가 들어갈 수 있을까**에 집중한다.
Java에서 배열 인덱스와 조건을 실수 없이 작성하는 연습이 핵심이다.

### Day 2. 11/19(목) — D3 구현과 탐색

목표: **5문제, 약 3~4시간**

| 순서 | SWEA 문제 | 핵심 유형 |
| --- | --- | --- |
| 1 | [1206. View](https://swexpertacademy.com/main/code/problem/problemDetail.do?contestProbId=AV134DPqAA8CFAYh) | 배열 탐색, 최댓값 비교 |
| 2 | [1209. Sum](https://swexpertacademy.com/main/code/problem/problemDetail.do?contestProbId=AV13_BWKACUCFAYh) | 행·열·대각선 탐색 |
| 3 | [2805. 농작물 수확하기](https://swexpertacademy.com/main/code/problem/problemDetail.do?contestProbId=AV7GLXqKAWYDFAXB) | 2차원 배열, 규칙 찾기 |
| 4 | [1220. Magnetic](https://swexpertacademy.com/main/code/problem/problemDetail.do?contestProbId=AV14hwZqABsCFAYD) | 상태 관리, 시뮬레이션 |
| 5 | [1215. 회문1](https://swexpertacademy.com/main/code/problem/problemDetail.do?contestProbId=AV14QpAaAAwCFAYi) | 문자열, 완전탐색 |

문제당 **30~40분**을 목표로 한다. 풀이가 막히면 단순한 완전탐색으로 해결할 수 있는지 먼저 확인한다.

### Day 3. 11/20(금) — DFS 연습과 실전 모의고사

목표: **유형별 3문제 + 80분 모의고사**

| 순서 | SWEA 문제 | 핵심 유형 |
| --- | --- | --- |
| 1 | [1289. 원재의 메모리 복구하기](https://swexpertacademy.com/main/code/problem/problemDetail.do?contestProbId=AV19AcoKI9sCFAZN) | 그리디, 문자열 |
| 2 | [2817. 부분 수열의 합](https://swexpertacademy.com/main/code/problem/problemDetail.do?contestProbId=AV7IzvG6EksDFAXB) | DFS, 부분집합 |
| 3 | [5215. 햄버거 다이어트](https://swexpertacademy.com/main/code/problem/problemDetail.do?contestProbId=AWT-lPB6dHUDFAVT) | DFS, 백트래킹 |

위 3문제를 푼 뒤, 아래 2문제를 **Java로 80분 동안 연속해서** 푼다.
시험에서 사용할 Eclipse와 단일 모니터로 연습하고, 코드 복사·붙여넣기와 실제 제출까지 시간에 포함한다.
아래 시간 배분은 연습용이며, 시험의 문항별 시간 제한을 뜻하지 않는다.

#### 80분 모의고사

| 순서 | SWEA 문제 | 시간 배분 |
| --- | --- | --- |
| 1 | 1208. Flatten | 25분 |
| 2 | 1873. 상호의 배틀필드 | 55분 |
| 합계 | 2문제 | 80분 |

모의고사 문제는 SWEA에서 문제 번호로 검색한다.
실전 연습 전에는 풀이를 미리 확인하지 않는다.

## Java 구현 점검

C++로 알고리즘을 풀어온 경험을 바탕으로, 알고리즘 개념 자체보다 **Java로 옮겨 구현하는 과정**에 익숙해진다.

| 항목 | 연습할 내용 |
| --- | --- |
| 입력 | `BufferedReader`, `StringTokenizer` |
| 출력 | `StringBuilder`, `System.out.print()` |
| 배열 | `int[][]`, `char[][]`, `Arrays.sort()` |
| 문자열 | `charAt()`, `toCharArray()`, `substring()` |
| 탐색 | `dr`, `dc` 방향 배열과 재귀 DFS |
| 자료형 | 합계나 이익이 클 때 `long` 사용 |

- SWEA에는 테스트케이스 개수 `T`가 주어지는 문제와 10개로 고정된 문제가 섞여 있으므로, 문제마다 입력 형식을 확인한다.
- 배열 인덱스, 경계 조건, 상태 갱신을 빠뜨리지 않고 구현하는 데 집중한다.
- 유형별 연습에서는 제한 시간을 정해 풀고, 시간이 지나도 해결하지 못하면 풀이를 확인한 뒤 직접 다시 구현한다.

## 시간이 더 남는다면

| 문제 | 추천 이유 |
| --- | --- |
| [1244. 최대 상금](https://swexpertacademy.com/main/code/problem/problemDetail.do?contestProbId=AV15Khn6AN0CFAYD) (D3) | 교환 횟수가 정해진 완전탐색과 백트래킹 연습 |
| [1220. Magnetic](https://swexpertacademy.com/main/code/problem/problemDetail.do?contestProbId=AV14hwZqABsCFAYD) 재풀이 | 상태를 추적하는 구현을 빠르게 할 수 있는지 점검 |

1220은 Day 2에 포함되어 있으므로, 추가 시간에는 **기존 코드를 보지 않고 다시 구현하는 용도**로 사용한다.
추가 연습은 기본 15문제에 포함하지 않는다.

## 준비 완료의 기준

15문제를 모두 푸는 것보다 **D2를 빠르고 정확하게 해결하고, D3 구현 문제를 Java로 혼자 완성할 수 있는 상태**가 중요하다.
남은 3일 동안 D4 이상에 많은 시간을 쓰기보다, 위 유형의 구현 정확도와 속도를 높이는 데 집중한다.
