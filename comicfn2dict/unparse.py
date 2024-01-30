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


def dict2comicfn(md: Mapping, ext: bool = True) -> str | None:
    """Get our preferred basename from a metadata dict."""
    if not md:
        return None
    tokens = []
    for tag, fmt in _FILENAME_FORMAT_TAGS:
        val = md.get(tag)
        if val in _EMPTY_VALUES:
            continue
        final_fmt = fmt(val) if isinstance(fmt, Callable) else fmt
        token = final_fmt.format(val).strip()
        if token:
            tokens.append(token)
    fn = " ".join(tokens)
    if remainders := md.get("remainders"):
        remainder = " ".join(remainders)
        fn += f" - {remainder}"
    if ext:
        fn += "." + md.get("ext", "cbz")
    return fn
