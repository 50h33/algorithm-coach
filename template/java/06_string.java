import java.util.*;

class Solution {
    public int solution(String s) {
        int n = s.length();
        if (n <= 1) return n;

        int answer = n;

        for (int size = 1; size <= n / 2; size++) {
            String prev = s.substring(0, size);
            int count = 1;
            StringBuilder sb = new StringBuilder();

            for (int i = size; i < n; i += size) {
                String cur = s.substring(i, Math.min(i + size, n));

                if (prev.equals(cur)) {
                    count++;
                } else {
                    if (count > 1) sb.append(count);
                    sb.append(prev);
                    prev = cur;
                    count = 1;
                }
            }

            if (count > 1) sb.append(count);
            sb.append(prev);
            answer = Math.min(answer, sb.length());
        }

        return answer;
    }
}
