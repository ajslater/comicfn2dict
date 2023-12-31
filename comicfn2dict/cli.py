#!/usr/bin/env python3
"""Simple cli for comicfn2dict."""
from argparse import ArgumentParser
from pathlib import Path
from pprint import pprint

from comicfn2dict.parse import comicfn2dict


def main():
    """Test parser."""
    description = "Comic book archive read/write tool."
    parser = ArgumentParser(description=description)
    parser.add_argument("path", help="Path of comic filename to parse", type=Path)
    args = parser.parse_args()
    name = args.path.name
    metadata = comicfn2dict(name)
    pprint(metadata)  # noqa:T203


if __name__ == "__main__":
    main()
