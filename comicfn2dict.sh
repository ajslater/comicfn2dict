#!/bin/bash
# Run comicfn2dict cli
set -euo pipefail
poetry run ./comicfn2dict.py "$@"
