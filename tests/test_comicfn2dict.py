"""Tests for filename parsing."""
from pprint import pprint
from types import MappingProxyType

import pytest
from deepdiff.diff import DeepDiff

from comicfn2dict import ComicFilenameParser
from tests.comic_filenames import FNS

ALL_FIELDS = frozenset({"series", "volume", "issue", "issue_count", "year", "ext"})
FIELD_SCHEMA = MappingProxyType({key: None for key in ALL_FIELDS})


@pytest.mark.parametrize("item", FNS.items())
def test_parse_filename(item):
    """Test filename parsing."""
    fn, defined_fields = item
    md = ComicFilenameParser(fn, verbose=1).parse()
    diff = DeepDiff(defined_fields, md, ignore_order=True)
    print(fn)
    pprint(defined_fields)
    pprint(md)
    pprint(diff)
    assert not diff
