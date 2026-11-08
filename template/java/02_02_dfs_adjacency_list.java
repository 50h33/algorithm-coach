import java.util.*;

// 인접 리스트 DFS: 시작점에서 탐색한 경로의 깊이
// 트리에서는 경로가 하나뿐이므로 깊이 = 시작점부터 지나온 간선 수
// 일반 그래프에서는 최단 거리를 보장하지 않음. 이동 비용이 모두 1인 최단 거리는 BFS 사용
class Solution {
    // 정점 번호: 1 ~ n, edges: 양방향 연결 쌍, start: 시작 정점
    // 반환값: depth[start] = 0, 도달할 수 없는 정점 = -1, 0번 인덱스는 사용하지 않음
    public int[] solution(int n, int[][] edges, int start) {
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i <= n; i++) {
            adj.add(new ArrayList<>());
        }

        for (int[] edge : edges) {
            int u = edge[0];
            int v = edge[1];
            adj.get(u).add(v);
            adj.get(v).add(u); // 단방향 u -> v라면 이 줄 제거
        }

        int[] depth = new int[n + 1];
        Arrays.fill(depth, -1);

        depth[start] = 0;
        dfs(start, adj, depth);
        return depth;
    }

    // 재귀 깊이가 크면 StackOverflowError가 발생할 수 있음: 큰 입력에서는 반복형 DFS 고려
    private void dfs(int cur, List<List<Integer>> adj, int[] depth) {
        for (int next : adj.get(cur)) {
            if (depth[next] != -1) continue; // 부모로 돌아가거나 순환하는 것을 방지

            depth[next] = depth[cur] + 1;
            dfs(next, adj, depth);
        }
    }
}
