"""Language-specific learning state, paths, and isolation."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import study


URL = "https://school.programmers.co.kr/learn/courses/30/lessons/42583"
PID = "programmers-42583"
CONTENT = {
    "title": "합성 문제",
    "description": "언어별 학습 상태를 확인한다.",
    "constraints": "입력은 정수이다.",
    "examples": "입력 1 / 출력 1",
}


def evidence():
    return {"status": "unknown", "source": "not_checked", "evidence": ""}


def completion():
    return {"declaration": "완료했다.", "local_examples": evidence(), "submission": evidence()}


def draft():
    return {
        "initial_approach": "직접 구현했다.",
        "stuck_points": ["종료 조건"],
        "facts": ["조건을 수정했다."],
        "hypotheses": [],
        "help_received": "도움 없음",
        "correction_principle": "",
        "review_task": {"kind": "full", "prompt": "문제만 보고 다시 구현한다."},
    }


def hint(text, topic="syntax"):
    return {
        "question": text,
        "hint": "질문한 문법만 설명한다.",
        "level": 0,
        "topic": topic,
        "facts": [],
        "hypotheses": [],
        "issue": "other",
        "line_start": 1,
        "line_end": 1,
    }


def algorithm_hint(level, text, topic="approach"):
    value = hint(text, topic)
    value.update({"level": level, "issue": "approach"})
    if level >= 4:
        value["explicit_request"] = True
    return value


class LanguageStudyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.root = Path(self.temp.name)
        self.coach = study.Coach(self.root, "2026-01-01")

    def tearDown(self):
        self.temp.cleanup()

    def register_both(self):
        cpp = self.coach.register(URL, copy.deepcopy(CONTENT), language="cpp")
        with mock.patch("scripts.study.fetch_problem") as fetch:
            java = self.coach.register(URL, language="java")
        fetch.assert_not_called()
        return cpp, java

    def approve(self, language):
        self.coach.apply(PID, "completion", f"complete-{language}", completion(), language)
        self.coach.apply(PID, "draft", f"draft-{language}", draft(), language)
        self.coach.apply(PID, "confirmed", f"confirm-{language}", {
            "draft_version": 1,
            "principle": "구현 전에 상태를 정의한다.",
            "confirmation": "확인했다.",
        }, language)

    def test_registers_cpp_by_default_and_adds_java_without_refetching(self):
        cpp = self.coach.register(URL, copy.deepcopy(CONTENT))
        self.assertEqual("cpp", cpp["language"])
        self.assertEqual(f"problems/{PID}/cpp/solution.cpp", cpp["files"]["solution"])
        self.assertTrue((self.root / cpp["files"]["solution"]).is_file())

        with mock.patch("scripts.study.fetch_problem") as fetch:
            java = self.coach.register(URL, language="java")
        fetch.assert_not_called()
        self.assertFalse(java["duplicate"])
        self.assertEqual("java", java["language"])
        self.assertEqual(f"problems/{PID}/java/Solution.java", java["files"]["solution"])
        self.assertTrue((self.root / java["files"]["solution"]).is_file())

        duplicate = self.coach.register(URL, language="java")
        self.assertTrue(duplicate["duplicate"])
        state = self.coach.load()
        self.assertEqual(2, state["version"])
        self.assertEqual({"cpp", "java"}, set(state["problems"][PID]["studies"]))

    def test_language_is_required_when_problem_has_multiple_studies(self):
        self.register_both()
        before = (self.root / "data/index.json").read_bytes()
        with self.assertRaisesRegex(study.StudyError, "언어"):
            self.coach.apply(PID, "hint", "ambiguous", hint("어느 언어인가요?"))
        self.assertEqual(before, (self.root / "data/index.json").read_bytes())

        for language in ("python", "CPP", ""):
            with self.subTest(language=language), self.assertRaises(study.StudyError):
                self.coach.resume(language=language)

    def test_hints_replays_and_markdown_are_isolated_by_language(self):
        cpp, java = self.register_both()
        cpp_file = self.root / cpp["files"]["solution"]
        java_file = self.root / java["files"]["solution"]
        cpp_file.write_text("int answer;\n", encoding="utf-8")
        java_file.write_text("class Solution {}\n", encoding="utf-8")

        cpp_payload = hint("C++ 타입은?", "types")
        java_payload = hint("Java 타입은?", "types")
        self.coach.apply(PID, "hint", "same-id", cpp_payload, "cpp")
        self.coach.apply(PID, "hint", "same-id", java_payload, "java")
        replayed = self.coach.apply(PID, "hint", "same-id", java_payload, "java")
        self.assertTrue(replayed["replayed"])

        cpp_context = self.coach.context(PID, "cpp")
        java_context = self.coach.context(PID, "java")
        self.assertEqual(["int answer;"], [e["data"]["code"] for e in cpp_context["hints"]])
        self.assertEqual(["class Solution {}"], [e["data"]["code"] for e in java_context["hints"]])
        self.assertTrue(all(e["language"] == "cpp" for e in cpp_context["hints"]))
        self.assertTrue(all(e["language"] == "java" for e in java_context["hints"]))
        self.assertIn("```cpp", (self.root / cpp["files"]["log"]).read_text(encoding="utf-8"))
        self.assertIn("```java", (self.root / java["files"]["log"]).read_text(encoding="utf-8"))

    def test_completion_and_review_schedules_are_independent(self):
        self.register_both()
        self.approve("cpp")
        state = self.coach.load()["problems"][PID]["studies"]
        self.assertEqual("review", state["cpp"]["phase"])
        self.assertEqual("solving", state["java"]["phase"])
        self.assertIsNone(state["java"]["schedule"])

        self.approve("java")
        due = study.Coach(self.root, "2026-01-02").due()
        self.assertEqual(["cpp", "java"], [item["language"] for item in due["items"]])
        self.assertEqual(["java"], [item["language"] for item in study.Coach(
            self.root, "2026-01-02").due("java")["items"]])

        java_review = study.Coach(self.root, "2026-01-02").review_start(PID, "java")
        self.assertEqual(f"problems/{PID}/java/reviews/attempt-001/Solution.java", java_review["file"])
        self.assertTrue((self.root / java_review["file"]).is_file())
        study.Coach(self.root, "2026-01-02").apply(PID, "review_finished", "finish-java", {
            "attempt": 1, "success": True, "hint_used": False,
            "source": "user_report", "evidence": "사용자 보고",
        }, "java")
        studies = self.coach.load()["problems"][PID]["studies"]
        self.assertEqual("2026-01-05", studies["java"]["schedule"]["due"])
        self.assertEqual("2026-01-02", studies["cpp"]["schedule"]["due"])

    def test_content_is_shared_and_never_requires_a_language(self):
        partial = {**CONTENT, "examples": ""}
        self.coach.register(URL, copy.deepcopy(partial), language="cpp")
        self.coach.register(URL, language="java")
        result = self.coach.apply(PID, "content", "shared-content", {"examples": "1 -> 1"})
        self.assertEqual("complete", result["content_status"])
        problem = self.coach.load()["problems"][PID]
        self.assertEqual("1 -> 1", problem["content"]["examples"])
        self.assertEqual({"cpp", "java"}, set(problem["studies"]))
        event = next(e for e in problem["events"] if e["request_id"] == "shared-content")
        self.assertIsNone(event["language"])

    def test_resume_does_not_read_or_modify_user_templates(self):
        self.coach.register(URL, copy.deepcopy(CONTENT), language="java")
        template = self.root / "template/java/dp/custom.java"
        template.parent.mkdir(parents=True)
        original = b"// user-owned template\r\n"
        template.write_bytes(original)
        result = self.coach.resume(PID, "java")
        self.assertNotIn("user-owned template", json.dumps(result, ensure_ascii=False))
        self.assertEqual(original, template.read_bytes())

    def test_help_levels_and_full_explanation_are_isolated_by_language(self):
        cpp, java = self.register_both()
        (self.root / cpp["files"]["solution"]).write_text("int answer;\n", encoding="utf-8")
        (self.root / java["files"]["solution"]).write_text("class Solution {}\n", encoding="utf-8")
        self.coach.apply(PID, "hint", "cpp-full", algorithm_hint(5, "C++ 전체 해설을 보여줘"), "cpp")

        self.coach.apply(PID, "completion", "complete-cpp", completion(), "cpp")
        with self.assertRaisesRegex(study.StudyError, "전체 재풀이"):
            self.coach.apply(PID, "draft", "cpp-partial", {
                **draft(), "review_task": {"kind": "partial", "prompt": "일부를 다시 구현한다."},
            }, "cpp")

        self.coach.apply(PID, "completion", "complete-java", completion(), "java")
        java_partial = self.coach.apply(PID, "draft", "java-partial", {
            **draft(), "review_task": {"kind": "partial", "prompt": "일부를 다시 구현한다."},
        }, "java")
        self.assertEqual(1, java_partial["draft_version"])
        java_context = self.coach.context(PID, "java")
        self.assertEqual([], java_context["hints"])

    def test_review_context_never_crosses_language_or_attempt(self):
        self.register_both()
        self.approve("cpp")
        self.approve("java")
        day = study.Coach(self.root, "2026-01-02")
        cpp_review = day.review_start(PID, "cpp")
        java_review = day.review_start(PID, "java")
        (self.root / cpp_review["file"]).write_text("// CPP_REVIEW_SECRET\n", encoding="utf-8")
        (self.root / java_review["file"]).write_text("// JAVA_REVIEW_SECRET\n", encoding="utf-8")
        day.apply(PID, "hint", "review-same", hint("C++ 복습 질문"), "cpp")
        day.apply(PID, "hint", "review-same", hint("Java 복습 질문"), "java")

        cpp_context = json.dumps(day.context(PID, "cpp"), ensure_ascii=False)
        java_context = json.dumps(day.context(PID, "java"), ensure_ascii=False)
        self.assertIn("CPP_REVIEW_SECRET", cpp_context)
        self.assertNotIn("JAVA_REVIEW_SECRET", cpp_context)
        self.assertIn("JAVA_REVIEW_SECRET", java_context)
        self.assertNotIn("CPP_REVIEW_SECRET", java_context)

    def test_java_sources_cannot_be_overwritten_through_managed_writers(self):
        coach = self.coach
        java_solution = f"problems/{PID}/java/Solution.java"
        with self.assertRaises(study.StudyError):
            coach.atomic_text(java_solution, "overwrite")
        with self.assertRaises(study.StudyError):
            coach.create_source(f"problems/{PID}/java/reviews/../Solution.java", "java")
        with self.assertRaises(study.StudyError):
            coach.create_source(f"problems/{PID}/cpp/Solution.java", "java")


if __name__ == "__main__":
    unittest.main()
