# Java 그래프 인접 리스트

인접 리스트는 정점마다 연결된 이웃 정점들을 리스트로 저장하는 방식이다.
C++의 `vector<vector<int>>`처럼 Java에서는 `List<List<Integer>>`를 사용하고,
실제 리스트는 `ArrayList`로 생성할 수 있다.

## C++ 문법과 대응

| 동작 | C++ | Java |
| --- | --- | --- |
| u의 이웃 리스트 접근 | `adj[u]` | `adj.get(u)` |
| u에서 v로 연결 추가 | `adj[u].push_back(v)` | `adj.get(u).add(v)` |
| u의 이웃 수 | `adj[u].size()` | `adj.get(u).size()` |
| u의 이웃 순회 | `for (int v : adj[u])` | `for (int v : adj.get(u))` |

`List`는 인터페이스이고 `ArrayList`는 그 구현체다.
바깥 리스트의 각 원소가 정점 하나의 이웃 리스트이며,
정수 원소의 제네릭 타입에는 `int` 대신 `Integer`를 사용한다.
관련 내용은 [타입과 문자열 변환](type-conversion.md)을 참고한다.

## 생성과 연결 추가

정점 번호가 1부터 n까지라면 0번을 비워 두고 n + 1개의 리스트를 만든다.

```java
import java.util.*;

// 아래 코드는 메서드 안에서 사용한다.
int n = 5;
List<List<Integer>> adj = new ArrayList<>();

for (int i = 0; i <= n; i++) {
    adj.add(new ArrayList<>());
}

int[][] edges = {{1, 2}, {1, 3}, {2, 4}, {4, 5}};

for (int[] edge : edges) {
    int u = edge[0];
    int v = edge[1];
    adj.get(u).add(v);
    adj.get(v).add(u); // 양방향 연결일 때 추가
}

for (int v : adj.get(1)) {
    System.out.println(v);
}
// 출력: 2, 3 (각각 한 줄)
```

- 방향이 있는 `u → v` 연결이라면 `adj.get(u).add(v)`만 수행한다.
- 양방향 연결이라면 반대쪽 리스트에도 추가한다.
- `new ArrayList<>(n + 1)`은 내부 저장 공간의 초기 용량만 지정하며 원소를 만들지 않는다.
  이웃 리스트를 각각 `add`해야 `get(u)`로 접근할 수 있다.
- 이웃 리스트에 저장되는 것은 연결된 정점 번호다. 이동 거리나 소요 시간이 자동으로 계산되지는 않는다.

## 연결 정보와 이동 시간

모든 연결을 지나는 시간이 동일하다면 BFS로 시작점에서 각 정점까지의 최소 이동 횟수를
구할 수 있다. 한 번 이동하는 데 1시간 단위가 걸리면 그 횟수가 최소 소요 시간이 된다.
연결마다 시간이 다르면 이웃 정점 번호와 함께 해당 연결의 시간도 저장해야 한다.
연결 쌍만으로는 서로 다른 이동 시간을 알 수 없다.
