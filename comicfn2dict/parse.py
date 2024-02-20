"""Parse comic book archive names using the simple 'parse' parser."""
from pprint import pprint
from copy import copy
from pathlib import Path
from re import Pattern
from typing import Any

from comicfn2dict.regex import (
    EXTRA_SPACES_RE,
    ISSUE_ANYWHERE_RE,
    ISSUE_COUNT_RE,
    ISSUE_NUMBER_RE,
    ISSUE_BEGIN_RE,
    ISSUE_END_RE,
    NON_SPACE_DIVIDER_RE,
    ORIGINAL_FORMAT_SCAN_INFO_SEPARATE_RE,
    ORIGINAL_FORMAT_SCAN_INFO_RE,
    REMAINING_GROUP_RE,
    VOLUME_RE,
    YEAR_BEGIN_RE,
    YEAR_END_RE,
    YEAR_TOKEN_RE,
)

_REMAINING_GROUP_KEYS = ("series", "title")
_TITLE_PRECEDING_KEYS = ("issue", "year", "volume")
_TOKEN_DELIMETER = "/"


class ComicFilenameParser:
    @staticmethod
    def _clean_dividers(data: str) -> str:
        """Replace non space dividers and clean extra spaces out of string."""
        data = NON_SPACE_DIVIDER_RE.sub(" ", data)
        return EXTRA_SPACES_RE.sub(" ", data).strip()

    def _parse_ext(self):
        """Pop the extension from the pathname."""
        path = Path(self._unparsed_path)
        suffix = path.suffix
        if not suffix:
            return
        self.path_indexes["ext"] = self.path.rfind(suffix)

        data = path.name.removesuffix(suffix)
        ext = suffix.lstrip(".")
        self.metadata["ext"] = ext
        self._unparsed_path = data

    def _grouping_operators_strip(self, value: str) -> str:
        """Strip spaces and parens."""
        value = value.strip()
        value = value.strip("()").strip()
        value = value.strip("-").strip()
        value = value.strip("'").strip('"').strip()
        return value

    def _parse_item(
        self,
        regex: Pattern,
        require_all: bool = False,
    ) -> None:
        """Parse a value from the data list into metadata and alter the data list."""
        matches = regex.search(self._unparsed_path)
        if not matches:
            return
        matched_metadata = {}
        matched_path_indexes = {}
        for key, value in matches.groupdict().items():
            if not value:
                if require_all:
                    return
                continue
            matched_path_indexes[key] = self.path.find(value)
            # TODO idk if strip is necceesary here
            matched_metadata[key] = self._grouping_operators_strip(value)
        self.metadata.update(matched_metadata)
        self.path_indexes.update(matched_path_indexes)

        marked_str = regex.sub(_TOKEN_DELIMETER, self._unparsed_path)
        parts = []
        for part in marked_str.split(_TOKEN_DELIMETER):
            if token := part.strip():
                parts.append(token)
        self._unparsed_path = _TOKEN_DELIMETER.join(parts)

    def _is_title_in_position(self, value):
        """Does the title come after series and one other token if they exist."""
        title_index = self.path.find(value)

        # Does a series come first.
        if title_index < self.path_indexes.get("series", -1):
            return False

        # If other tokens exist then they much precede the title.
        title_ok = False
        other_tokens_exist = False
        for preceding_key in _TITLE_PRECEDING_KEYS:
            other_tokens_exist = True
            if title_index > self.path_indexes.get(preceding_key, -1):
                title_ok = True
                break
        return title_ok or not other_tokens_exist

    def _assign_remaining_groups(self):
        """Assign series and title."""
        if not self._unparsed_path:
            return

        # TODO fix REMAINING GROUP_RE to use token delim
        tokens = self._unparsed_path.split(_TOKEN_DELIMETER)

        # ASSIGN GROUPS
        remaining_key_index = 0
        unused_tokens = []
        while tokens and remaining_key_index < len(_REMAINING_GROUP_KEYS):
            key = _REMAINING_GROUP_KEYS[remaining_key_index]
            token = tokens.pop(0)
            match = REMAINING_GROUP_RE.search(token)
            if match:
                value = match.group()
                if key == "title" and not self._is_title_in_position(value):
                    unused_tokens.append(token)
                    continue
                value = self._grouping_operators_strip(value)
                self.metadata[key] = value
                self.path_indexes[key] = self.path.find(value)
                remaining_key_index += 1
            else:
                unused_tokens.append(token)

        self._unparsed_path = " ".join(unused_tokens) if unused_tokens else ""

    def _add_remainders(self):
        """Add Remainders."""
        remainders = []
        for token in self._unparsed_path.split(_TOKEN_DELIMETER):
            if remainder := token.strip():
                remainders.append(remainder)

        if remainders:
            self.metadata["remainders"] = tuple(remainders)

    def _log_progress(self, label):
        if not self._debug:
            return
        print(label + ":")
        combined = {}
        for key in self.metadata:
            combined[key] = (self.metadata.get(key), self.path_indexes.get(key))
        pprint(combined)
        print(self._unparsed_path)

    def parse(self) -> dict[str, Any]:
        """Parse the filename with a hierarchy of regexes."""
        self._unparsed_path = self._clean_dividers(self._unparsed_path)
        self._log_progress("INITIAL")
        self._parse_ext()

        # Parse paren tokens
        self._parse_item(ISSUE_COUNT_RE)
        self._parse_item(YEAR_TOKEN_RE)
        self._parse_item(
            ORIGINAL_FORMAT_SCAN_INFO_RE,
            require_all=True,
        )
        if "original_format" not in self.metadata:
            self._parse_item(
                ORIGINAL_FORMAT_SCAN_INFO_SEPARATE_RE,
            )
        self._log_progress("AFTER PAREN TOKENS")

        # Parse regular tokens
        self._parse_item(VOLUME_RE)
        self._parse_item(ISSUE_NUMBER_RE)
        self._log_progress("AFTER REGULAR TOKENS")

        # Pickup year if not gotten.
        if "year" not in self.metadata:
            self._parse_item(YEAR_BEGIN_RE)
        if "year" not in self.metadata:
            self._parse_item(YEAR_END_RE)
        self._log_progress("AFTER YEAR PICKUP")

        # Pickup issue if it's a standalone token
        if "issue" not in self.metadata:
            self._parse_item(ISSUE_END_RE)
        if "issue" not in self.metadata:
            self._parse_item(ISSUE_BEGIN_RE)

        self._log_progress("AFTER ISSUE PICKUP")

        # Series and Title. Also looks for issue.
        self._assign_remaining_groups()
        self._log_progress("AFTER SERIES AND TITLE")

        # Final try for issue number.
        if "issue" not in self.metadata:
            # TODO is this useful?
            self._parse_item(ISSUE_ANYWHERE_RE)
        self._log_progress("AFTER ISSUE PICKUP")

        self._add_remainders()

        return self.metadata

    def __init__(self, path: str | Path, verbose: int = 0):
        """Initialize."""
        self._debug: bool = verbose > 0
        self.metadata: dict[str, str | tuple[str, ...]] = {}
        self.path_indexes: dict[str, int] = {}
        # munge path
        if isinstance(path, str):
            path = path.strip()
        p_path = Path(path)
        self.path = str(p_path.name).strip()
        self._unparsed_path = copy(self.path)
