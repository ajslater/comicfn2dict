"""
Optional smoke test against a real comic library.

Set the ``COMICFN2DICT_CORPUS_DIR`` environment variable to a directory tree
containing ``.cbz``/``.cbr``/``.cbt``/``.pdf`` files (e.g. an actual comic
library) and pytest will walk it, parse every basename, and assert the parser
runs without exceptions and extracts at least one field for each filename.

If the env var is unset the test is skipped, so this stays out of CI by
default. The optional ``COMICFN2DICT_CORPUS_LIMIT`` env var caps the number of
files parsed (handy when pointing at very large libraries).
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from comicfn2dict import comicfn2dict

_CORPUS_ENV = "COMICFN2DICT_CORPUS_DIR"
_LIMIT_ENV = "COMICFN2DICT_CORPUS_LIMIT"
_COMIC_SUFFIXES = frozenset({".cbz", ".cbr", ".cbt", ".pdf"})


def _corpus_filenames() -> list[str]:
    root = os.environ.get(_CORPUS_ENV)
    if not root:
        return []
    limit_str = os.environ.get(_LIMIT_ENV)
    limit = int(limit_str) if limit_str else None
    seen: set[str] = set()
    for path in Path(root).rglob("*"):
        if path.suffix.lower() not in _COMIC_SUFFIXES:
            continue
        seen.add(path.name)
        if limit and len(seen) >= limit:
            break
    return sorted(seen)


@pytest.mark.skipif(
    not os.environ.get(_CORPUS_ENV),
    reason=f"set {_CORPUS_ENV} to a comic library path to enable",
)
def test_corpus_smoke():
    """Parse every filename in the corpus; report any failures."""
    filenames = _corpus_filenames()
    assert filenames, f"no comic files found under {os.environ[_CORPUS_ENV]!r}"

    failures: list[tuple[str, str]] = []
    empty: list[str] = []
    for fn in filenames:
        try:
            md = comicfn2dict(fn)
        except Exception as exc:
            failures.append((fn, repr(exc)))
            continue
        # ext is set unconditionally; require at least one other field
        # (series, issue, year, etc.) — if ext is the only key, the parser
        # extracted nothing usable.
        if set(md) <= {"ext"}:
            empty.append(fn)

    summary = (
        f"{len(filenames)} files parsed, "
        f"{len(failures)} crashed, "
        f"{len(empty)} extracted only the extension"
    )
    print(summary)
    assert not failures, "\n".join(f"  {fn} -> {err}" for fn, err in failures[:20])
