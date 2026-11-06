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


@pytest.mark.parametrize(("month", "date"), [("Dec", "Dec"), ("13", "13"), (12, "Dec")])
def test_serialize_month_without_year(month, date):
    """Months the schema doesn't allow are written, not crashed on."""
    md = {"series": "Series Name", "month": month, "day": "31"}
    fn = ComicFilenameSerializer(md).serialize()
    assert fn == f"Series Name ({date}-31).cbz"


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
