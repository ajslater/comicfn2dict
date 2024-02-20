"""Unparse comic filenames."""
from collections.abc import Callable, Mapping


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
    ("issue", issue_formatter),
    ("issue_count", "(of {:03})"),
    ("year", _PAREN_FMT),
    ("title", "{}"),
    ("original_format", _PAREN_FMT),
    ("scan_info", _PAREN_FMT),
)
_EMPTY_VALUES: tuple[None, str] = (None, "")
_DEFAULT_EXT = "cbz"


class ComicFilenameSerializer:
    def _tokenize_tag(self, tag: str, fmt: str | Callable) -> str:
        val = self.metadata.get(tag)
        if val in _EMPTY_VALUES:
            return ""
        final_fmt = fmt(val) if isinstance(fmt, Callable) else fmt
        token = final_fmt.format(val).strip()
        return token

    def serialize(self) -> str:
        """Get our preferred basename from a metadata dict."""
        tokens = []
        for tag, fmt in _FILENAME_FORMAT_TAGS:
            if token := self._tokenize_tag(tag, fmt):
                tokens.append(token)
        fn = " ".join(tokens)

        if remainders := self.metadata.get("remainders"):
            # TODO make token and add before join?
            remainder = " ".join(remainders)
            # TODO oh this is the - delineated remainder :(
            fn += f" - {remainder}"

        if self._ext:
            fn += "." + self.metadata.get("ext", _DEFAULT_EXT)

        return fn

    def __init__(self, metadata: Mapping, ext: bool = True):
        self.metadata: Mapping = metadata
        self._ext: bool = ext


def dict2comicfn(md: Mapping, ext: bool = True) -> str:
    """Simple API."""
    return ComicFilenameSerializer(md, ext=ext).serialize()
