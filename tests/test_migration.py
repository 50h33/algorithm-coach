"""Explicit v1-to-v2 migration and legacy-path preservation."""
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
    "title": "기존 문제", "description": "설명", "constraints": "제약", "examples": "예제",
}


def legacy_event(request_id, kind, payload, data=None):
    return {
        "request_id": request_id,
        "fingerprint": study.digest({"kind": kind, "payload": payload}),
        "kind": kind,
        "at": "2026-01-01T12:00:00+09:00",
        "on": "2026-01-01",
        "data": copy.deepcopy(payload if data is None else data),
    }


def legacy_state(active_review=True):
    completion = {
        "declaration": "완료했다.", "on": "2026-01-01",
        "local_examples": {"status": "unknown", "source": "not_checked", "evidence": ""},
        "submission": {"status": "unknown", "source": "not_checked", "evidence": ""},
    }
    body = {
        "initial_approach": "직접 구현", "stuck_points": ["조건"], "facts": ["수정함"],
        "hypotheses": [], "help_received": "없음", "correction_principle": "",
        "review_task": {"kind": "full", "prompt": "다시 구현"},
    }
    reviews = [{
        "number": 1, "started_on": "2026-01-02", "task": copy.deepcopy(body["review_task"]),
        "result": None if active_review else {
            "on": "2026-01-02", "success": True, "hint_used": False,
            "source": "user_report", "evidence": "사용자 보고", "independent": True,
        },
    }]
    registered = legacy_event("register", "registered", {}, {
        "content": copy.deepcopy(CONTENT), "source": "user_provided", "reason": "사용자가 제공한 본문",
    })
    started = legacy_event("review-start:1", "review_started", {}, copy.deepcopy(reviews[0]))
    hint_payload = {
        "question": "기존 질문", "hint": "기존 힌트", "level": 0, "topic": "syntax",
        "facts": [], "hypotheses": [], "issue": "other", "line_start": 1, "line_end": 1,
    }
    hint_data = {
        **hint_payload, "explicit_request": False,
        "source": f"problems/{PID}/reviews/attempt-001.cpp", "code": "// active review",
        "review": 1,
    }
    prior_hint = legacy_event("legacy-review-hint", "hint", hint_payload, hint_data)
    return {
        "version": 1, "timezone": "Asia/Seoul", "problems": {PID: {
            "url": URL, "content": copy.deepcopy(CONTENT), "content_status": "complete", "content_note": "",
            "phase": "review", "events": [registered, started, prior_hint], "completion": completion,
            "draft": {"version": 1, "body": copy.deepcopy(body)},
            "approved": {"version": 1, "body": copy.deepcopy(body), "principle": "상태부터 확인",
                         "confirmation": "확인", "on": "2026-01-01"},
            "schedule": {"due": "2026-01-02", "stage": 0, "independent_successes": 0,
                         "independent_full_successes": 0},
            "reviews": reviews,
        }},
    }


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.root = Path(self.temp.name)
        (self.root / "data").mkdir()
        (self.root / "problems" / PID / "reviews").mkdir(parents=True)
        self.index = self.root / "data/index.json"
        self.solution = self.root / "problems" / PID / "solution.cpp"
        self.attempt = self.root / "problems" / PID / "reviews/attempt-001.cpp"
        self.solution.write_bytes(b"// legacy solution\r\n")
        self.attempt.write_bytes(b"// active review\r\n")
        self.state = legacy_state()
        self.index.write_text(json.dumps(self.state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.original_index = self.index.read_bytes()

    def tearDown(self):
        self.temp.cleanup()

    def coach(self):
        return study.Coach(self.root, "2026-01-02")

    def test_dry_run_and_read_only_due_do_not_change_v1_files(self):
        result = self.coach().migrate(dry_run=True)
        self.assertEqual({
            "from_version": 1, "to_version": 2, "problems": 1, "studies": 1,
            "dry_run": True, "migrated": False, "backup": "data/index.v1.backup.json",
        }, result)
        due = self.coach().due()
        self.assertEqual((PID, "cpp"), (due["items"][0]["id"], due["items"][0]["language"]))
        self.assertEqual(self.original_index, self.index.read_bytes())
        self.assertFalse((self.root / "data/index.v1.backup.json").exists())
        self.assertEqual(b"// legacy solution\r\n", self.solution.read_bytes())
        self.assertEqual(b"// active review\r\n", self.attempt.read_bytes())

    def test_mutating_v1_requires_explicit_migration(self):
        before = self.index.read_bytes()
        with self.assertRaisesRegex(study.StudyError, "migrate"):
            self.coach().resume(PID)
        with self.assertRaisesRegex(study.StudyError, "migrate"):
            self.coach().apply(PID, "hint", "new", {
                "question": "질문", "hint": "힌트", "level": 0, "topic": "syntax",
                "facts": [], "hypotheses": [], "issue": "other", "line_start": 1, "line_end": 1,
            })
        self.assertEqual(before, self.index.read_bytes())

    def test_migration_preserves_events_and_legacy_source_paths(self):
        legacy_events = copy.deepcopy(self.state["problems"][PID]["events"])
        result = self.coach().migrate()
        self.assertTrue(result["migrated"])
        self.assertEqual("data/index.v1.backup.json", result["backup"])
        self.assertEqual(self.original_index, (self.root / result["backup"]).read_bytes())

        migrated = self.coach().load()
        problem = migrated["problems"][PID]
        cpp = problem["studies"]["cpp"]
        self.assertEqual(2, migrated["version"])
        self.assertEqual("legacy_cpp", cpp["layout"])
        for before, after in zip(legacy_events, problem["events"]):
            self.assertEqual(before, {key: after[key] for key in before})
            self.assertEqual(None if after["kind"] in ("registered", "content") else "cpp",
                             after["language"])
        resumed = self.coach().review_start(PID, "cpp")
        self.assertTrue(resumed["resumed"])
        self.assertEqual(f"problems/{PID}/reviews/attempt-001.cpp", resumed["file"])
        self.assertEqual(b"// legacy solution\r\n", self.solution.read_bytes())
        self.assertEqual(b"// active review\r\n", self.attempt.read_bytes())

        again = self.coach().migrate()
        self.assertEqual((2, 2, False), (again["from_version"], again["to_version"], again["migrated"]))

    def test_migration_failure_keeps_original_and_retry_succeeds(self):
        original_atomic = self.coach().atomic_text
        coach = self.coach()

        def fail_index(relative, content):
            if relative == "data/index.json":
                raise OSError("save failed")
            return original_atomic(relative, content)

        with mock.patch.object(coach, "atomic_text", side_effect=fail_index):
            with self.assertRaisesRegex(OSError, "save failed"):
                coach.migrate()
        self.assertEqual(self.original_index, self.index.read_bytes())
        self.assertEqual(self.original_index, (self.root / "data/index.v1.backup.json").read_bytes())

        result = self.coach().migrate()
        self.assertTrue(result["migrated"])
        self.assertEqual(2, self.coach().load()["version"])

    def test_conflicting_backup_is_never_overwritten(self):
        backup = self.root / "data/index.v1.backup.json"
        backup.write_bytes(b"unrelated backup")
        with self.assertRaisesRegex(study.StudyError, "백업"):
            self.coach().migrate()
        self.assertEqual(b"unrelated backup", backup.read_bytes())
        self.assertEqual(self.original_index, self.index.read_bytes())

    def test_partial_backup_write_is_removed_and_original_remains(self):
        with mock.patch("scripts.study.os.fsync", side_effect=OSError("sync failed")):
            with self.assertRaisesRegex(OSError, "sync failed"):
                self.coach().migrate()
        self.assertEqual(self.original_index, self.index.read_bytes())
        self.assertFalse((self.root / "data/index.v1.backup.json").exists())

        retry = self.coach().migrate()
        self.assertTrue(retry["migrated"])
        self.assertEqual(self.original_index, (self.root / retry["backup"]).read_bytes())

    def test_pre_migration_hint_replay_keeps_fingerprint_and_snapshot(self):
        original_hint = copy.deepcopy(self.state["problems"][PID]["events"][-1])
        self.coach().migrate()
        payload = {
            "question": "기존 질문", "hint": "기존 힌트", "level": 0, "topic": "syntax",
            "facts": [], "hypotheses": [], "issue": "other", "line_start": 1, "line_end": 1,
        }
        replayed = self.coach().apply(PID, "hint", "legacy-review-hint", payload, "cpp")
        self.assertTrue(replayed["replayed"])
        events = self.coach().load()["problems"][PID]["events"]
        hints = [event for event in events if event["request_id"] == "legacy-review-hint"]
        self.assertEqual(1, len(hints))
        self.assertEqual(original_hint["fingerprint"], hints[0]["fingerprint"])
        self.assertEqual(original_hint["data"], hints[0]["data"])


if __name__ == "__main__":
    unittest.main()
