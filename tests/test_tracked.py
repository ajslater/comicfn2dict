"""Tests for the text that tracks where its characters came from."""

import re
from itertools import pairwise

import pytest

from comicfn2dict import ComicFilenameParser
from comicfn2dict.regex import ISSUE_NUMBER_RE, REGEX_SUBS, YEAR_END_RE
from comicfn2dict.tracked import TrackedText
from tests.comic_filenames import PARSE_FNS

_NAME = "Starling_#001__Long Night__  (2020-2024) [Digital].cbz"
_DEFAULT_INDEX = 99


def _assert_tracked(tracked: TrackedText) -> None:
    """Every character has an origin and origins never go backwards."""
    assert len(tracked.text) == len(tracked.origins)
    assert all(first <= second for first, second in pairwise(tracked.origins))


def test_from_source():
    """A new text's origins are its own indexes."""
    tracked = TrackedText.from_source("abc")
    assert tracked == TrackedText("abc", (0, 1, 2))


@pytest.mark.parametrize("fn", PARSE_FNS.keys())
def test_sub_matches_regex_sub(fn):
    """sub() gives the text regex.sub() gives, for each cleanup regex in turn."""
    tracked = TrackedText.from_source(fn)
    for regex, (replacement, count) in REGEX_SUBS.items():
        expected = regex.sub(replacement, tracked.text, count=count)
        tracked = tracked.sub(regex, replacement, count=count)
        assert tracked.text == expected
        _assert_tracked(tracked)


@pytest.mark.parametrize(
    ("regex", "replacement", "count"),
    [
        # A pattern that can match the empty string at the end.
        (YEAR_END_RE, "/", 0),
        (re.compile(r"x*"), "-", 0),
        (re.compile(r"\s"), "", 0),
        (re.compile(r"\s"), "", 2),
        (ISSUE_NUMBER_RE, "/", 1),
        (re.compile(r"__(.*)__"), r"(\1)", 0),
    ],
)
def test_sub_edge_cases(regex, replacement, count):
    """sub() agrees with regex.sub() on empty matches, groups and counts."""
    tracked = TrackedText.from_source(_NAME).sub(regex, replacement, count=count)
    assert tracked.text == regex.sub(replacement, _NAME, count=count)
    _assert_tracked(tracked)


def test_sub_replacement_takes_origin_of_match():
    """Inserted characters take the origin of the text they replace."""
    tracked = TrackedText.from_source("ab__cd__ef").sub(
        re.compile(r"__(.*)__"), r"(\1)"
    )
    assert tracked.text == "ab(cd)ef"
    assert tracked.origins == (0, 1, 2, 2, 2, 2, 8, 9)


def test_strip_split_join():
    """strip(), split() and join() keep each character's origin."""
    tracked = TrackedText.from_source("  ab / cd  ")
    assert tracked.strip() == TrackedText("ab / cd", tuple(range(2, 9)))
    parts = [part.strip() for part in tracked.split("/")]
    assert parts == [TrackedText("ab", (2, 3)), TrackedText("cd", (7, 8))]
    joined = TrackedText.join("/", parts)
    assert joined == TrackedText("ab/cd", (2, 3, 7, 7, 8))
    assert TrackedText.from_source("   ").strip() == TrackedText("", ())


def test_origin_past_the_end():
    """The origin just past the end follows the last character's."""
    tracked = TrackedText.from_source("abc")[:2]
    assert tracked.origin(len(tracked.text)) == len(tracked.text)
    assert TrackedText("", ()).origin(0) == 0


@pytest.mark.parametrize(
    ("fn", "expected"),
    [
        (
            "Empire #001 Long Night (2020) (Digital) (Empire).cbz",
            {
                "series": 0,
                "issue": 8,
                "title": 12,
                "year": 24,
                "original_format": 31,
                "scan_info": 41,
                "ext": 49,
            },
        ),
        # The title has underscores, the month is converted, and the scan
        # info is a bare "c2c".
        (
            "Starling_#1_Long_Night_(Dec_2020)_(c2c).cbz",
            {
                "series": 0,
                "issue": 10,
                "title": 12,
                "month": 24,
                "year": 28,
                "scan_info": 35,
                "ext": 40,
            },
        ),
        # The first of two years becomes the volume.
        (
            "Starling_#1_Long_Night_(2018)_(2020)_(c2c).cbz",
            {
                "series": 0,
                "issue": 10,
                "title": 12,
                "volume": 24,
                "year": 31,
                "scan_info": 38,
                "ext": 43,
            },
        ),
    ],
)
def test_path_index(fn, expected):
    """Each field's index is where its text starts in the name."""
    parser = ComicFilenameParser(fn)
    metadata = parser.parse()
    assert {key: parser.path_index(key) for key in metadata} == expected
    assert parser.path_index("remainders") == -1
    assert parser.path_index("publisher", _DEFAULT_INDEX) == _DEFAULT_INDEX
