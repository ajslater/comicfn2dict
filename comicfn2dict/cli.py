#!/usr/bin/env python3
"""Simple cli for comicfn2dict."""

from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint

from comicfn2dict.parse import ComicFilenameParser


def main() -> None:
    """Test parser."""
    description = "Comic book archive read/write tool."
    parser = ArgumentParser(description=description)
    parser.add_argument("path", help="Path of comic filename to parse", type=Path)
    parser.add_argument(
        "-v",
        "--verbose",
        default=0,
        action="count",
        help="Display intermediate parsing steps. Good for debugging.",
    )
    args = parser.parse_args()
    name = args.path.name
    cfnparser = ComicFilenameParser(name, verbose=args.verbose)
    metadata = cfnparser.parse()
    if args.verbose:
        print("=" * 80)  # noqa:T201
    pprint(metadata)  # noqa:T203


if __name__ == "__main__":
    main()
