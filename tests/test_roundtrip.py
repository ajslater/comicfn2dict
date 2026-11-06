"""Tests that what dict2comicfn() writes, comicfn2dict() reads back."""

import pytest

from comicfn2dict import comicfn2dict, dict2comicfn
from tests.comic_filenames import PARSE_FNS, ROUND_TRIP_FNS, ROUND_TRIP_MDS

_ROUND_TRIP_MDS = (
    *ROUND_TRIP_MDS,
    pytest.param(
        {
            "series": "Series Name",
            "issue": "001",
            "remainders": ("Extra", "(4 covers)"),
            "ext": "cbz",
        },
        marks=pytest.mark.xfail(
            strict=True, reason="several remainders read back as one string"
        ),
    ),
)


@pytest.mark.parametrize("fn", ROUND_TRIP_FNS)
def test_filename_round_trip(fn):
    """A name dict2comicfn() writes reads to a dict that writes it again."""
    assert dict2comicfn(comicfn2dict(fn)) == fn


@pytest.mark.parametrize("md", _ROUND_TRIP_MDS)
def test_dict_round_trip(md):
    """A dict in comicfn2dict() form is written to a name that reads back to it."""
    assert comicfn2dict(dict2comicfn(md)) == md


@pytest.mark.parametrize("fn", PARSE_FNS.keys())
def test_written_name_has_no_path_separator(fn):
    """No parsed value carries the parser's "/" token delimiter into a name."""
    assert "/" not in dict2comicfn(comicfn2dict(fn))
