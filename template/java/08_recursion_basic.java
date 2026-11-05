class Solution {
    public int solution(int n) {
        int answer = 0;

        answer += go(n);

        return answer;
    }

    private int go(int n) {
        // 종료 조건
        if (n == 0) {
            return 1;
        }

        // 재귀 호출
        if (n > 0) {
            return go(n - 1);
        }

        return 0;
    }
}