"""Tests for filename parsing."""

import pytest

from comicfn2dict import ComicFilenameSerializer, comicfn2dict
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


@pytest.mark.parametrize(
    ("issue", "token"),
    [
        ("1", "#001"),
        ("1.5", "#001.5"),
        ("27AU", "#027AU"),
        ("½", "#000½"),
        ("1½", "#001½"),
        ("1024", "#1024"),
        ("0", "#000"),
        ("0.0.1", "#000.0.1"),
        ("-1", "#-001"),
        ("Omega", "#Omega"),
        pytest.param(1, "#001", id="int-1"),
    ],
)
def test_serialize_issue(issue, token):
    """Issues are padded after any sign, letter issues aren't, and both read back."""
    fn = ComicFilenameSerializer({"series": "Series Name", "issue": issue}).serialize()
    assert fn == f"Series Name {token}.cbz"
    assert comicfn2dict(fn)["issue"] == token.removeprefix("#")


@pytest.mark.parametrize(
    ("md", "date"),
    [
        ({"year": "2000", "month": "13", "day": "31"}, " (2000)"),
        ({"year": "2000", "month": "", "day": "31"}, " (2000)"),
        ({"year": "2000", "day": "3"}, " (2000)"),
        ({"day": "31"}, ""),
        ({"year": "2000", "date": ""}, " (2000)"),
        ({"year": "2000", "date": None}, " (2000)"),
        ({"year": "2000", "date": "Spring 2000"}, " (Spring 2000)"),
    ],
)
def test_serialize_date_edges(md, date):
    """A date is built from year, month and day unless a date is set."""
    fn = ComicFilenameSerializer({"series": "Series Name", **md}).serialize()
    assert fn == f"Series Name{date}.cbz"


@pytest.mark.parametrize("ext", ["", None])
def test_serialize_empty_ext(ext):
    """An empty ext writes the default extension."""
    fn = ComicFilenameSerializer({"series": "Series Name", "ext": ext}).serialize()
    assert fn == "Series Name.cbz"


@pytest.mark.parametrize(
    ("md", "fn"),
    [
        ({"volume_count": "3"}, "Series Name.cbz"),
        ({"volume": "", "volume_count": "3"}, "Series Name.cbz"),
        ({"issue_count": "12"}, "Series Name.cbz"),
        (
            {"volume_count": "3", "issue": "1", "issue_count": "12"},
            "Series Name #001 (of 012).cbz",
        ),
    ],
)
def test_serialize_count_without_number(md, fn):
    """A count is written only after the number it counts, so the name reads back."""
    md = {"series": "Series Name", **md}
    assert ComicFilenameSerializer(md).serialize() == fn
    assert "remainders" not in comicfn2dict(fn)
