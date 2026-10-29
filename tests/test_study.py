import copy
from datetime import date, datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts import study


URL = "https://school.programmers.co.kr/learn/courses/30/lessons/42583"
PID = "programmers-42583"
CONTENT = {
    "title": "다리를 지나는 트럭",
    "description": "트럭이 다리를 모두 건너는 시간을 구한다.",
    "constraints": "bridge_length는 1 이상이다.",
    "examples": "2, 10, [7,4,5,6] -> 8",
}


def evidence(status="unknown", source="not_checked", text=""):
    return {"status": status, "source": source, "evidence": text}


def completion(local=None, submission=None):
    return {
        "declaration": "풀이를 완료했다.",
        "local_examples": local or evidence(),
        "submission": submission or evidence(),
    }


def draft(kind="partial"):
    return {
        "initial_approach": "직접 시뮬레이션했다.",
        "stuck_points": ["종료 조건에서 막혔다."],
        "facts": ["종료 조건을 두 번 수정했다."],
        "hypotheses": ["진행 중 상태를 빠뜨렸을 수 있다."],
        "help_received": "작은 반례 힌트 한 번",
        "correction_principle": "완료 상태를 먼저 문장으로 쓴다.",
        "review_task": {"kind": kind, "prompt": "핵심 반복문을 다시 작성한다."},
    }


def hint(level=1, topic="종료 조건", **overrides):
    value = {
        "question": "왜 종료되지 않나요?",
        "hint": "완료 상태를 말로 정의해 보세요.",
        "level": level,
        "topic": topic,
        "facts": ["대기열만 종료 조건에서 확인한다."],
        "hypotheses": ["다리 위 트럭을 빠뜨렸을 수 있다."],
        "issue": "edge_case",
        "line_start": 1,
        "line_end": 2,
    }
    value.update(overrides)
    return value


class CoachCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def coach(self, on="2026-01-01"):
        return study.Coach(self.root, on)

    def register(self, on="2026-01-01", content=CONTENT):
        coach = self.coach(on)
        coach.register(URL, copy.deepcopy(content))
        return coach

    def approve(self, completed_on="2026-01-01", confirmed_on=None, kind="partial"):
        coach = self.register(completed_on)
        coach.apply(PID, "completion", "complete-1", completion())
        coach.apply(PID, "draft", "draft-1", draft(kind))
        confirmer = self.coach(confirmed_on or completed_on)
        confirmer.apply(PID, "confirmed", "confirm-1", {
            "draft_version": 1,
            "principle": "완료 상태를 먼저 확인한다.",
            "confirmation": "초안을 확인했다.",
        })
        return confirmer

    def load(self):
        return self.coach().load()

    def finish_review(self, day, attempt, success=True, hint_used=False, request_id=None):
        return self.coach(day).apply(PID, "review_finished", request_id or f"finish-{attempt}", {
            "attempt": attempt,
            "success": success,
            "hint_used": hint_used,
            "source": "user_report",
            "evidence": "사용자가 재구현 결과를 보고함",
        })


class EndToEndTests(CoachCase):
    def test_seoul_day_rolls_over_near_utc_midnight(self):
        instant = datetime(2026, 1, 1, 15, 30, tzinfo=timezone.utc)
        self.assertEqual(date(2026, 1, 2), study.seoul_day(instant))

    def test_review_schedule_handles_month_end_and_leap_year(self):
        self.assertEqual(("2028-03-01", 1), study.next_review(date(2028, 2, 27), 0, True))
        self.assertEqual(("2028-03-07", 2), study.next_review(date(2028, 2, 29), 1, True))
        self.assertEqual(("2026-02-01", 0), study.next_review(date(2026, 1, 31), 3, False))

    def test_registration_hint_completion_and_retrospective_preserve_evidence_sources(self):
        coach = self.register()
        solution = self.root / "problems" / PID / "cpp" / "solution.cpp"
        solution.write_text("int solution() {\n    return 0;\n}\n", encoding="utf-8")
        coach.apply(PID, "hint", "hint-1", hint())
        result = coach.apply(PID, "completion", "complete-1", completion(
            evidence("passed", "agent_run", "로컬 예제 프로세스 종료 코드 0"),
            evidence("passed", "user_report", "사용자가 프로그래머스 통과를 보고함"),
        ))
        self.assertEqual("retrospective_pending", result["phase"])
        coach.apply(PID, "draft", "draft-1", draft())
        coach.apply(PID, "draft", "draft-2", {**draft(), "help_received": "점검 질문 한 번"})
        result = coach.apply(PID, "confirmed", "confirm-1", {
            "draft_version": 2,
            "principle": "종료 상태부터 정의한다.",
            "confirmation": "수정본을 확인했다.",
        })

        state = self.load()["problems"][PID]["studies"]["cpp"]
        self.assertEqual("review", result["phase"])
        self.assertEqual("agent_run", state["completion"]["local_examples"]["source"])
        self.assertEqual("user_report", state["completion"]["submission"]["source"])
        self.assertEqual(2, state["approved"]["version"])
        self.assertEqual("2026-01-02", state["schedule"]["due"])
        log = (self.root / "problems" / PID / "cpp" / "learning-log.md").read_text(encoding="utf-8")
        self.assertIn("확인된 사실", log)
        self.assertIn("원인 후보 (추정)", log)

    def test_first_due_uses_completion_day_instead_of_late_confirmation_day(self):
        self.approve(completed_on="2026-01-01", confirmed_on="2026-01-05")
        self.assertEqual("2026-01-02", self.load()["problems"][PID]["studies"]["cpp"]["schedule"]["due"])
        due = self.coach("2026-01-05").due()["items"][0]
        self.assertEqual(3, due["overdue_days"])

    def test_independent_success_intervals_use_actual_review_day_and_repeat_fourteen(self):
        self.approve()
        expected = [
            ("2026-01-02", "2026-01-05", 1),
            ("2026-01-10", "2026-01-17", 2),
            ("2026-01-17", "2026-01-31", 3),
            ("2026-01-31", "2026-02-14", 3),
        ]
        for attempt, (actual, next_due, stage) in enumerate(expected, 1):
            self.coach(actual).review_start(PID)
            self.finish_review(actual, attempt)
            schedule = self.load()["problems"][PID]["studies"]["cpp"]["schedule"]
            self.assertEqual(next_due, schedule["due"])
            self.assertEqual(stage, schedule["stage"])
        self.assertEqual(4, self.load()["problems"][PID]["studies"]["cpp"]["schedule"]["independent_successes"])

    def test_hint_or_failure_resets_interval_then_independent_success_gets_three_days(self):
        self.approve()
        self.coach("2026-01-02").review_start(PID)
        self.finish_review("2026-01-02", 1)

        self.coach("2026-01-05").review_start(PID)
        self.coach("2026-01-05").apply(PID, "hint", "review-hint", hint())
        self.finish_review("2026-01-05", 2, success=True, hint_used=False)
        schedule = self.load()["problems"][PID]["studies"]["cpp"]["schedule"]
        self.assertEqual(("2026-01-06", 0), (schedule["due"], schedule["stage"]))

        self.coach("2026-01-06").review_start(PID)
        self.finish_review("2026-01-06", 3, success=False)
        schedule = self.load()["problems"][PID]["studies"]["cpp"]["schedule"]
        self.assertEqual(("2026-01-07", 0), (schedule["due"], schedule["stage"]))

        self.coach("2026-01-07").review_start(PID)
        self.finish_review("2026-01-07", 4)
        schedule = self.load()["problems"][PID]["studies"]["cpp"]["schedule"]
        self.assertEqual(("2026-01-10", 1), (schedule["due"], schedule["stage"]))

    def test_partial_and_full_independent_success_counts_are_separate(self):
        self.approve(kind="partial")
        self.coach("2026-01-02").review_start(PID)
        self.finish_review("2026-01-02", 1)
        schedule = self.load()["problems"][PID]["studies"]["cpp"]["schedule"]
        self.assertEqual((1, 0), (schedule["independent_successes"], schedule["independent_full_successes"]))

        other_root = self.root / "full-case"
        other_root.mkdir()
        self.root = other_root
        self.approve(kind="full")
        self.coach("2026-01-02").review_start(PID)
        self.finish_review("2026-01-02", 1)
        schedule = self.load()["problems"][PID]["studies"]["cpp"]["schedule"]
        self.assertEqual((1, 1), (schedule["independent_successes"], schedule["independent_full_successes"]))

    def test_overdue_item_stays_due_until_finished(self):
        self.approve()
        first = self.coach("2026-01-10").due()["items"][0]
        second = self.coach("2026-01-11").due()["items"][0]
        self.assertEqual("2026-01-02", first["due"])
        self.assertEqual(8, first["overdue_days"])
        self.assertEqual(9, second["overdue_days"])
        self.assertEqual([], self.load()["problems"][PID]["studies"]["cpp"]["reviews"])

    def test_hint_levels_cannot_skip_but_same_level_is_allowed_and_new_review_resets(self):
        coach = self.register()
        coach.apply(PID, "hint", "solution-level-1", hint(level=1))
        coach.apply(PID, "hint", "solution-level-1-again", hint(level=1))
        with self.assertRaisesRegex(study.StudyError, "한 번에 한 단계"):
            coach.apply(PID, "hint", "solution-level-3", hint(level=3))

        coach.apply(PID, "completion", "complete-1", completion())
        coach.apply(PID, "draft", "draft-1", draft())
        coach.apply(PID, "confirmed", "confirm-1", {
            "draft_version": 1,
            "principle": "완료 상태부터 정의한다.",
            "confirmation": "확인했다.",
        })
        review_coach = self.coach("2026-01-02")
        review_coach.review_start(PID)
        review_coach.apply(PID, "hint", "review-level-1", hint(level=1))
        review_hint = [e for e in self.load()["problems"][PID]["events"]
                       if e["request_id"] == "review-level-1"][0]
        self.assertEqual(1, review_hint["data"]["review"])

    def test_full_explanation_requires_explicit_request_and_forces_full_review_task(self):
        coach = self.register()
        with self.assertRaises(study.StudyError):
            coach.apply(PID, "hint", "full-without-request", hint(level=5))
        coach.apply(PID, "hint", "full-explicit", hint(level=5, explicit_request=True))
        coach.apply(PID, "completion", "complete-1", completion())
        with self.assertRaisesRegex(study.StudyError, "전체 재풀이"):
            coach.apply(PID, "draft", "partial-draft", draft("partial"))
        result = coach.apply(PID, "draft", "full-draft", draft("full"))
        self.assertEqual(1, result["draft_version"])

    def test_confirmation_rejects_stale_draft_version_and_accepts_current_version(self):
        coach = self.register()
        coach.apply(PID, "completion", "complete-1", completion())
        coach.apply(PID, "draft", "draft-1", draft())
        coach.apply(PID, "draft", "draft-2", {**draft(), "initial_approach": "수정한 접근"})
        confirmation = {"principle": "상태를 먼저 정의한다.", "confirmation": "확인했다."}
        with self.assertRaisesRegex(study.StudyError, "현재 초안 버전"):
            coach.apply(PID, "confirmed", "confirm-stale", {"draft_version": 1, **confirmation})
        result = coach.apply(PID, "confirmed", "confirm-current", {"draft_version": 2, **confirmation})
        self.assertEqual("review", result["phase"])
        self.assertEqual(2, result["draft_version"])

    def test_context_is_limited_to_the_current_review_attempt(self):
        coach = self.register()
        solution = self.root / "problems" / PID / "cpp" / "solution.cpp"
        solution.write_text("// ORIGINAL_CODE_SECRET\n", encoding="utf-8")
        coach.apply(PID, "hint", "original-hint", hint(
            question="ORIGINAL_QUESTION_SECRET", hint="ORIGINAL_HINT_SECRET", line_end=1))
        solving_context = coach.context(PID)
        self.assertEqual(("solution", None), (solving_context["scope"], solving_context["attempt"]))
        self.assertEqual(["original-hint"], [event["request_id"] for event in solving_context["hints"]])

        coach.apply(PID, "completion", "complete-1", completion())
        coach.apply(PID, "draft", "draft-1", draft())
        coach.apply(PID, "confirmed", "confirm-1", {
            "draft_version": 1,
            "principle": "완료 상태부터 정의한다.",
            "confirmation": "확인했다.",
        })

        due_output = self.coach("2026-01-02").due()
        first_start = self.coach("2026-01-02").review_start(PID)
        resume_output = self.coach("2026-01-02").resume(PID)
        public_outputs = json.dumps([due_output, first_start, resume_output], ensure_ascii=False)
        for secret in ("ORIGINAL_CODE_SECRET", "ORIGINAL_QUESTION_SECRET", "ORIGINAL_HINT_SECRET"):
            self.assertNotIn(secret, public_outputs)

        first_attempt = self.root / first_start["file"]
        first_attempt.write_text("// PRIOR_REVIEW_CODE_SECRET\n", encoding="utf-8")
        first_coach = self.coach("2026-01-02")
        first_coach.apply(PID, "hint", "review-1-hint", hint(
            question="PRIOR_REVIEW_QUESTION_SECRET", hint="PRIOR_REVIEW_HINT_SECRET", line_end=1))
        first_context = first_coach.context(PID)
        self.assertEqual(("review", 1), (first_context["scope"], first_context["attempt"]))
        self.assertEqual(["review-1-hint"], [event["request_id"] for event in first_context["hints"]])
        self.finish_review("2026-01-02", 1, success=False)

        second_start = self.coach("2026-01-03").review_start(PID)
        empty_second_context = self.coach("2026-01-03").context(PID)
        self.assertEqual(("review", 2), (empty_second_context["scope"], empty_second_context["attempt"]))
        self.assertEqual([], empty_second_context["hints"])

        second_attempt = self.root / second_start["file"]
        second_attempt.write_text("// CURRENT_REVIEW_CODE_SECRET\n", encoding="utf-8")
        second_coach = self.coach("2026-01-03")
        second_coach.apply(PID, "hint", "review-2-hint", hint(
            question="CURRENT_REVIEW_QUESTION_SECRET", hint="CURRENT_REVIEW_HINT_SECRET", line_end=1))
        current = second_coach.context(PID)
        encoded = json.dumps(current, ensure_ascii=False)
        self.assertEqual(("review", 2), (current["scope"], current["attempt"]))
        self.assertEqual(["review-2-hint"], [event["request_id"] for event in current["hints"]])
        self.assertIn("CURRENT_REVIEW_HINT_SECRET", encoded)
        for secret in ("ORIGINAL_HINT_SECRET", "ORIGINAL_CODE_SECRET",
                       "PRIOR_REVIEW_HINT_SECRET", "PRIOR_REVIEW_CODE_SECRET"):
            self.assertNotIn(secret, encoded)


class IdempotencyAndRecoveryTests(CoachCase):
    def test_fetch_needs_content_note_is_preserved_even_when_all_content_fields_exist(self):
        fetched = {**CONTENT, "status": "needs_content", "reason": "이미지 예제는 사용자 확인이 필요합니다."}
        with mock.patch("scripts.study.fetch_problem", return_value=fetched):
            result = self.coach().register(URL)
        self.assertEqual("needs_content", result["content_status"])
        self.assertEqual("이미지 예제는 사용자 확인이 필요합니다.", result["content_note"])
        self.assertEqual([], result["missing"])
        persisted = self.load()["problems"][PID]
        self.assertEqual(result["content_note"], persisted["content_note"])
        problem_md = (self.root / "problems" / PID / "problem.md").read_text(encoding="utf-8")
        self.assertIn(result["content_note"], problem_md)

    def test_duplicate_registration_preserves_existing_solution_bytes(self):
        coach = self.register()
        solution = self.root / "problems" / PID / "cpp" / "solution.cpp"
        original = b"// learner bytes\r\nint main() {}\r\n"
        solution.write_bytes(original)
        result = coach.register(URL, copy.deepcopy(CONTENT))
        self.assertTrue(result["duplicate"])
        self.assertEqual(original, solution.read_bytes())

    def test_new_coach_resumes_active_review_and_preserves_attempt_bytes(self):
        self.approve()
        first = self.coach("2026-01-02").review_start(PID)
        attempt = self.root / first["file"]
        original = b"// my review\r\n"
        attempt.write_bytes(original)

        fresh = study.Coach(self.root, "2026-01-03")
        resumed = fresh.review_start(PID)
        self.assertTrue(resumed["resumed"])
        self.assertEqual(1, resumed["attempt"])
        self.assertEqual(original, attempt.read_bytes())
        self.assertEqual(1, len(self.load()["problems"][PID]["studies"]["cpp"]["reviews"]))

    def test_failed_fetch_persists_partial_record_and_requests_missing_content(self):
        fetched = {"title": "제목만 확인", "reason": "본문 접근 실패"}
        with mock.patch("scripts.study.fetch_problem", return_value=fetched):
            result = self.coach().register(URL)
        self.assertEqual("needs_content", result["content_status"])
        self.assertEqual(["description", "constraints", "examples"], result["missing"])
        state = self.load()["problems"][PID]
        self.assertEqual("page_fetch", state["events"][0]["data"]["source"])
        self.assertEqual("본문 접근 실패", state["events"][0]["data"]["reason"])

    def test_replayed_hint_uses_original_snapshot_even_after_solution_changes(self):
        coach = self.register()
        solution = self.root / "problems" / PID / "cpp" / "solution.cpp"
        solution.write_text("old line\nsecond\n", encoding="utf-8")
        payload = hint()
        coach.apply(PID, "hint", "same-id", payload)
        solution.write_text("new line\nchanged\n", encoding="utf-8")
        result = coach.apply(PID, "hint", "same-id", payload)

        hints = [e for e in self.load()["problems"][PID]["events"] if e["kind"] == "hint"]
        self.assertTrue(result["replayed"])
        self.assertEqual(1, len(hints))
        self.assertEqual("old line\nsecond", hints[0]["data"]["code"])

    def test_same_request_id_with_changed_payload_is_rejected(self):
        coach = self.register()
        coach.apply(PID, "hint", "same-id", hint())
        with self.assertRaisesRegex(study.StudyError, "요청 ID의 내용이 바뀌었습니다"):
            coach.apply(PID, "hint", "same-id", hint(question="다른 질문"))

    def test_atomic_index_replace_failure_keeps_old_index_and_cleans_temp_file(self):
        coach = self.register()
        index = self.root / "data" / "index.json"
        old = index.read_bytes()
        with mock.patch("scripts.study.os.replace", side_effect=OSError("replace failed")):
            with self.assertRaises(OSError):
                coach.apply(PID, "hint", "hint-fails", hint())
        self.assertEqual(old, index.read_bytes())
        self.assertEqual([], list(index.parent.glob(".study-*.tmp")))

    def test_index_commit_before_markdown_failure_is_recovered_by_resume(self):
        coach = self.coach()
        original = coach.atomic_text

        def fail_projection(relative, content):
            if relative.endswith("problem.md"):
                raise OSError("projection failed")
            return original(relative, content)

        with mock.patch.object(coach, "atomic_text", side_effect=fail_projection):
            with self.assertRaises(OSError):
                coach.register(URL, copy.deepcopy(CONTENT))
        self.assertIn(PID, self.load()["problems"])
        self.assertFalse((self.root / "problems" / PID / "problem.md").exists())

        fresh = self.coach()
        fresh.resume(PID)
        self.assertTrue((self.root / "problems" / PID / "problem.md").is_file())
        self.assertTrue((self.root / "problems" / PID / "cpp" / "learning-log.md").is_file())


class ValidationAndSafetyTests(CoachCase):
    def write_state(self, value):
        path = self.root / "data" / "index.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")

    def test_malformed_nested_states_are_rejected(self):
        self.approve()
        valid = self.load()
        mutations = []

        bad_stage = copy.deepcopy(valid)
        bad_stage["problems"][PID]["studies"]["cpp"]["schedule"]["stage"] = True
        mutations.append(bad_stage)

        bad_content = copy.deepcopy(valid)
        bad_content["problems"][PID]["content"]["examples"] = []
        mutations.append(bad_content)

        bad_review_count = copy.deepcopy(valid)
        bad_review_count["problems"][PID]["studies"]["cpp"]["schedule"]["independent_successes"] = -1
        mutations.append(bad_review_count)

        for state in mutations:
            with self.subTest(state=state):
                self.write_state(state)
                with self.assertRaises(study.StudyError):
                    self.coach().load()

    def test_bad_url_in_persisted_state_is_rejected(self):
        self.register()
        state = self.load()
        state["problems"][PID]["url"] = "https://evil.example/42583"
        self.write_state(state)
        with self.assertRaisesRegex(study.StudyError, "잘못된 출처 URL"):
            self.coach().load()

    def test_invalid_evidence_combinations_are_rejected(self):
        coach = self.register()
        cases = [
            completion(local=evidence("passed", "not_checked", "claimed")),
            completion(submission=evidence("passed", "agent_run", "agent cannot submit")),
            completion(local=evidence("unknown", "user_report", "uncertain")),
        ]
        for number, payload in enumerate(cases, 1):
            with self.subTest(number=number):
                with self.assertRaises(study.StudyError):
                    coach.apply(PID, "completion", f"bad-evidence-{number}", payload)

    def test_out_of_order_retrospective_and_review_operations_are_rejected(self):
        coach = self.register()
        with self.assertRaises(study.StudyError):
            coach.apply(PID, "draft", "early-draft", draft())
        with self.assertRaises(study.StudyError):
            coach.apply(PID, "confirmed", "early-confirm", {
                "draft_version": 1, "principle": "원칙", "confirmation": "확인"
            })
        with self.assertRaises(study.StudyError):
            coach.review_start(PID)
        coach.apply(PID, "completion", "complete-1", completion())
        with self.assertRaises(study.StudyError):
            coach.apply(PID, "completion", "complete-2", completion())
        with self.assertRaises(study.StudyError):
            coach.apply(PID, "confirmed", "confirm-without-draft", {
                "draft_version": 1, "principle": "원칙", "confirmation": "확인"
            })

    def test_cpp_paths_cannot_be_written_through_managed_document_writer(self):
        coach = self.coach()
        with self.assertRaisesRegex(study.StudyError, "파일과 템플릿은 보호"):
            coach.atomic_text(f"problems/{PID}/solution.cpp", "overwrite")
        with self.assertRaises(study.StudyError):
            coach.create_source(f"problems/{PID}/cpp/reviews/../solution.cpp", "cpp")

    def test_symlink_in_managed_path_is_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        managed = self.root / "problems"
        try:
            managed.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlink creation unavailable: {exc}")
        with self.assertRaisesRegex(study.StudyError, "심볼릭 링크"):
            self.coach().path(f"problems/{PID}/problem.md")

    def test_unknown_local_and_submission_status_make_no_pass_claim(self):
        coach = self.register()
        coach.apply(PID, "completion", "complete-unknown", completion())
        stored = self.load()["problems"][PID]["studies"]["cpp"]["completion"]
        for key in ("local_examples", "submission"):
            self.assertEqual("unknown", stored[key]["status"])
            self.assertEqual("not_checked", stored[key]["source"])
            self.assertEqual("", stored[key]["evidence"])

    def test_lock_rejects_contention_and_is_released_after_process_termination(self):
        script = (
            "import sys,time\n"
            "from scripts.study import Coach\n"
            "with Coach(sys.argv[1], '2026-01-01').lock():\n"
            " print('READY', flush=True)\n"
            " time.sleep(30)\n"
        )
        process = subprocess.Popen(
            [sys.executable, "-u", "-c", script, str(self.root)],
            cwd=Path.cwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            self.assertEqual("READY", process.stdout.readline().strip())
            with self.assertRaisesRegex(study.StudyError, "다른 study.py 작업"):
                with self.coach().lock():
                    self.fail("contended lock was unexpectedly acquired")
        finally:
            process.terminate()
            process.wait(timeout=10)
            process.stdout.close()
            process.stderr.close()
        with self.coach().lock():
            pass


if __name__ == "__main__":
    unittest.main()
