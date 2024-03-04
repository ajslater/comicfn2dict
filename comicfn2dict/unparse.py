"""Unparse comic filenames."""

from __future__ import annotations

from calendar import month_abbr
from collections.abc import Callable, Mapping, Sequence
from contextlib import suppress
from types import MappingProxyType

from comicfn2dict.log import print_log_header


def issue_formatter(issue: str) -> str:
    """Formatter to zero pad issues."""
    i = 0
    issue = issue.lstrip("0")
    for c in issue:
        if not c.isdigit():
            break
        i += 1
    pad = 3 + len(issue) - i
    return "#{:0>" + str(pad) + "}"


_PAREN_FMT: str = "({})"
_FILENAME_FORMAT_TAGS: tuple[tuple[str, str | Callable], ...] = (
    ("series", "{}"),
    ("volume", "v{}"),
    ("volume_count", "(of {:03})"),
    ("issue", issue_formatter),
    ("issue_count", "(of {:03})"),
    ("date", _PAREN_FMT),
    ("title", "{}"),
    ("publisher", _PAREN_FMT),
    ("original_format", _PAREN_FMT),
    ("scan_info", _PAREN_FMT),
)
_EMPTY_VALUES: tuple[None, str] = (None, "")
_DEFAULT_EXT = "cbz"
_DATE_KEYS = ("year", "month", "day")


class ComicFilenameSerializer:
    """Serialize Comic Filenames from dict."""

    def _log(self, label: str, fn: str) -> None:
        """Log progress."""
        if not self._debug:
            return
        print_log_header(label)
        print(fn)  # noqa: T201

    def _add_date(self) -> None:
        """Construct date from Y-m-D if they exist."""
        if "date" in self.metadata:
            return
        parts = []
        for key in _DATE_KEYS:
            if part := self.metadata.get(key):
                if key == "month" and not parts:
                    with suppress(TypeError):
                        part = month_abbr[int(part)]

                parts.append(part)
            if key == "month" and not parts:
                # noop if only day.
                break
        if parts:
            parts = (str(part) for part in parts)
            date = "-".join(parts)
            self._log("After date", date)
            self.metadata = MappingProxyType({**self.metadata, "date": date})

    def _tokenize_tag(self, tag: str, fmt: str | Callable) -> str:
        """Add tags to the string."""
        val = self.metadata.get(tag)
        if val in _EMPTY_VALUES:
            return ""
        final_fmt = fmt(val) if isinstance(fmt, Callable) else fmt
        return final_fmt.format(val).strip()

    def _add_remainder(self) -> str:
        """Add the remainders specially."""
        if remainders := self.metadata.get("remainders"):
            if isinstance(remainders, Sequence):
                remainders = (str(remainder) for remainder in remainders)
                remainder = " ".join(remainders)
            else:
                remainder = str(remainders)
            return f"[{remainder}]"
        return ""

    def serialize(self) -> str:
        """Get our preferred basename from a metadata dict."""
        self._add_date()

        tokens = []
        for tag, fmt in _FILENAME_FORMAT_TAGS:
            if token := self._tokenize_tag(tag, fmt):
                tokens.append(token)
            self._log(f"After {tag}", str(tokens))
        fn = " ".join(tokens)

        fn += self._add_remainder()
        self._log("After remainder", fn)

        if self._ext:
            ext = self.metadata.get("ext", _DEFAULT_EXT)
            fn += f".{ext}"
            self._log("After ext", fn)

        return fn

    def __init__(self, metadata: Mapping, ext: bool = True, verbose: int = 0):
        """Initialize."""
        self.metadata: Mapping = metadata
        self._ext: bool = ext
        self._debug: bool = bool(verbose)


def dict2comicfn(md: Mapping, ext: bool = True, verbose: int = 0) -> str:
    """Simplify API."""
    serializer = ComicFilenameSerializer(md, ext=ext, verbose=verbose)
    return serializer.serialize()
