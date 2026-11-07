"""Test the metadata dicts against the packaged JSON Schema."""

import json
from importlib.resources import files

import pytest
from jsonschema import Draft202012Validator, validators

from comicfn2dict import comicfn2dict
from tests.comic_filenames import PARSE_FNS, ROUND_TRIP_MDS, SERIALIZE_FNS

_SCHEMA = json.loads(
    (files("comicfn2dict") / "schemas" / "comicfn2dict.schema.json").read_text()
)
# comicfn2dict returns remainders as a tuple, which is a JSON array.
_TYPE_CHECKER = Draft202012Validator.TYPE_CHECKER.redefine(
    "array", lambda _checker, instance: isinstance(instance, list | tuple)
)
_VALIDATOR = validators.extend(Draft202012Validator, type_checker=_TYPE_CHECKER)(
    _SCHEMA
)
_FILENAMES = sorted(PARSE_FNS.keys() | SERIALIZE_FNS.keys())


def test_schema_is_valid():
    """The schema is a valid draft 2020-12 JSON Schema and its examples match it."""
    Draft202012Validator.check_schema(_SCHEMA)
    for example in _SCHEMA["examples"]:
        _VALIDATOR.validate(example)


@pytest.mark.parametrize("fn", _FILENAMES)
def test_parsed_dict_matches_schema(fn):
    """comicfn2dict() returns only keys and values the schema allows."""
    _VALIDATOR.validate(comicfn2dict(fn))


@pytest.mark.parametrize("md", SERIALIZE_FNS.values())
def test_serialized_dict_matches_schema(md):
    """The dicts the dict2comicfn() tests write from match the schema."""
    _VALIDATOR.validate(md)


@pytest.mark.parametrize("md", ROUND_TRIP_MDS)
def test_round_trip_dict_matches_schema(md):
    """The dicts the round-trip tests write from match the schema."""
    _VALIDATOR.validate(md)
