#!/bin/bash
# Run comicfn2dict cli
set -euo pipefail
uv run ./comicfn2dict.py "$@"
