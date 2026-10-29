"""Conservative Programmers problem-page ingestion.

Downloaded page content is untrusted external data.  It is parsed only to
extract explicitly labelled problem-statement fields; it is never treated as
instructions for the agent or as executable content.
"""

from __future__ import annotations

import html
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Dict, Iterable, List, Optional, Tuple, Union


_CANONICAL_HOST = "school.programmers.co.kr"
_ALLOWED_HOSTS = {_CANONICAL_HOST, "programmers.co.kr"}
_LESSON_PATH = re.compile(r"/learn/courses/30/lessons/([0-9]+)/?")
_MAX_RESPONSE_BYTES = 2 * 1024 * 1024
_IGNORED_TAGS = {"script", "style", "noscript", "svg", "form", "textarea", "button", "input"}
_VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def normalize_url(url: str) -> Tuple[str, str]:
    """Return ``(problem_id, canonical_url)`` for a supported lesson URL."""

    if not isinstance(url, str) or not url.strip():
        raise ValueError("프로그래머스 문제 URL이 필요합니다.")
    try:
        parsed = urllib.parse.urlsplit(url.strip())
    except ValueError as exc:
        raise ValueError("올바르지 않은 URL입니다.") from exc

    if parsed.scheme.lower() != "https":
        raise ValueError("HTTPS 프로그래머스 문제 URL만 지원합니다.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("사용자 정보가 포함된 URL은 지원하지 않습니다.")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("올바르지 않은 포트입니다.") from exc
    if port is not None:
        raise ValueError("포트가 지정된 URL은 지원하지 않습니다.")

    host = (parsed.hostname or "").lower().rstrip(".")
    if host not in _ALLOWED_HOSTS:
        raise ValueError("지원하는 프로그래머스 호스트가 아닙니다.")
    match = _LESSON_PATH.fullmatch(parsed.path)
    if not match:
        raise ValueError("지원하는 프로그래머스 문제 경로가 아닙니다.")

    lesson_id = int(match.group(1), 10)
    if lesson_id <= 0:
        raise ValueError("문제 번호는 양의 정수여야 합니다.")
    numeric_id = str(lesson_id)
    canonical = (
        f"https://{_CANONICAL_HOST}/learn/courses/30/lessons/{numeric_id}"
    )
    return f"programmers-{numeric_id}", canonical


class _UnsafeRedirectError(Exception):
    pass


class _RestrictedRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, expected_url: str) -> None:
        self.expected_url = expected_url

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        absolute = urllib.parse.urljoin(req.full_url, newurl)
        try:
            _, normalized = normalize_url(absolute)
        except ValueError as exc:
            raise _UnsafeRedirectError("안전하지 않은 페이지로 이동되어 본문을 가져오지 않았습니다.") from exc
        if normalized != self.expected_url:
            raise _UnsafeRedirectError("다른 문제 페이지로 이동되어 본문을 가져오지 않았습니다.")
        return super().redirect_request(req, fp, code, msg, headers, absolute)


def _open_url(url: str):
    opener = urllib.request.build_opener(_RestrictedRedirectHandler(url))
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "algorithm-coach/1.0 (+local-study-tool)"},
    )
    return opener.open(request, timeout=15)


@dataclass
class _Element:
    tag: str
    attrs: Dict[str, str] = field(default_factory=dict)
    children: List[Union["_Element", str]] = field(default_factory=list)


class _StatementParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.blocks: List[_Element] = []
        self.description_marked_blocks: List[bool] = []
        self._stack: List[_Element] = []
        self._capture_depth = 0
        self._ignored_depth = 0
        self._ignored_tags: List[str] = []
        self._guide_heading_depth = 0
        self._guide_heading_text: List[str] = []
        self._description_marker_pending = False
        self.issues: List[str] = []
        self.image_count = 0

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        attr_map = {key: (value or "") for key, value in attrs}
        classes = set(attr_map.get("class", "").split())
        if "lesson-content" in classes and attr_map.get("data-lesson-title", "").strip():
            candidate = attr_map["data-lesson-title"].strip()
            self.title = candidate if not self.title else self.title

        if self._capture_depth == 0:
            if self._guide_heading_depth:
                self._guide_heading_depth += 1
                return
            if tag == "h6" and "guide-section-title" in classes:
                self._guide_heading_depth = 1
                self._guide_heading_text = []
                self._description_marker_pending = False
                return
            if tag == "div" and "markdown" in classes:
                root = _Element(tag, attr_map)
                self.blocks.append(root)
                self.description_marked_blocks.append(self._description_marker_pending)
                self._stack = [root]
                self._capture_depth = 1
                self._description_marker_pending = False
            elif self._description_marker_pending:
                # The verified external marker applies only to the immediately
                # following statement block (ignoring whitespace).
                self._description_marker_pending = False
            return

        if tag in _VOID_TAGS:
            if not self._ignored_depth:
                if tag == "br":
                    self._stack[-1].children.append(_Element("br"))
                elif tag == "img":
                    self._stack[-1].children.append(_Element("img", attr_map))
                    self.image_count += 1
            return
        self._capture_depth += 1
        if self._ignored_depth:
            self._ignored_depth += 1
            self._ignored_tags.append(tag)
            return
        if tag in _IGNORED_TAGS:
            self._ignored_depth = 1
            self._ignored_tags = [tag]
            return
        node = _Element(tag, attr_map)
        self._stack[-1].children.append(node)
        self._stack.append(node)

    def handle_startendtag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        if not self._capture_depth or self._ignored_depth:
            return
        attr_map = {key: (value or "") for key, value in attrs}
        if tag == "br":
            self._stack[-1].children.append(_Element("br"))
        elif tag == "img":
            self._stack[-1].children.append(_Element("img", attr_map))
            self.image_count += 1

    def handle_endtag(self, tag: str) -> None:
        if self._capture_depth == 0:
            if self._guide_heading_depth:
                self._guide_heading_depth -= 1
                if self._guide_heading_depth == 0:
                    marker = re.sub(r"\s+", "", "".join(self._guide_heading_text)).strip("#:：")
                    self._description_marker_pending = marker == "문제설명"
                return
            if self._description_marker_pending:
                self._description_marker_pending = False
            return
        if self._ignored_depth:
            expected = self._ignored_tags.pop() if self._ignored_tags else ""
            if expected != tag:
                self.issues.append("무시 대상 요소의 HTML 중첩이 올바르지 않습니다.")
            self._ignored_depth -= 1
        elif self._stack:
            expected = self._stack[-1].tag
            if expected == tag:
                if len(self._stack) > 1:
                    self._stack.pop()
            else:
                self.issues.append("문제 본문 HTML 중첩이 올바르지 않습니다.")
        self._capture_depth -= 1
        if self._capture_depth == 0:
            self._stack = []

    def handle_data(self, data: str) -> None:
        if self._capture_depth and not self._ignored_depth and self._stack:
            self._stack[-1].children.append(data)
        elif self._guide_heading_depth:
            self._guide_heading_text.append(data)
        elif self._description_marker_pending and data.strip():
            self._description_marker_pending = False

    def close(self) -> None:
        super().close()
        if self._capture_depth or self._ignored_depth or self._stack:
            self.issues.append("문제 본문 HTML이 닫히지 않았습니다.")


def _plain_text(node: Union[_Element, str]) -> str:
    if isinstance(node, str):
        return node
    if node.tag == "br":
        return "\n"
    return "".join(_plain_text(child) for child in node.children)


def _clean_inline(value: str) -> str:
    return re.sub(r"[ \t\r\f\v]+", " ", html.unescape(value)).strip()


def _direct_descendants(node: _Element, tag: str) -> Iterable[_Element]:
    for child in node.children:
        if isinstance(child, _Element):
            if child.tag == tag:
                yield child
            else:
                yield from _direct_descendants(child, tag)


def _render_table(node: _Element) -> str:
    rows: List[List[str]] = []
    for row in _direct_descendants(node, "tr"):
        cells: List[str] = []
        for child in row.children:
            if isinstance(child, _Element) and child.tag in {"th", "td"}:
                value = _clean_inline(_plain_text(child)).replace("\n", "<br>")
                cells.append(value.replace("|", "\\|"))
        if cells:
            rows.append(cells)
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    padded = [row + [""] * (width - len(row)) for row in rows]
    lines = ["| " + " | ".join(padded[0]) + " |"]
    lines.append("| " + " | ".join(["---"] * width) + " |")
    lines.extend("| " + " | ".join(row) + " |" for row in padded[1:])
    return "\n".join(lines)


def _render(node: Union[_Element, str], list_depth: int = 0) -> str:
    if isinstance(node, str):
        return node
    tag = node.tag
    if tag == "br":
        return "\n"
    if tag == "img":
        alt = _clean_inline(node.attrs.get("alt", "")) or "없음"
        source = _clean_inline(node.attrs.get("src", "")) or "없음"
        return f"[이미지: 대체 텍스트={alt}; URL={source}]"
    if tag == "table":
        return _render_table(node) + "\n\n"
    content = "".join(_render(child, list_depth) for child in node.children)
    cleaned = _clean_inline(content) if tag not in {"pre", "code"} else content.strip()
    if tag in {"p", "div", "section", "article"}:
        return cleaned + "\n\n" if cleaned else ""
    if tag in {"ul", "ol"}:
        return content + ("\n" if content else "")
    if tag == "li":
        return f"{'  ' * list_depth}- {cleaned}\n" if cleaned else ""
    if tag == "pre":
        return f"```\n{content.strip()}\n```\n\n" if content.strip() else ""
    if tag == "code":
        return f"`{cleaned}`" if cleaned else ""
    if tag in {"strong", "b"}:
        return f"**{cleaned}**" if cleaned else ""
    if tag in {"em", "i"}:
        return f"*{cleaned}*" if cleaned else ""
    if tag == "blockquote":
        return "\n".join(f"> {line}" for line in cleaned.splitlines()) + "\n\n"
    if re.fullmatch(r"h[1-6]", tag):
        return f"{'#' * int(tag[1])} {cleaned}\n\n" if cleaned else ""
    return content


def _heading_key(node: Union[_Element, str]) -> Optional[str]:
    if not isinstance(node, _Element) or not re.fullmatch(r"h[1-6]", node.tag):
        return None
    normalized = re.sub(r"\s+", "", _plain_text(node)).strip("#:：")
    if normalized == "문제설명":
        return "description"
    if normalized in {"제한사항", "제한조건"}:
        return "constraints"
    if normalized in {"입출력예", "입출력예시", "예제", "예시"}:
        return "examples"
    return "other"


def _parse_problem(document: str) -> Tuple[str, str, str, str, str]:
    parser = _StatementParser()
    try:
        parser.feed(document)
        parser.close()
    except (AssertionError, ValueError) as exc:
        return (
            "",
            "",
            "",
            "",
            f"문제 페이지 HTML을 안전하게 해석하지 못했습니다 ({type(exc).__name__}).",
        )
    if len(parser.blocks) != 1:
        return parser.title, "", "", "", "문제 본문 블록을 명확히 확인하지 못했습니다."

    sections: Dict[str, List[Union[_Element, str]]] = {
        "description": [],
        "constraints": [],
        "examples": [],
    }
    active: Optional[str] = (
        "description" if parser.description_marked_blocks[0] else None
    )
    for node in parser.blocks[0].children:
        heading = _heading_key(node)
        if heading is not None:
            if heading in sections:
                active = heading
            elif active is not None:
                # A statement may contain legitimate explanatory subsections.
                # Preserve them in the currently labelled section.
                sections[active].append(node)
            continue
        if active is not None:
            sections[active].append(node)

    rendered = {
        key: re.sub(r"\n{3,}", "\n\n", "".join(_render(n) for n in nodes)).strip()
        for key, nodes in sections.items()
    }
    issues = list(dict.fromkeys(parser.issues))
    if parser.image_count:
        issues.append(
            "문제 본문에 이미지가 있어 의미를 확인할 수 없습니다. 이미지 내용을 텍스트로 제공해 주세요."
        )
    return (
        parser.title.strip(),
        rendered["description"],
        rendered["constraints"],
        rendered["examples"],
        " ".join(issues),
    )


def _result(source_url: str, reason: str = "", **fields: str) -> Dict[str, str]:
    result = {
        "title": fields.get("title", ""),
        "description": fields.get("description", ""),
        "constraints": fields.get("constraints", ""),
        "examples": fields.get("examples", ""),
        "status": "needs_content",
        "reason": reason,
        "source_url": source_url,
    }
    missing = [name for name in ("title", "description", "constraints", "examples") if not result[name]]
    if not missing and not reason:
        result["status"] = "complete"
    elif not result["reason"]:
        labels = {"title": "제목", "description": "문제 설명", "constraints": "제약조건", "examples": "예제"}
        result["reason"] = "확인하지 못한 항목: " + ", ".join(labels[name] for name in missing)
    return result


def fetch_problem(url: str) -> Dict[str, str]:
    """Fetch a supported page, returning ``needs_content`` on retrieval failure."""

    _, canonical = normalize_url(url)
    try:
        with _open_url(canonical) as response:
            final_url = response.geturl()
            try:
                _, normalized_final = normalize_url(final_url)
            except ValueError:
                return _result(canonical, "로그인 또는 지원하지 않는 페이지로 이동되어 본문을 가져오지 않았습니다.")
            if normalized_final != canonical:
                return _result(canonical, "다른 문제 페이지로 이동되어 본문을 가져오지 않았습니다.")
            payload = response.read(_MAX_RESPONSE_BYTES + 1)
            if len(payload) > _MAX_RESPONSE_BYTES:
                return _result(canonical, "응답 크기가 제한을 초과했습니다.")
            charset = response.headers.get_content_charset() or "utf-8"
            try:
                document = payload.decode(charset)
            except (LookupError, UnicodeDecodeError):
                return _result(canonical, "문제 페이지의 문자 인코딩을 확인하지 못했습니다.")
    except _UnsafeRedirectError as exc:
        return _result(canonical, str(exc))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
        return _result(canonical, f"문제 페이지를 가져오지 못했습니다: {type(exc).__name__}")

    title, description, constraints, examples, parse_reason = _parse_problem(document)
    return _result(
        canonical,
        parse_reason,
        title=title,
        description=description,
        constraints=constraints,
        examples=examples,
    )
