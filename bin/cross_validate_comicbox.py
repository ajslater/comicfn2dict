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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# When run as `python bin/cross_validate_comicbox.py`, Python doesn't put the
# project root on sys.path[0], so a comicfn2dict bundled in the comicbox
# environment can shadow the editable install. Force the project root to the
# very front so we always exercise the parser under development.
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
sys.path[:0] = [_PROJECT_ROOT]

from comicbox.box import (  # noqa: E402  # pyright: ignore[reportMissingImports], #ty: ignore[unresolved-import]
    Comicbox,
)

from comicfn2dict import comicfn2dict  # noqa: E402

_COMIC_SUFFIXES = frozenset({".cbz", ".cbr", ".cbt"})
_DEFAULT_DIRS = (
    Path.home() / "Milliways/Comics/Test",
    Path.home() / "Milliways/Comics/slimlib",
)
_COMPARE_KEYS = ("series", "issue", "year", "volume", "title", "publisher")
# Each output key, with the nested-dict path that holds it in the comicbox
# metadata. The last element is a tuple of sub-keys tried in order — the first
# truthy one is used. ``None`` in the path means the value is at the top level
# of the comicbox dict.
_GROUND_TRUTH_SPECS: tuple[tuple[str, str | None, tuple[str, ...]], ...] = (
    ("series", "series", ("name",)),
    ("issue", "issue", ("number", "name")),
    ("year", "date", ("year",)),
    ("volume", "volume", ("number",)),
    ("title", None, ("title",)),
    ("publisher", "publisher", ("name",)),
)


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


def _extract_truth_value(
    cb: dict[str, Any], parent: str | None, subkeys: tuple[str, ...]
) -> Any:
    """Pull a single value out of the nested comicbox dict, or None."""
    if parent is None:
        return cb.get(subkeys[0])
    section = cb.get(parent)
    if not isinstance(section, dict):
        return None
    for sub in subkeys:
        if (value := section.get(sub)) is not None:
            return value
    return None


def _ground_truth(cb: dict[str, Any]) -> dict[str, str]:
    """Extract the fields we can compare against the parser, normalised."""
    out: dict[str, str] = {}
    for key, parent, subkeys in _GROUND_TRUTH_SPECS:
        if (value := _extract_truth_value(cb, parent, subkeys)) is not None:
            normalized = _normalize(key, value)
            if normalized:
                out[key] = normalized
    return out


def _parser_output(filename: str) -> dict[str, str]:
    raw = comicfn2dict(filename)
    return {k: _normalize(k, raw.get(k)) for k in _COMPARE_KEYS if raw.get(k)}


def _is_colon_split_equivalent(truth: dict[str, str], parsed: dict[str, str]) -> bool:
    """True when parser series+title matches a colon-joined comicbox series."""
    truth_series = truth.get("series", "")
    parsed_series = parsed.get("series", "")
    parsed_title = parsed.get("title", "")
    return (
        ":" in truth_series
        and bool(parsed_series)
        and bool(parsed_title)
        and truth_series == f"{parsed_series}: {parsed_title}"
    )


def _diff(truth: dict[str, str], parsed: dict[str, str]) -> dict[str, tuple[str, str]]:
    # Treat a parser series/title split as equivalent to comicbox's colon-
    # joined "X: Y" series, so the field-by-field comparison doesn't flag it.
    if _is_colon_split_equivalent(truth, parsed):
        ignore = {"series", "title"}
        truth = {k: v for k, v in truth.items() if k not in ignore}
        parsed = {k: v for k, v in parsed.items() if k not in ignore}

    # A meaningful diff requires both sides to have a value; comicbox often
    # supplies fields the filename can't (title from internal tags, etc.).
    return {
        key: (truth[key], parsed[key])
        for key in _COMPARE_KEYS
        if truth.get(key) and parsed.get(key) and truth[key] != parsed[key]
    }


def _walk(dirs: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for d in dirs:
        if not d.exists():
            print(f"  (skipping missing {d})", file=sys.stderr)
            continue
        paths.extend(p for p in d.rglob("*") if p.suffix.lower() in _COMIC_SUFFIXES)
    return paths


@dataclass
class _Tally:
    """Accumulates per-file processing results."""

    diffs: list[dict[str, Any]] = field(default_factory=list)
    skipped: int = 0
    untagged: int = 0
    matched: int = 0
    field_disagreements: Counter[str] = field(default_factory=Counter)
    field_examples: dict[str, list[tuple[str, str, str]]] = field(default_factory=dict)


def _build_argparser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dirs", nargs="*", type=Path, default=list(_DEFAULT_DIRS))
    ap.add_argument("--limit", type=int, default=0, help="cap files processed")
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("/tmp/cfn_analysis/cb_diff.json"),
        help="JSON output file with per-file diffs",
    )
    return ap


def _process_path(path: Path, tally: _Tally) -> None:
    """Parse one archive, record either a match or a per-field disagreement."""
    cb = _comicbox_metadata(path)
    if cb is None:
        tally.skipped += 1
        return
    truth = _ground_truth(cb)
    if not truth.get("series"):
        tally.untagged += 1
        return
    parsed = _parser_output(path.name)
    diff = _diff(truth, parsed)
    if not diff:
        tally.matched += 1
        return
    tally.diffs.append(
        {"file": path.name, "truth": truth, "parsed": parsed, "diff": diff}
    )
    for key, (t, p) in diff.items():
        tally.field_disagreements[key] += 1
        tally.field_examples.setdefault(key, []).append((path.name, t, p))


def _print_report(tally: _Tally, total: int, out_path: Path) -> None:
    print()
    print(f"Total scanned : {total}")
    print(f"  comicbox skipped: {tally.skipped}")
    print(f"  untagged        : {tally.untagged}")
    print(f"  parser matched  : {tally.matched}")
    print(f"  disagreements   : {len(tally.diffs)}")
    print()
    print("Disagreements by field:")
    for key, n in tally.field_disagreements.most_common():
        print(f"  {key:10s} {n:5d}")
        for fn, t, p in tally.field_examples[key][:5]:
            print(f"    {fn}")
            print(f"        truth : {t!r}")
            print(f"        parsed: {p!r}")
    print()
    print(f"Full diff written to {out_path}")


def main() -> int:
    args = _build_argparser().parse_args()
    paths = _walk(args.dirs)
    if args.limit:
        paths = paths[: args.limit]
    print(f"Scanning {len(paths)} files...")

    tally = _Tally()
    for i, path in enumerate(paths):
        if i and i % 200 == 0:
            print(f"  {i}/{len(paths)}...")
        _process_path(path, tally)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(tally.diffs, indent=2, ensure_ascii=False))
    _print_report(tally, len(paths), args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
