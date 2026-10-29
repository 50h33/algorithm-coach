import java.util.*;

class Solution {
    static final long INF = Long.MAX_VALUE/4;
    
    public long[] solution(int n, int[][] edges, int start) {
        // 1. 그래프 초기화
        List<int[]>[] graph = new ArrayList[n+1];

        for (int i = 1; i <= n; i++) {
            graph[i] = new ArrayList<>();
        }

        // 2. 간선 정보 추가
        for (int[] edge : edges) {
            int u = edge[0];
            int v = edge[1];
            int w = edge[2];
            graph[u].add(new int[]{v, w});
        }

        // 3. 거리 배열 초기화 및 우선순위 큐 초기화
        long[] dist = new long[n+1];
        Arrays.fill(dist, INF);

        PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
        dist[start] = 0;
        pq.offer(new long[]{0, start});

        // 4. 다익스트라 알고리즘 수행
        while (!pq.isEmpty()) {
            long[] cur = pq.poll();
            long d = cur[0];
            int u = (int) cur[1];

            if (d != dist[u]) continue;

            for (int[] edge : graph[u]) {
                int v = edge[0];
                int w = edge[1];

                long nd = d + w;
                if (nd < dist[v]) {
                    dist[v] = nd;
                    pq.offer(new long[]{nd, v});
                }
            }
        }

        for (int i = 1; i <= n; i++) {
            if (dist[i] == INF) {
                dist[i] = -1;
            }
        }
        return dist;
    }
}