"""Tests for filename parsing."""

import pytest

from comicfn2dict import ComicFilenameSerializer
from tests.comic_filenames import SERIALIZE_FNS


@pytest.mark.parametrize("item", SERIALIZE_FNS.items())
def test_serialize_dict(item):
    """Test metadata serialization."""
    test_fn, md = item
    fn = ComicFilenameSerializer(md).serialize()
    assert test_fn == fn


@pytest.mark.parametrize(
    ("month", "date"),
    [
        ("Dec", ""),
        ("13", ""),
        (12, " (Dec-31)"),
        ("0", ""),
        ("00", ""),
        ("-1", ""),
        ("1", " (Jan-31)"),
        ("01", " (Jan-31)"),
    ],
)
def test_serialize_month_without_year(month, date):
    """With no year, a month from 1 to 12 is named; any other is left out."""
    md = {"series": "Series Name", "month": month, "day": "31"}
    fn = ComicFilenameSerializer(md).serialize()
    assert fn == f"Series Name{date}.cbz"


def test_serialize_int_counts():
    """Int counts are padded on the left, like str counts."""
    md = {
        "series": "Series Name",
        "volume": "1",
        "volume_count": 6,
        "issue": "1",
        "issue_count": 12,
    }
    fn = ComicFilenameSerializer(md).serialize()
    assert fn == "Series Name v1 (of 006) #001 (of 012).cbz"
