import java.util.*;

class Solution {
    public String[] solution(String[] records) {
        Map<String, String> state = new HashMap<>();
        List<String> answer = new ArrayList<>();

        for (String record : records) {
            String[] parts = record.split(" ", 3);
            String command = parts[0];
            String key = parts[1];

            switch (command) {
                case "SET":
                    state.put(key, parts[2]);
                    break;
                case "DELETE":
                    state.remove(key);
                    break;
                case "GET":
                    answer.add(state.getOrDefault(key, "NOT_FOUND"));
                    break;
                default:
                    break;
            }
        }

        return answer.toArray(new String[0]);
    }
}
