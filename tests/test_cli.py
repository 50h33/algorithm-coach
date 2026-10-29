"""Exercise the documented CLI as separate sessions, without network access."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CliScenarioTests(unittest.TestCase):
    def test_register_to_review_in_separate_processes(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "study.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pid = "programmers-99999999"

            def run(day, *args, payload=None):
                command = [sys.executable, str(script), "--root", str(root / "study"), "--on", day, *args]
                if payload is not None:
                    source = root / "input.json"
                    source.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
                    command += ["--input", str(source)]
                result = subprocess.run(command, capture_output=True, encoding="utf-8", timeout=15)
                self.assertEqual(0, result.returncode, result.stderr)
                return json.loads(result.stdout)

            content = {"title": "합성 예제", "description": "주어진 수를 그대로 반환한다.",
                       "constraints": "입력은 정수이다.", "examples": "입력 1 / 출력 1"}
            registered = run("2026-09-27", "register",
                             "https://school.programmers.co.kr/learn/courses/30/lessons/99999999", payload=content)
            self.assertEqual("complete", registered["content_status"])
            # This represents the learner editing; the CLI never performs this write.
            solution = root / "study" / registered["files"]["solution"]
            original = b"// learner implementation\r\nint solution(int n) { return n; }\r\n"
            solution.write_bytes(original)
            run("2026-09-27", "log", pid, "--request-id", "q-1", payload={
                "question": "반환형만 설명해줘.", "hint": "함수가 돌려주는 값의 타입입니다.",
                "level": 0, "topic": "cpp-return-type", "facts": [], "hypotheses": [], "issue": "other"})
            run("2026-09-27", "complete", pid, "--request-id", "complete-1", payload={
                "declaration": "통과했어.",
                "local_examples": {"status": "unknown", "source": "not_checked", "evidence": ""},
                "submission": {"status": "passed", "source": "user_report", "evidence": "통과했어."}})
            run("2026-09-27", "draft", pid, "--request-id", "draft-1", payload={
                "initial_approach": "문제 요구를 함수로 옮겼다.", "stuck_points": ["반환형 확인"],
                "facts": ["반환형 문법을 질문했다."], "hypotheses": [], "help_received": "문법 설명 1회",
                "correction_principle": "", "review_task": {"kind": "full", "prompt": "문제만 보고 다시 구현하세요."}})
            self.assertEqual([], run("2026-09-28", "due")["items"])
            run("2026-09-27", "confirm", pid, "--request-id", "confirm-1", payload={
                "draft_version": 1, "principle": "코드를 쓰기 전에 반환형부터 확인하겠다.", "confirmation": "확인했어."})
            self.assertEqual(1, len(run("2026-09-28", "due")["items"]))
            started = run("2026-09-28", "review-start", pid)
            attempt = root / "study" / started["file"]
            attempt.write_text("// learner review\n", encoding="utf-8")
            self.assertEqual(1, run("2026-09-29", "resume", pid)["problems"][0]["active_review"]["number"])
            self.assertTrue(run("2026-09-29", "review-start", pid)["resumed"])
            finished = run("2026-09-29", "review-finish", pid, "--request-id", "finish-1", payload={
                "attempt": 1, "success": True, "hint_used": False, "source": "user_report",
                "evidence": "기존 풀이와 도움 없이 다시 구현했다는 사용자 보고"})
            self.assertEqual("2026-10-02", finished["schedule"]["due"])
            self.assertEqual(1, finished["schedule"]["independent_full_successes"])
            self.assertEqual(original, solution.read_bytes())
            self.assertEqual("// learner review\n", attempt.read_text(encoding="utf-8"))
            self.assertTrue(run("2026-09-29", "validate")["valid"])

    def test_java_register_to_review_in_separate_processes(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "study.py"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root / "study"
            pid = "programmers-88888888"

            def run(day, *args, payload=None, expected=0):
                command = [sys.executable, str(script), "--root", str(workspace), "--on", day, *args]
                if payload is not None:
                    source = root / "input.json"
                    source.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
                    command += ["--input", str(source)]
                result = subprocess.run(command, capture_output=True, encoding="utf-8", timeout=15)
                self.assertEqual(expected, result.returncode, result.stderr)
                return json.loads(result.stdout if expected == 0 else result.stderr)

            content = {"title": "Java 합성 문제", "description": "값을 반환한다.",
                       "constraints": "정수 입력", "examples": "1 -> 1"}
            registered = run("2026-10-01", "register",
                             "https://school.programmers.co.kr/learn/courses/30/lessons/88888888",
                             "--language", "java", payload=content)
            self.assertEqual("java", registered["language"])
            self.assertEqual(f"problems/{pid}/java/Solution.java", registered["files"]["solution"])
            solution = workspace / registered["files"]["solution"]
            original = b"class Solution { int solution(int n) { return n; } }\r\n"
            solution.write_bytes(original)

            run("2026-10-01", "log", pid, "--language", "java", "--request-id", "java-q-1", payload={
                "question": "Java 반환형만 설명해줘.", "hint": "메서드가 돌려주는 값의 타입입니다.",
                "level": 0, "topic": "java-return-type", "facts": [], "hypotheses": [], "issue": "other",
                "line_start": 1, "line_end": 1,
            })
            run("2026-10-01", "complete", pid, "--language", "java", "--request-id", "java-complete-1", payload={
                "declaration": "Java 풀이가 통과했어.",
                "local_examples": {"status": "unknown", "source": "not_checked", "evidence": ""},
                "submission": {"status": "passed", "source": "user_report", "evidence": "통과했어."},
            })
            run("2026-10-01", "draft", pid, "--language", "java", "--request-id", "java-draft-1", payload={
                "initial_approach": "문제 요구를 Java 메서드로 옮겼다.",
                "stuck_points": ["반환형 확인"], "facts": ["Java 반환형 문법을 질문했다."],
                "hypotheses": [], "help_received": "문법 설명 1회", "correction_principle": "",
                "review_task": {"kind": "full", "prompt": "문제만 보고 Java로 다시 구현하세요."},
            })
            self.assertEqual([], run("2026-10-02", "due", "--language", "java")["items"])
            run("2026-10-01", "confirm", pid, "--language", "java", "--request-id", "java-confirm-1", payload={
                "draft_version": 1, "principle": "코드를 쓰기 전에 Java 반환형부터 확인하겠다.",
                "confirmation": "확인했어.",
            })
            self.assertEqual(1, len(run("2026-10-02", "due", "--language", "java")["items"]))

            started = run("2026-10-02", "review-start", pid, "--language", "java")
            self.assertEqual(f"problems/{pid}/java/reviews/attempt-001/Solution.java", started["file"])
            attempt = workspace / started["file"]
            attempt_original = b"class Solution { int solution(int n) { return n; } }\r\n"
            attempt.write_bytes(attempt_original)

            resumed = run("2026-10-03", "resume", pid, "--language", "java")
            self.assertEqual("java", resumed["problems"][0]["language"])
            self.assertEqual(1, resumed["problems"][0]["active_review"]["number"])
            resumed_review = run("2026-10-03", "review-start", pid, "--language", "java")
            self.assertTrue(resumed_review["resumed"])
            self.assertEqual(started["file"], resumed_review["file"])

            finished = run("2026-10-03", "review-finish", pid, "--language", "java",
                           "--request-id", "java-finish-1", payload={
                "attempt": 1, "success": True, "hint_used": False, "source": "user_report",
                "evidence": "기존 풀이와 도움 없이 Java로 다시 구현했다는 사용자 보고",
            })
            self.assertEqual("2026-10-06", finished["schedule"]["due"])
            self.assertEqual(1, finished["schedule"]["independent_full_successes"])
            self.assertEqual(original, solution.read_bytes())
            self.assertEqual(attempt_original, attempt.read_bytes())
            validated = run("2026-10-03", "validate")
            self.assertEqual((True, 2, 1, 1), (
                validated["valid"], validated["version"], validated["problems"], validated["studies"]))


if __name__ == "__main__":
    unittest.main()
