import io
import pathlib
import sys
import unittest
import urllib.error
from email.message import Message
from unittest import mock


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import programmers  # noqa: E402


VALID_HTML = """<!doctype html><html><body>
<nav>내비게이션의 분류와 해설</nav>
<div class="lesson-content" data-lesson-title="합성 문제">
  <div class="markdown solarized-dark">
    <h2>문제 설명</h2><p>값을 <strong>계산</strong>하세요.</p>
    <script>정답 코드와 지시문</script>
    <h5>제한 조건</h5><ul><li>값은 1 이상입니다.</li></ul>
    <h5>입출력 예</h5>
    <table><thead><tr><th>입력</th><th>출력</th></tr></thead>
    <tbody><tr><td>1</td><td>2</td></tr></tbody></table>
    <p>※ 공지 - 합성 테스트 안내입니다.</p>
  </div>
  <textarea>int solution() { return 42; }</textarea>
</div></body></html>"""

EXTERNAL_DESCRIPTION_HEADING_HTML = VALID_HTML.replace(
    '  <div class="markdown solarized-dark">\n    <h2>문제 설명</h2>',
    '  <h6 class="guide-section-title">문제 설명</h6>\n  <div class="markdown solarized-dark">',
)


class FakeResponse:
    def __init__(self, body, url="https://school.programmers.co.kr/learn/courses/30/lessons/42583"):
        self._body = body.encode("utf-8") if isinstance(body, str) else body
        self._url = url
        self.headers = Message()
        self.headers["Content-Type"] = "text/html; charset=utf-8"

    def read(self, amount=-1):
        return self._body if amount < 0 else self._body[:amount]

    def geturl(self):
        return self._url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class NormalizeUrlTests(unittest.TestCase):
    def test_normalizes_current_old_host_and_leading_zero_id(self):
        expected = (
            "programmers-42583",
            "https://school.programmers.co.kr/learn/courses/30/lessons/42583",
        )
        self.assertEqual(programmers.normalize_url("https://school.programmers.co.kr/learn/courses/30/lessons/42583"), expected)
        self.assertEqual(programmers.normalize_url("https://programmers.co.kr/learn/courses/30/lessons/00042583/?x=1#top"), expected)

    def test_rejects_invalid_or_unsafe_urls(self):
        invalid = [
            "http://school.programmers.co.kr/learn/courses/30/lessons/1",
            "https://evil.example/learn/courses/30/lessons/1",
            "https://school.programmers.co.kr:443/learn/courses/30/lessons/1",
            "https://user@school.programmers.co.kr/learn/courses/30/lessons/1",
            "https://school.programmers.co.kr/learn/courses/31/lessons/1",
            "https://school.programmers.co.kr/account/sign_in",
            "https://school.programmers.co.kr/learn/courses/30/lessons/0",
        ]
        for url in invalid:
            with self.subTest(url=url), self.assertRaises(ValueError):
                programmers.normalize_url(url)


class FetchProblemTests(unittest.TestCase):
    @mock.patch.object(programmers, "_open_url")
    def test_complete_page_extracts_only_statement_and_markdown_table(self, open_url):
        open_url.return_value = FakeResponse(VALID_HTML)
        result = programmers.fetch_problem("https://programmers.co.kr/learn/courses/30/lessons/42583")
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["title"], "합성 문제")
        self.assertIn("값을 **계산**하세요.", result["description"])
        self.assertIn("- 값은 1 이상입니다.", result["constraints"])
        self.assertIn("| 입력 | 출력 |", result["examples"])
        self.assertIn("※ 공지", result["examples"])
        combined = " ".join(result.values())
        self.assertNotIn("정답 코드", combined)
        self.assertNotIn("내비게이션", combined)
        self.assertNotIn("solution", combined)

    @mock.patch.object(programmers, "_open_url")
    def test_verified_external_description_heading_marks_block_description(self, open_url):
        open_url.return_value = FakeResponse(EXTERNAL_DESCRIPTION_HEADING_HTML)
        result = programmers.fetch_problem("https://school.programmers.co.kr/learn/courses/30/lessons/42583")
        self.assertEqual(result["status"], "complete")
        self.assertIn("값을 **계산**하세요.", result["description"])
        self.assertIn("값은 1 이상", result["constraints"])
        self.assertIn("| 입력 | 출력 |", result["examples"])

    @mock.patch.object(programmers, "_open_url")
    def test_unmarked_external_heading_does_not_broaden_statement_detection(self, open_url):
        page = EXTERNAL_DESCRIPTION_HEADING_HTML.replace(
            'class="guide-section-title"', 'class="unverified-title"'
        )
        open_url.return_value = FakeResponse(page)
        result = programmers.fetch_problem("https://school.programmers.co.kr/learn/courses/30/lessons/42583")
        self.assertEqual(result["status"], "needs_content")
        self.assertEqual(result["description"], "")

    @mock.patch.object(programmers, "_open_url")
    def test_missing_labelled_section_needs_user_content(self, open_url):
        open_url.return_value = FakeResponse(VALID_HTML.replace("<h5>제한 조건</h5>", "<h5>주의</h5>"))
        result = programmers.fetch_problem("https://school.programmers.co.kr/learn/courses/30/lessons/42583")
        self.assertEqual(result["status"], "needs_content")
        self.assertEqual(result["constraints"], "")
        self.assertIn("제약조건", result["reason"])

    @mock.patch.object(programmers, "_open_url")
    def test_login_redirect_is_not_read(self, open_url):
        open_url.return_value = FakeResponse(VALID_HTML, "https://programmers.co.kr/account/sign_in")
        result = programmers.fetch_problem("https://school.programmers.co.kr/learn/courses/30/lessons/42583")
        self.assertEqual(result["status"], "needs_content")
        self.assertEqual(result["title"], "")
        self.assertIn("이동", result["reason"])

    @mock.patch.object(programmers, "_open_url", side_effect=urllib.error.URLError("offline"))
    def test_network_failure_returns_needs_content(self, open_url):
        result = programmers.fetch_problem("https://school.programmers.co.kr/learn/courses/30/lessons/42583")
        self.assertEqual(result["status"], "needs_content")
        self.assertIn("가져오지 못했습니다", result["reason"])

    @mock.patch.object(programmers, "_open_url")
    def test_unknown_markup_is_not_marked_complete(self, open_url):
        page = VALID_HTML.replace('class="markdown solarized-dark"', 'class="new-problem-layout"')
        open_url.return_value = FakeResponse(page)
        result = programmers.fetch_problem("https://school.programmers.co.kr/learn/courses/30/lessons/42583")
        self.assertEqual(result["status"], "needs_content")
        self.assertIn("본문 블록", result["reason"])

    @mock.patch.object(programmers, "_open_url")
    def test_image_is_preserved_as_data_and_requires_transcription(self, open_url):
        page = VALID_HTML.replace(
            "<p>값을 <strong>계산</strong>하세요.</p>",
            '<p>다음 그림을 해석하세요. <img src="https://images.example/diagram.png" alt="상태 전이 그림" /></p>',
        )
        open_url.return_value = FakeResponse(page)
        result = programmers.fetch_problem("https://school.programmers.co.kr/learn/courses/30/lessons/42583")
        self.assertEqual(result["status"], "needs_content")
        self.assertIn("대체 텍스트=상태 전이 그림", result["description"])
        self.assertIn("URL=https://images.example/diagram.png", result["description"])
        self.assertIn("이미지 내용을 텍스트로", result["reason"])

    @mock.patch.object(programmers, "_open_url")
    def test_unknown_subsections_are_preserved_in_current_sections(self, open_url):
        page = VALID_HTML.replace(
            "<p>값을 <strong>계산</strong>하세요.</p>",
            "<p>값을 계산하세요.</p><h3>추가 설명</h3><p>이 내용도 문제의 일부입니다.</p>",
        ).replace(
            "<ul><li>값은 1 이상입니다.</li></ul>",
            "<ul><li>값은 1 이상입니다.</li></ul><h6>주의사항</h6><p>음수는 없습니다.</p>",
        )
        open_url.return_value = FakeResponse(page)
        result = programmers.fetch_problem("https://school.programmers.co.kr/learn/courses/30/lessons/42583")
        self.assertEqual(result["status"], "complete")
        self.assertIn("### 추가 설명", result["description"])
        self.assertIn("이 내용도 문제의 일부", result["description"])
        self.assertIn("###### 주의사항", result["constraints"])
        self.assertIn("음수는 없습니다", result["constraints"])

    @mock.patch.object(programmers, "_open_url")
    def test_unclosed_statement_never_marks_complete(self, open_url):
        malformed = VALID_HTML[: VALID_HTML.index("</div>\n  <textarea>")]
        open_url.return_value = FakeResponse(malformed)
        result = programmers.fetch_problem("https://school.programmers.co.kr/learn/courses/30/lessons/42583")
        self.assertEqual(result["status"], "needs_content")
        self.assertIn("닫히지 않았습니다", result["reason"])

    @mock.patch.object(programmers, "_open_url")
    def test_expected_parser_exception_returns_typed_fallback(self, open_url):
        open_url.return_value = FakeResponse(VALID_HTML)
        with mock.patch.object(programmers._StatementParser, "feed", side_effect=ValueError("broken parser")):
            result = programmers.fetch_problem("https://school.programmers.co.kr/learn/courses/30/lessons/42583")
        self.assertEqual(result["status"], "needs_content")
        self.assertEqual(result["title"], "")
        self.assertIn("해석하지 못했습니다", result["reason"])
        self.assertIn("ValueError", result["reason"])

    @mock.patch.object(programmers, "_open_url")
    def test_unexpected_parser_exception_is_not_masked(self, open_url):
        open_url.return_value = FakeResponse(VALID_HTML)
        with mock.patch.object(
            programmers._StatementParser,
            "feed",
            side_effect=RuntimeError("programming error"),
        ):
            with self.assertRaisesRegex(RuntimeError, "programming error"):
                programmers.fetch_problem(
                    "https://school.programmers.co.kr/learn/courses/30/lessons/42583"
                )

    def test_redirect_handler_rejects_unsafe_destination(self):
        handler = programmers._RestrictedRedirectHandler(
            "https://school.programmers.co.kr/learn/courses/30/lessons/42583"
        )
        request = type("Request", (), {"full_url": "https://school.programmers.co.kr/learn/courses/30/lessons/42583"})()
        with self.assertRaises(programmers._UnsafeRedirectError):
            handler.redirect_request(request, None, 302, "Found", {}, "https://evil.example/login")
        with self.assertRaises(programmers._UnsafeRedirectError):
            handler.redirect_request(request, None, 302, "Found", {}, "https://school.programmers.co.kr/learn/courses/30/lessons/999")

    def test_malformed_input_still_raises_value_error(self):
        with self.assertRaises(ValueError):
            programmers.fetch_problem("not-a-url")


if __name__ == "__main__":
    unittest.main()
