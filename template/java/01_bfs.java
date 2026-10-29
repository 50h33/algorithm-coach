import java.util.*;

class Solution {
    static int[] dx = {0, 1, 0, -1};
    static int[] dy = {-1, 0, 1, 0};
    
    public int solution(int[][] maps) {
        int n = maps.length;
        int m = maps[0].length;
        
        int[][] dist = new int[n][m];
        
        Queue<int[]> q = new ArrayDeque<>();
        q.offer(new int[]{0, 0});
        dist[0][0] = 1;
        
        while(!q.isEmpty()) {
            int[] cur = q.poll();
            int y = cur[0];
            int x = cur[1];
            
            if (y == n-1 && x == m-1) {
                return dist[y][x];
            }
            
            for (int d = 0; d < 4; d++) {
                int ny = y + dy[d];
                int nx = x + dx[d];
                if (ny < 0 || ny >= n || nx < 0 || nx >= m) continue;
                if (maps[ny][nx] == 0 || dist[ny][nx] != 0) continue;
                dist[ny][nx] = dist[y][x] + 1;
                q.offer(new int[]{ny, nx});
            }
        }
        return -1;
    }
}