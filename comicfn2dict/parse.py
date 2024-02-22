"""Parse comic book archive names using the simple 'parse' parser."""
from pprint import pprint
from calendar import month_abbr
from copy import copy
from pathlib import Path
from re import Pattern
from typing import Any

from comicfn2dict.regex import (
    ALPHA_MONTH_RANGE_RE,
    BOOK_VOLUME_RE,
    ISSUE_ANYWHERE_RE,
    ISSUE_BEGIN_RE,
    ISSUE_END_RE,
    ISSUE_NUMBER_RE,
    ISSUE_WITH_COUNT_RE,
    MONTH_FIRST_DATE_RE,
    NON_NUMBER_DOT_RE,
    ORIGINAL_FORMAT_SCAN_INFO_RE,
    ORIGINAL_FORMAT_SCAN_INFO_SEPARATE_RE,
    PUBLISHER_AMBIGUOUS_RE,
    PUBLISHER_UNAMBIGUOUS_RE,
    PUBLISHER_AMBIGUOUS_TOKEN_RE,
    PUBLISHER_UNAMBIGUOUS_TOKEN_RE,
    REGEX_SUBS,
    REMAINING_GROUP_RE,
    SCAN_INFO_SECONDARY_RE,
    TOKEN_DELIMETER,
    VOLUME_RE,
    VOLUME_WITH_COUNT_RE,
    YEAR_END_RE,
    YEAR_FIRST_DATE_RE,
    YEAR_TOKEN_RE,
)

_REMAINING_GROUP_KEYS = ("series", "title")
_TITLE_PRECEDING_KEYS = ("issue", "year", "volume")
_DATE_KEYS = frozenset({"year", "month", "day"})


class ComicFilenameParser:
    def path_index(self, key: str):
        """Lazily retrieve and memoize the key's location in the path."""
        if key == "remainders":
            return -1
        value: str = self.metadata.get(key, "")  # type: ignore
        if not value:
            return -1
        if value not in self._path_indexes:
            # TODO This is fragile.
            #      Better to get it at match time.
            if key == "ext":
                index = self.path.rfind(value)
            else:
                index = self.path.find(value)
            self._path_indexes[value] = index
        return self._path_indexes[value]

    def _parse_ext(self):
        """Pop the extension from the pathname."""
        path = Path(self._unparsed_path)
        suffix = path.suffix
        if not suffix:
            return

        data = path.name.removesuffix(suffix)
        ext = suffix.lstrip(".")
        self.metadata["ext"] = ext
        self._unparsed_path = data

    def _grouping_operators_strip(self, value: str) -> str:
        """Strip spaces and parens."""
        value = value.strip()
        value = value.strip("()").strip()
        value = value.strip("-").strip()
        value = value.strip(",").strip()
        value = value.strip("'").strip()
        return value.strip('"').strip()

    def _parenthify_double_underscores(self) -> str:
        """Replace double underscores with parens."""
        parts = self._unparsed_path.split("__")
        num_parts = len(parts)
        print(f"{num_parts=} {num_parts % 2}")
        if num_parts < 3 or not num_parts % 2:
            return self._unparsed_path
        index = 0
        mode = " ("
        parenthified = parts[index]
        index += 1
        while index < len(parts):
            parenthified += mode + parts[index]
            print(f"{parenthified=}")
            mode = ") " if mode == " (" else ") "
            index += 1
        return parenthified.strip()

    def _clean_dividers(self):
        """Replace non space dividers and clean extra spaces out of string."""
        data = self._parenthify_double_underscores()

        # Simple substitutions
        for regex, pair in REGEX_SUBS.items():
            replacement, count = pair
            data = regex.sub(replacement, data, count=count).strip()
        self._unparsed_path = data.strip()

    def _parse_items(
        self,
        regex: Pattern,
        require_all: bool = False,
        exclude: str = "",
        first_only: bool = False,
        pop: bool = True,
    ) -> None:
        """Parse a value from the data list into metadata and alter the data list."""
        matches = regex.search(self._unparsed_path)
        if not matches:
            return
        matched_metadata = {}
        for key, value in matches.groupdict().items():
            if value == exclude:
                continue
            if not value:
                if require_all:
                    return
                continue
            # TODO idk if strip is necessary here
            matched_metadata[key] = self._grouping_operators_strip(value)
            if first_only:
                break
        self.metadata.update(matched_metadata)

        if not matched_metadata or not pop:
            return
        count = 1 if first_only else 0
        marked_str = regex.sub(TOKEN_DELIMETER, self._unparsed_path, count=count)
        parts = []
        for part in marked_str.split(TOKEN_DELIMETER):
            if token := part.strip():
                parts.append(token)
        self._unparsed_path = TOKEN_DELIMETER.join(parts)

    def _alpha_month_to_numeric(self):
        """Translate alpha_month to numeric month."""
        if alpha_month := self.metadata.pop("alpha_month", ""):
            alpha_month = alpha_month.capitalize()  # type: ignore
            for index, abbr in enumerate(month_abbr):
                if abbr and alpha_month.startswith(abbr):
                    month = f"{index:02d}"
                    self.metadata["month"] = month
                    break

    def _parse_dates(self):
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

    def _is_title_in_position(self, value):
        """Does the title come after series and one other token if they exist."""
        title_index = self.path.find(value)

        # Does a series come first.
        if title_index < self.path_index("series"):
            return False

        # If other tokens exist then they much precede the title.
        title_ok = False
        other_tokens_exist = False
        for preceding_key in _TITLE_PRECEDING_KEYS:
            other_tokens_exist = True
            if title_index > self.path_index(preceding_key):
                title_ok = True
                break
        return title_ok or not other_tokens_exist

    def _assign_remaining_groups(self):
        """Assign series and title."""
        if not self._unparsed_path:
            return

        remaining_key_index = 0
        unused_tokens = []
        tokens = self._unparsed_path.split(TOKEN_DELIMETER)
        while tokens and remaining_key_index < len(_REMAINING_GROUP_KEYS):
            key = _REMAINING_GROUP_KEYS[remaining_key_index]
            if key in self.metadata:
                continue
            token = tokens.pop(0)
            match = REMAINING_GROUP_RE.search(token)
            if match:
                value = match.group()
                if key == "title" and not self._is_title_in_position(value):
                    unused_tokens.append(token)
                    continue
                value = self._grouping_operators_strip(value)
                value = NON_NUMBER_DOT_RE.sub(r"\1 \2", value)

                self.metadata[key] = value
                remaining_key_index += 1
            else:
                unused_tokens.append(token)

        self._unparsed_path = " ".join(unused_tokens) if unused_tokens else ""

    def _add_remainders(self):
        """Add Remainders."""
        remainders = []
        for token in self._unparsed_path.split(TOKEN_DELIMETER):
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
            combined[key] = (self.metadata.get(key), self.path_index(key))
        pprint(combined)
        print(self._unparsed_path)

    def parse(self) -> dict[str, Any]:
        """Parse the filename with a hierarchy of regexes."""
        # Init
        #
        self._log_progress("INITIAL")
        self._parse_ext()
        self._clean_dividers()
        self._log_progress("CLEANED")

        # Issue
        #
        self._parse_items(ISSUE_NUMBER_RE)
        if "issue" not in self.metadata:
            self._parse_items(ISSUE_WITH_COUNT_RE)
        # self._parse_items(ISSUE_COUNT_RE)
        self._log_progress("AFTER ISSUE")

        # Volume and Date
        #
        self._parse_items(VOLUME_RE)
        if "volume" not in self.metadata:
            self._parse_items(VOLUME_WITH_COUNT_RE)
        self._parse_dates()
        self._log_progress("AFTER VOLUME & DATE")

        # Format & Scan Info
        #
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

        self._log_progress("AFTER PAREN TOKENS")

        # Series and Title
        #
        # Volume left on the end of string tokens
        if "volume" not in self.metadata:
            self._parse_items(BOOK_VOLUME_RE)

        # Years left on the end of string tokens
        year_end_matched = False
        if "year" not in self.metadata:
            self._parse_items(YEAR_END_RE, pop=False)
            year_end_matched = "year" in self.metadata

        # Issue left on the end of string tokens
        if "issue" not in self.metadata and not year_end_matched:
            exclude: str = self.metadata.get("year", "")  # type: ignore
            self._parse_items(ISSUE_END_RE, exclude=exclude)
        if "issue" not in self.metadata:
            self._parse_items(ISSUE_BEGIN_RE)
        self._log_progress("AFTER ISSUE PICKUP")

        # Publisher
        #
        # Pop single tokens so they don't end up titles.
        self._parse_items(PUBLISHER_UNAMBIGUOUS_TOKEN_RE, first_only=True)
        if "publisher" not in self.metadata:
            self._parse_items(PUBLISHER_AMBIGUOUS_TOKEN_RE, first_only=True)
        if "publisher" not in self.metadata:
            self._parse_items(PUBLISHER_UNAMBIGUOUS_RE, pop=False, first_only=True)
        if "publisher" not in self.metadata:
            self._parse_items(PUBLISHER_AMBIGUOUS_RE, pop=False, first_only=True)

        self._assign_remaining_groups()
        self._log_progress("AFTER SERIES AND TITLE")

        # Final try for issue number.
        # TODO unused
        if "issue" not in self.metadata:
            self._parse_items(ISSUE_ANYWHERE_RE)
        self._log_progress("AFTER ISSUE PICKUP")

        # Copy volume into issue if it's all we have.
        #
        if "issue" not in self.metadata and "volume" in self.metadata:
            self.metadata["issue"] = self.metadata["volume"]

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


def comicfn2dict(path: str | Path):
    """Simple API."""
    return ComicFilenameParser(path).parse()
