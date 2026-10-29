import java.util.*;

class Solution {
    public int solution(int n, int[][] computers) {
        boolean[] visited = new boolean[n];
        int answer = 0;

        for (int i = 0; i < n ; i++) {
            if (!visited[i]) {
                dfs(i, computers, visited);
                answer++;
            }
        }
        return answer;
    }

    private void dfs(int start, int[][] computers, boolean[] visited) {
        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(start);

        while (!stack.isEmpty()) {
            int cur = stack.pop();
            if (visited[cur]) continue;
            visited[cur] = true;
            
            for (int next = 0; next < computers.length; next++) {
                if (computers[cur][next] == 1 && !visited[next]) {
                    stack.push(next);
                }
            }
        }
    }
}