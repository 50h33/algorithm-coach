class Solution {
    public boolean solution(int n) {
        return go(n);
    }

    private boolean go(int n) {
        // 성공 조건
        if (n == 0) {
            return true;
        }

        // 실패 조건
        if (n < 0) {
            return false;
        }

        return go(n - 2) || go(n - 3);
    }
}