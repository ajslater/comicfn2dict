#!/usr/bin/env bash
# Render the packaged JSON Schema as the docs page docs/schema/comicfn2dict.schema.md
set -euo pipefail
cd "$(dirname "$0")/.."
SCHEMA=comicfn2dict/schemas/comicfn2dict.schema.json
MD=docs/schema/comicfn2dict.schema.md

mkdir -p "$(dirname "$MD")"
uvx jsonschema2md@1.7.0 --locale en_US "$SCHEMA" "$MD"
# The H1 is the page's docs nav title. The schema's title names the format,
# which is also this site's name, so title the page for what it holds.
perl -pi -e 's/^# comicfn2dict$/# Metadata Schema/ if $. == 1' "$MD"
npx prettier --write "$MD"
