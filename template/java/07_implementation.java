import java.util.*;

class Solution {
    public int[] solution(int n, String commands) {
        int row = 0;
        int col = 0;

        int[] dr = {-1, 1, 0, 0};
        int[] dc = {0, 0, -1, 1};
        String directions = "UDLR";

        for (int i = 0; i < commands.length(); i++) {
            int dir = directions.indexOf(commands.charAt(i));
            if (dir == -1) continue;

            int nr = row + dr[dir];
            int nc = col + dc[dir];

            if (nr < 0 || nr >= n || nc < 0 || nc >= n) continue;

            row = nr;
            col = nc;
        }

        return new int[]{row, col};
    }
}
