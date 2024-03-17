"""Parse comic book archive names using the simple 'parse' parser."""

from __future__ import annotations

from calendar import month_abbr
from copy import copy
from pathlib import Path
from pprint import pformat
from sys import maxsize
from typing import TYPE_CHECKING

from comicfn2dict.log import print_log_header
from comicfn2dict.regex import (
    ALPHA_MONTH_RANGE_RE,
    BOOK_VOLUME_RE,
    ISSUE_BEGIN_RE,
    ISSUE_END_RE,
    ISSUE_NUMBER_RE,
    ISSUE_WITH_COUNT_RE,
    MONTH_FIRST_DATE_RE,
    NON_NUMBER_DOT_RE,
    ORIGINAL_FORMAT_NAKED_RE,
    ORIGINAL_FORMAT_SCAN_INFO_RE,
    ORIGINAL_FORMAT_SCAN_INFO_SEPARATE_RE,
    PUBLISHER_AMBIGUOUS_RE,
    PUBLISHER_AMBIGUOUS_TOKEN_RE,
    PUBLISHER_UNAMBIGUOUS_RE,
    PUBLISHER_UNAMBIGUOUS_TOKEN_RE,
    REGEX_SUBS,
    REMAINDER_PAREN_GROUPS_RE,
    REMAINING_GROUP_RE,
    SCAN_INFO_SECONDARY_RE,
    TOKEN_DELIMETER,
    VOLUME_RE,
    VOLUME_WITH_COUNT_RE,
    YEAR_END_RE,
    YEAR_FIRST_DATE_RE,
    YEAR_TOKEN_RE,
)

if TYPE_CHECKING:
    from re import Match, Pattern

_DATE_KEYS = frozenset({"year", "month", "day"})
_REMAINING_GROUP_KEYS = ("series", "title")
# Ordered by commonness.
_TITLE_PRECEDING_KEYS = ("issue", "year", "volume", "month")


class ComicFilenameParser:
    """Parse a filename metadata into a dict."""

    def path_index(self, key: str, default: int = -1) -> int:
        """Lazily retrieve and memoize the key's location in the path."""
        if key == "remainders":
            return default
        value: str = self.metadata.get(key, "")  # type: ignore
        if not value:
            return default
        if value not in self._path_indexes:
            # XXX This is fragile, but it's difficult to calculate the original
            #     position at match time from the ever changing _unparsed_path.
            index = self.path.rfind(value) if key == "ext" else self.path.find(value)
            self._path_indexes[value] = index
        return self._path_indexes[value]

    def _log(self, label: str) -> None:
        if not self._debug:
            return
        print_log_header(label)
        combined = {}
        for key in self.metadata:
            combined[key] = (self.metadata.get(key), self.path_index(key))
        print("  " + self._unparsed_path)  # noqa: T201
        print("  " + pformat(combined))  # noqa: T201

    def _parse_ext(self) -> None:
        """Pop the extension from the pathname."""
        path = Path(self._unparsed_path)
        suffix = path.suffix
        if not suffix:
            return

        data = path.name.removesuffix(suffix)
        ext = suffix.lstrip(".")
        self.metadata["ext"] = ext
        self._unparsed_path = data

    def _clean_dividers(self) -> None:
        """Replace non space dividers and clean extra spaces out of string."""
        data = self._unparsed_path

        # Simple substitutions
        for regex, pair in REGEX_SUBS.items():
            replacement, count = pair
            data = regex.sub(replacement, data, count=count).strip()
        self._unparsed_path = data.strip()
        self._log("After Clean Path")

    def _parse_items_update_metadata(
        self, matches: Match, exclude: str, require_all: bool, first_only: bool
    ) -> bool:
        """Update Metadata."""
        matched_metadata = {}
        for key, value in matches.groupdict().items():
            if value == exclude:
                continue
            if not value:
                if require_all:
                    return False
                continue
            matched_metadata[key] = value
            if first_only:
                break
        if not matched_metadata:
            return False
        self.metadata.update(matched_metadata)
        return True

    def _parse_items_pop_tokens(self, regex: Pattern, first_only: bool) -> None:
        """Pop tokens from unparsed path."""
        count = 1 if first_only else 0
        marked_str = regex.sub(TOKEN_DELIMETER, self._unparsed_path, count=count)
        parts = []
        for part in marked_str.split(TOKEN_DELIMETER):
            if token := part.strip():
                parts.append(token)
        self._unparsed_path = TOKEN_DELIMETER.join(parts)

    def _parse_items(  # noqa: PLR0913
        self,
        regex: Pattern,
        require_all: bool = False,
        exclude: str = "",
        first_only: bool = False,
        pop: bool = True,
    ) -> None:
        """Parse a value from the data list into metadata and alter the data list."""
        # Match
        matches = regex.search(self._unparsed_path)
        if not matches:
            return

        if not self._parse_items_update_metadata(
            matches, exclude, require_all, first_only
        ):
            return

        if pop:
            self._parse_items_pop_tokens(regex, first_only)

    def _parse_issue(self) -> None:
        """Parse Issue."""
        self._parse_items(ISSUE_NUMBER_RE)
        if "issue" not in self.metadata:
            self._parse_items(ISSUE_WITH_COUNT_RE)
        self._log("After Issue")

    def _parse_volume(self) -> None:
        """Parse Volume."""
        self._parse_items(VOLUME_RE)
        if "volume" not in self.metadata:
            self._parse_items(VOLUME_WITH_COUNT_RE)
        self._log("After Volume")

    def _alpha_month_to_numeric(self) -> None:
        """Translate alpha_month to numeric month."""
        if alpha_month := self.metadata.pop("alpha_month", ""):
            alpha_month = alpha_month.capitalize()  # type: ignore
            for index, abbr in enumerate(month_abbr):
                if abbr and alpha_month.startswith(abbr):
                    month = f"{index:02d}"
                    self.metadata["month"] = month
                    break

    def _parse_dates(self) -> None:
        """Parse date schemes."""
        # Discard second month of alpha month ranges.
        self._unparsed_path = ALPHA_MONTH_RANGE_RE.sub(r"\1", self._unparsed_path)

        # Month first date
        self._parse_items(MONTH_FIRST_DATE_RE)
        self._alpha_month_to_numeric()

        # Year first date
        if _DATE_KEYS - self.metadata.keys():
            self._parse_items(YEAR_FIRST_DATE_RE)
            self._alpha_month_to_numeric()

        if "year" not in self.metadata:
            self._parse_items(YEAR_TOKEN_RE, first_only=True)
            if "volume" in self.metadata:
                return
            # A second year will be the real year.
            # Move the first year to volume
            if volume := self.metadata.get("year", ""):
                self._parse_items(YEAR_TOKEN_RE)
                if self.metadata.get("year", "") != volume:
                    self.metadata["volume"] = volume
        self._log("After Date")

    def _parse_format_and_scan_info(self) -> None:
        """Format & Scan Info."""
        self._parse_items(
            ORIGINAL_FORMAT_SCAN_INFO_RE,
            require_all=True,
        )
        if "original_format" not in self.metadata:
            self._parse_items(
                ORIGINAL_FORMAT_SCAN_INFO_SEPARATE_RE,
            )
        self._parse_items(SCAN_INFO_SECONDARY_RE)
        if (
            scan_info_secondary := self.metadata.pop("secondary_scan_info", "")
        ) and "scan_info" not in self.metadata:
            self.metadata["scan_info"] = scan_info_secondary  # type: ignore
        self._log("After original_format & scan_info")

    def _parse_remainder_paren_groups(self) -> None:
        """Remove extraneous paren groups."""
        self._parse_items(REMAINDER_PAREN_GROUPS_RE)
        remainders: str = self.metadata.get("remainders", "")  # type: ignore
        if remainders:
            self.metadata["remainders"] = (remainders,)
        self._log("After parsing remainder paren and bracket groups")

    def _parse_ends_of_remaining_tokens(self):
        # Volume left on the end of string tokens
        if "volume" not in self.metadata:
            self._parse_items(BOOK_VOLUME_RE)
            self._log("After original_format & scan_info")

        # Years left on the end of string tokens
        year_end_matched = False
        if "year" not in self.metadata:
            self._parse_items(YEAR_END_RE, pop=False)
            year_end_matched = "year" in self.metadata
            self._log("After Year on end of token")

        # Issue left on the end of string tokens
        if "issue" not in self.metadata and not year_end_matched:
            exclude: str = self.metadata.get("year", "")  # type: ignore
            self._parse_items(ISSUE_END_RE, exclude=exclude)
        if "issue" not in self.metadata:
            self._parse_items(ISSUE_BEGIN_RE)
        self._log("After Issue on ends of tokens")

    def _parse_publisher(self) -> None:
        """Parse Publisher."""
        # Pop single tokens so they don't end up titles.
        self._parse_items(PUBLISHER_UNAMBIGUOUS_TOKEN_RE, first_only=True)
        if "publisher" not in self.metadata:
            self._parse_items(PUBLISHER_AMBIGUOUS_TOKEN_RE, first_only=True)
        if "publisher" not in self.metadata:
            self._parse_items(PUBLISHER_UNAMBIGUOUS_RE, pop=False, first_only=True)
        if "publisher" not in self.metadata:
            self._parse_items(PUBLISHER_AMBIGUOUS_RE, pop=False, first_only=True)
        self._log("After publisher")

    def _is_at_title_position(self, value: str) -> bool:
        """Title is in correct position."""
        title_index = self.path.find(value)

        # Titles must come after series but before format and scan_info
        if (
            title_index < self.path_index("series")
            or title_index > self.path_index("original_format", maxsize)
            or title_index > self.path_index("scan_info", maxsize)
        ):
            return False

        # Titles must be after the series and one other token.
        title_ok = False
        other_tokens_exist = False
        for preceding_key in _TITLE_PRECEDING_KEYS:
            other_tokens_exist = True
            if title_index > self.path_index(preceding_key):
                title_ok = True
                break
        return title_ok or not other_tokens_exist

    def _grouping_operators_strip(self, value: str) -> str:
        """Strip spaces and parens."""
        value = value.strip()
        value = value.strip("()").strip()
        value = value.strip("-").strip()
        value = value.strip(",").strip()
        value = value.strip("'").strip()
        return value.strip('"').strip()

    def _parse_series_and_title_token(
        self, remaining_key_index: int, tokens: list[str]
    ) -> str:
        """Parse one series or title token."""
        key = _REMAINING_GROUP_KEYS[remaining_key_index]
        if key in self.metadata:
            return ""
        token = tokens.pop(0)
        match = REMAINING_GROUP_RE.search(token)
        if not match:
            return token
        value = match.group()
        if key == "title":
            if not self._is_at_title_position(value):
                return token

            # Parse titles that are really formats as formats.
            if "original_format" not in self.metadata and (
                match := ORIGINAL_FORMAT_NAKED_RE.fullmatch(value)
            ):
                self.metadata["original_format"] = match.group()
                return ""

        value = NON_NUMBER_DOT_RE.sub(r"\1 \2", value)
        value = self._grouping_operators_strip(value)
        if value:
            self.metadata[key] = value
        return ""

    def _parse_series_and_title(self) -> None:
        """Assign series and title."""
        if not self._unparsed_path:
            return

        remaining_key_index = 0
        unused_tokens = []
        tokens = self._unparsed_path.split(TOKEN_DELIMETER)
        while tokens and remaining_key_index < len(_REMAINING_GROUP_KEYS):
            unused_token = self._parse_series_and_title_token(
                remaining_key_index, tokens
            )
            if unused_token:
                unused_tokens.append(unused_token)
            remaining_key_index += 1

        self._unparsed_path = " ".join(unused_tokens) if unused_tokens else ""
        self._log("After Series & Title")

    def _add_remainders(self) -> None:
        """Add Remainders."""
        remainders = []
        for token in self._unparsed_path.split(TOKEN_DELIMETER):
            if remainder := token.strip():
                remainders.append(remainder)

        if remainders:
            self.metadata["remainders"] = tuple(
                remainders + list(self.metadata.get("remainders", []))
            )

    def parse(self) -> dict[str, str | tuple[str, ...]]:
        """Parse the filename with a hierarchy of regexes."""
        self._log("Init")
        self._parse_ext()
        self._clean_dividers()
        self._parse_issue()
        self._parse_volume()
        self._parse_dates()
        self._parse_format_and_scan_info()
        self._parse_remainder_paren_groups()
        self._parse_ends_of_remaining_tokens()
        self._parse_publisher()
        self._parse_series_and_title()

        # Copy volume into issue if it's all we have.
        if "issue" not in self.metadata and "volume" in self.metadata:
            self.metadata["issue"] = self.metadata["volume"]
        self._log("After issue can be volume")

        self._add_remainders()

        return self.metadata

    def __init__(self, path: str | Path, verbose: int = 0):
        """Initialize."""
        self._debug: bool = verbose > 0
        # munge path
        if isinstance(path, str):
            path = path.strip()
        p_path = Path(path)
        self.path = str(p_path.name).strip()
        self.metadata: dict[str, str | tuple[str, ...]] = {}
        self._unparsed_path = copy(self.path)
        self._path_indexes: dict[str, int] = {}


def comicfn2dict(
    path: str | Path, verbose: int = 0
) -> dict[str, str | tuple[str, ...]]:
    """Simplfily the API."""
    parser = ComicFilenameParser(path, verbose=verbose)
    return parser.parse()
