import java.util.*;

// 인접 리스트 BFS: 모든 간선의 이동 비용이 1일 때 시작점에서 각 정점까지 최단 거리
class Solution {
    // 정점 번호: 1 ~ n, edges: 양방향 연결 쌍, start: 시작 정점
    // 반환값: dist[start] = 0, 도달할 수 없는 정점 = -1, 0번 인덱스는 사용하지 않음
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

        int[] dist = new int[n + 1];
        Arrays.fill(dist, -1);

        Queue<Integer> q = new ArrayDeque<>();
        dist[start] = 0;
        q.offer(start);

        while (!q.isEmpty()) {
            int cur = q.poll();

            for (int next : adj.get(cur)) {
                if (dist[next] != -1) continue; // 이미 방문한 정점

                // 큐에 넣을 때 방문 처리: 같은 정점이 중복으로 들어가지 않음
                dist[next] = dist[cur] + 1;
                q.offer(next);
            }
        }

        return dist;
    }
}
