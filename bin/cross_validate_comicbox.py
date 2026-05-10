#!/usr/bin/env python3
"""
Cross-validate the parser against comicbox-extracted metadata.

For every tagged archive under a directory, extract its embedded metadata via
comicbox, run :func:`comicfn2dict.comicfn2dict` on the filename, and report
disagreements. The tool's job is to surface where the parser diverges from
human-or-tool-curated ground truth so we can decide whether to fix the parser
or note the case as ambiguous.

Usage::

    bin/cross_validate_comicbox.py [--limit N] [--out PATH] [DIR ...]

Defaults to ``~/Milliways/Comics/Test`` and ``~/Milliways/Comics/slimlib`` and
no limit. Run with ``uv run --with comicbox`` so ``comicbox`` is importable.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from comicbox.box import (  # pyright: ignore[reportMissingImports], #ty: ignore[unresolved-import]
    Comicbox,
)

from comicfn2dict import comicfn2dict

_COMIC_SUFFIXES = frozenset({".cbz", ".cbr", ".cbt"})
_DEFAULT_DIRS = (
    Path.home() / "Milliways/Comics/Test",
    Path.home() / "Milliways/Comics/slimlib",
)
_COMPARE_KEYS = ("series", "issue", "year", "volume", "title", "publisher")


def _comicbox_metadata(path: Path) -> dict[str, Any] | None:
    try:
        with Comicbox(str(path)) as cb:
            md = cb.to_dict() or {}
    except Exception as exc:
        print(f"  ! comicbox error on {path.name}: {exc}", file=sys.stderr)
        return None
    return md.get("comicbox") if isinstance(md, dict) else None


def _normalize(key: str, value: Any) -> str:
    if value is None:
        return ""
    if key == "issue":
        return (str(value).lstrip("0") or "0").removesuffix(".0")
    if key == "year":
        return str(value)
    return str(value).strip()


def _ground_truth(cb: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    if (series := cb.get("series")) and isinstance(series, dict):
        out["series"] = _normalize("series", series.get("name"))
    if (issue := cb.get("issue")) and isinstance(issue, dict):
        out["issue"] = _normalize("issue", issue.get("number") or issue.get("name"))
    if (date := cb.get("date")) and isinstance(date, dict) and date.get("year"):
        out["year"] = _normalize("year", date["year"])
    if (volume := cb.get("volume")) and isinstance(volume, dict):
        out["volume"] = _normalize("volume", volume.get("number"))
    if title := cb.get("title"):
        out["title"] = _normalize("title", title)
    if (publisher := cb.get("publisher")) and isinstance(publisher, dict):
        out["publisher"] = _normalize("publisher", publisher.get("name"))
    return {k: v for k, v in out.items() if v}


def _parser_output(filename: str) -> dict[str, str]:
    raw = comicfn2dict(filename)
    return {k: _normalize(k, raw.get(k)) for k in _COMPARE_KEYS if raw.get(k)}


def _diff(truth: dict[str, str], parsed: dict[str, str]) -> dict[str, tuple[str, str]]:
    diff: dict[str, tuple[str, str]] = {}
    for key in _COMPARE_KEYS:
        t = truth.get(key, "")
        p = parsed.get(key, "")
        if not t or not p:
            # Both must have a value for a meaningful diff (filename can't tell
            # us about title pulled from internal tags, etc.)
            continue
        if t == p:
            continue
        diff[key] = (t, p)
    return diff


def _walk(dirs: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for d in dirs:
        if not d.exists():
            print(f"  (skipping missing {d})", file=sys.stderr)
            continue
        paths.extend(p for p in d.rglob("*") if p.suffix.lower() in _COMIC_SUFFIXES)
    return paths


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dirs", nargs="*", type=Path, default=list(_DEFAULT_DIRS))
    ap.add_argument("--limit", type=int, default=0, help="cap files processed")
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("/tmp/cfn_analysis/cb_diff.json"),
        help="JSON output file with per-file diffs",
    )
    args = ap.parse_args()

    paths = _walk(args.dirs)
    if args.limit:
        paths = paths[: args.limit]
    print(f"Scanning {len(paths)} files...")

    diffs: list[dict[str, Any]] = []
    skipped = 0
    untagged = 0
    matched = 0
    field_disagreements: Counter[str] = Counter()
    field_examples: dict[str, list[tuple[str, str, str]]] = {}

    for i, path in enumerate(paths):
        if i and i % 200 == 0:
            print(f"  {i}/{len(paths)}...")
        cb = _comicbox_metadata(path)
        if cb is None:
            skipped += 1
            continue
        truth = _ground_truth(cb)
        if not truth.get("series"):
            untagged += 1
            continue
        parsed = _parser_output(path.name)
        diff = _diff(truth, parsed)
        if not diff:
            matched += 1
            continue
        diffs.append(
            {"file": path.name, "truth": truth, "parsed": parsed, "diff": diff}
        )
        for key, (t, p) in diff.items():
            field_disagreements[key] += 1
            field_examples.setdefault(key, []).append((path.name, t, p))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(diffs, indent=2, ensure_ascii=False))
    print()
    print(f"Total scanned : {len(paths)}")
    print(f"  comicbox skipped: {skipped}")
    print(f"  untagged        : {untagged}")
    print(f"  parser matched  : {matched}")
    print(f"  disagreements   : {len(diffs)}")
    print()
    print("Disagreements by field:")
    for key, n in field_disagreements.most_common():
        print(f"  {key:10s} {n:5d}")
        for fn, t, p in field_examples[key][:5]:
            print(f"    {fn}")
            print(f"        truth : {t!r}")
            print(f"        parsed: {p!r}")
    print()
    print(f"Full diff written to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
