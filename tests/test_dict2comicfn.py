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
