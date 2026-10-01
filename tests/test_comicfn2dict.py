"""Tests for filename parsing."""

from pprint import pprint
from time import perf_counter

import pytest
from deepdiff.diff import DeepDiff

from comicfn2dict import ComicFilenameParser
from tests.comic_filenames import PARSE_FNS


@pytest.mark.parametrize("item", PARSE_FNS.items())
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


def test_parse_long_digit_run_is_fast():
    """Long digit runs must not backtrack catastrophically in the issue regexes."""
    digits = "1" * 120
    start = perf_counter()
    md = ComicFilenameParser(f"Batman {digits}.cbz").parse()
    elapsed = perf_counter() - start
    assert md == {"ext": "cbz", "issue": digits, "series": "Batman"}
    assert elapsed < 1
