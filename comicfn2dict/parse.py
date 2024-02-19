"""Parse comic book archive names using the simple 'parse' parser."""
from pprint import pprint
from pathlib import Path
from re import Match, Pattern
from typing import Any

from comicfn2dict.regex import (
    EXTRA_SPACES_RE,
    ISSUE_ANYWHERE_RE,
    ISSUE_BEGIN_RE,
    ISSUE_COUNT_RE,
    ISSUE_END_RE,
    ISSUE_NUMBER_RE,
    ISSUE_TOKEN_RE,
    NON_SPACE_DIVIDER_RE,
    ORIGINAL_FORMAT_RE,
    ORIGINAL_FORMAT_SCAN_INFO_RE,
    REMAINING_GROUP_RE,
    SCAN_INFO_RE,
    VOLUME_RE,
    YEAR_BEGIN_RE,
    YEAR_END_RE,
    YEAR_TOKEN_RE,
)

_REMAINING_GROUP_KEYS = ("series", "title")


def _parse_ext(name: str | Path, metadata: dict) -> str:
    """Pop the extension from the pathname."""
    if isinstance(name, str):
        name = name.strip()
    path = Path(name)
    suffix = path.suffix
    data = path.name.removesuffix(suffix)
    ext = suffix.lstrip(".")
    if ext:
        metadata["ext"] = ext
    return data


def _clean_dividers(data: str) -> str:
    """Replace non space dividers and clean extra spaces out of string."""
    data = NON_SPACE_DIVIDER_RE.sub(" ", data)
    return EXTRA_SPACES_RE.sub(" ", data)


def _get_data_list(path: str | Path, metadata: dict) -> list[str]:
    """Prepare data list from a path or string."""
    data = _parse_ext(path, metadata)
    data = _clean_dividers(data)
    return [data]


def _grouping_operators_strip(value: str) -> str:
    """Strip spaces and parens."""
    value = value.strip()
    value = value.strip("()").strip()
    value = value.strip("-").strip()
    value = value.strip("'").strip('"').strip()
    return value


def _splicey_dicey(
    data_list: list[str], index: int, match: Match, match_group: int | str = 0
) -> str:
    """Replace a string token from a list with two strings and the value removed.

    And return the value.
    """
    value = match.group(match_group)
    data = data_list.pop(index)
    data_ends = []
    if data_before := data[: match.start()].strip():
        data_ends.append(data_before)
    if data_after := data[match.end() :].strip():
        data_ends.append(data_after)
    data_list[index:index] = data_ends
    return _grouping_operators_strip(value)


def _match_original_format_and_scan_info(
    match: Match, metadata: dict[str, Any], data_list: list[str], index: int
) -> None:
    """Match (ORIGINAL_FORMAT-SCAN_INFO)."""
    original_format = match.group("original_format")
    try:
        scan_info = match.group("scan_info")
    except IndexError:
        scan_info = None
    metadata["original_format"] = _grouping_operators_strip(original_format)
    match_group = 1
    if scan_info:
        metadata["scan_info"] = _grouping_operators_strip(scan_info)
        match_group = 0
    _splicey_dicey(data_list, index, match, match_group=match_group)


def _parse_original_format_and_scan_info(data_list: list[str], metadata: dict) -> int:
    """Parse (ORIGINAL_FORMAT-SCAN_INFO)."""
    index = 0
    match = None
    for data in data_list:
        match = ORIGINAL_FORMAT_SCAN_INFO_RE.search(data)
        if match:
            _match_original_format_and_scan_info(match, metadata, data_list, index)
            break
        index += 1
    else:
        index = 0
    return index


def _pop_value_from_token(
    data_list: list,
    metadata: dict,
    regex: Pattern,
    key: str,
    index: int = 0,
) -> str:
    """Search token for value, splice and assign to metadata."""
    data = data_list[index]
    match = regex.search(data)
    if match:
        value = _splicey_dicey(data_list, index, match, key)
        metadata[key] = value
    else:
        value = ""
    return value


def _parse_item(
    data_list: list[str],
    metadata: dict,
    regex: Pattern,
    key: str,
    start_index: int = 0,
    path: str = "",
) -> int:
    """Parse a value from the data list into metadata and alter the data list."""
    path_index = -1
    index = start_index
    dl_len = end_index = len(data_list)
    if index >= end_index:
        index = 0
    while index < end_index:
        value = _pop_value_from_token(data_list, metadata, regex, key, index)
        if value:
            if "key" == "issue":
                path_index = path.find(value)
            break
        index += 1
        if index > dl_len and start_index > 0:
            index = 0
            end_index = start_index
    return path_index


def _pop_issue_from_text_fields(
    data_list: list[str], metadata: dict, index: int
) -> str:
    """Search issue from ends of text fields."""
    if "issue" not in metadata:
        _pop_value_from_token(data_list, metadata, ISSUE_END_RE, "issue", index=index)
    if "issue" not in metadata:
        _pop_value_from_token(data_list, metadata, ISSUE_BEGIN_RE, "issue", index=index)
    return data_list.pop(index)


TITLE_PRECEDING_KEYS = ("issue", "year", "volume")


def _is_title_in_position(path, value, metadata):
    """Does the title come after series and one other token if they exist."""
    # TODO this could be faster if indexes could be grabbed for these tokens
    #      when they are extracted.
    title_index = path.find(value)

    # Does a series come first.
    series = metadata.get("series")
    if not series:
        return False
    series_index = path.find(series)
    if title_index < series_index:
        return False

    # If other tokens exist then they much precede the title.
    title_ok = False
    other_tokens_exist = False
    for preceding_key in TITLE_PRECEDING_KEYS:
        preceding_value = metadata.get(preceding_key)
        if not preceding_value:
            continue
        other_tokens_exist = True
        preceding_index = path.find(preceding_value)
        if title_index > preceding_index:
            title_ok = True
            break
    return title_ok or not other_tokens_exist


def _assign_remaining_groups(data_list: list[str], metadata: dict, path: str):
    """Assign series and title."""
    index = 0
    for key in _REMAINING_GROUP_KEYS:
        try:
            data = data_list[index]
        except (IndexError, TypeError):
            break
        match = REMAINING_GROUP_RE.search(data) if data else None
        if match:
            value = _pop_issue_from_text_fields(data_list, metadata, index)
            if key == "title" and not _is_title_in_position(path, value, metadata):
                continue
            value = _grouping_operators_strip(value)
            if value:
                metadata[key] = value
        else:
            index += 1


def _pickup_issue(remainders: list[str], metadata: dict) -> None:
    """Get issue from remaining tokens or anywhere in a pinch."""
    if "issue" in metadata:
        return
    _parse_item(remainders, metadata, ISSUE_TOKEN_RE, "issue")
    if "issue" in metadata:
        return
    _parse_item(remainders, metadata, ISSUE_ANYWHERE_RE, "issue")


def _log_progress(label, metadata, data_list):
    print(label + ":")
    pprint(metadata)
    pprint(data_list)


def comicfn2dict(path: str | Path) -> dict[str, Any]:
    """Parse the filename with a hierarchy of regexes."""
    metadata = {}
    data_list = _get_data_list(path, metadata)
    _log_progress("INITIAL", metadata, data_list)

    # Parse paren tokens
    _parse_item(data_list, metadata, ISSUE_COUNT_RE, "issue_count")
    _parse_item(data_list, metadata, YEAR_TOKEN_RE, "year")
    of_index = _parse_original_format_and_scan_info(data_list, metadata)
    if "original_format" not in metadata:
        of_index = _parse_item(
            data_list, metadata, ORIGINAL_FORMAT_RE, "original_format"
        )
    if "scan_info" not in metadata:
        # Start searching for scan_info after original format.
        _parse_item(
            data_list,
            metadata,
            SCAN_INFO_RE,
            "scan_info",
            start_index=of_index + 1,
        )
    _log_progress("AFTER PAREN TOKENS", metadata, data_list)

    # Parse regular tokens
    _parse_item(data_list, metadata, VOLUME_RE, "volume")
    _parse_item(data_list, metadata, ISSUE_NUMBER_RE, "issue", path=str(path))
    _log_progress("AFTER REGULAR TOKENS", metadata, data_list)

    # Pickup year if not gotten.
    if "year" not in metadata:
        _parse_item(data_list, metadata, YEAR_BEGIN_RE, "year")
    if "year" not in metadata:
        _parse_item(data_list, metadata, YEAR_END_RE, "year")
    _log_progress("AFTER YEAR PICKUP", metadata, data_list)

    # Pickup issue if it's a standalone token
    if "issue" not in metadata:
        _parse_item(data_list, metadata, ISSUE_TOKEN_RE, "issue")

    _log_progress("AFTER ISSUE PICKUP", metadata, data_list)

    # Series and Title. Also looks for issue.
    _assign_remaining_groups(data_list, metadata, str(path))
    _log_progress("AFTER SERIES AND TITLE", metadata, data_list)

    # Final try for issue number.
    _pickup_issue(data_list, metadata)
    _log_progress("AFTER ISSUE PICKUP", metadata, data_list)

    # Add Remainders
    if data_list:
        metadata["remainders"] = tuple(data_list)

    return metadata
