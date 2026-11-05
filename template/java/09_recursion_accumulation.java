class Solution {
    public int solution(int n) {
        int answer = 0;

        answer += go(n);

        return answer;
    }

    private int go(int n) {
        // 성공 조건
        if (n == 0) {
            return 1;
        }

        // 실패 조건
        if (n < 0) {
            return 0;
        }

        int count = 0;

        // 재귀 분기
        count += go(n - 1);
        count += go(n - 2);

        return count;
    }
}