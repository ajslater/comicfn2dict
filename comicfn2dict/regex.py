"""Parsing regexes."""

import re
from re import IGNORECASE, Pattern
from types import MappingProxyType

PUBLISHERS_UNAMBIGUOUS: tuple[str, ...] = (
    r"Abrams ComicArts",
    r"BOOM! Studios",
    r"DC(\sComics)?",
    r"Dark Horse Comics",
    r"Drawn & Quarterly",
    r"Dynamite Entertainment",
    r"IDW Publishing",
    r"Icon Comics",
    r"Kodansha",
    r"Oni Press",
    r"Pantheon Books",
    r"SLG Publishing",
    r"SelfMadeHero",
    r"Titan Comics",
)
PUBLISHERS_AMBIGUOUS: tuple[str, ...] = (
    r"(?<!Capt\.\s)(?<!Capt\s)(?<!Captain\s)Marvel",
    r"Heavy Metal",
    r"Epic",
    r"Image",
    r"Mirage",
)

ORIGINAL_FORMAT_PATTERNS: tuple[str, ...] = (
    r"Anthology",
    r"Annual",
    r"Annotation[s]?",
    r"Ashcan",
    r"Box[-\s]Set",
    r"Digital(?:[-\s](?:Chapter|Mobile|Rip))?",
    r"Director[’']?s\sCut",  # noqa: RUF001
    r"FCBD",
    r"Free[-\s]Comic[-\s]Book[-\s]Day",
    r"Giant([-\s]Size(d)?)?",
    r"Graphic[-\s]Novel",
    r"GN",
    r"Hard[-\s]?Cover",
    r"HC",
    r"HD-Upscaled",
    r"Infinity[-\s]Comic",
    r"King[-\s]Size(d)?",
    r"Limited[-\s]Series",
    r"Magazine",
    r"Manga",
    r"Mini[-\s]Series",
    r"Omnibus",
    r"(One|1)[-\s]Shot",
    r"PDF([-\s]Rip)?",
    r"Preview",
    r"Prologue",
    r"Single[-\s]Issue",
    r"Scanlation",
    r"Script",
    r"Sketch",
    r"TPB",
    r"Trade[-\s]Paper[-\s]?Back",
    r"Web([-\s]?(Comic|Rip))?",
)

MONTHS: tuple[str, ...] = (
    r"Jan(uary)?",
    r"Feb(ruary)?",
    r"Mar(ch)?",
    r"Apr(il)?",
    r"May",
    r"Jun(e)?",
    r"Jul(y)?",
    r"Aug(ust)?",
    r"Sep(tember)?",
    r"Oct(ober)?",
    r"Nov(ember)?",
    r"Dec(ember)?",
)

TOKEN_DELIMITER: str = r"/"  # noqa: S105


def re_compile(exp: str, *, parenthify: bool = False) -> Pattern:
    """Compile regex with options."""
    if parenthify:
        exp = r"\(" + exp + r"\)"
    return re.compile(exp, flags=IGNORECASE)


# CLEAN
_TOKEN_DIVIDERS_RE = re_compile(r":")
_SPACE_EQUIVALENT_RE = re_compile(r"_")
_EXTRA_SPACES_RE = re_compile(r"\s\s+")
_LEFT_PAREN_EQUIVALENT_RE = re_compile(r"\[")
_RIGHT_PAREN_EQUIVALENT_RE = re_compile(r"\]")
_DOUBLE_UNDERSCORE_RE = re_compile(r"__(.*)__")
# Open-ended series-year notation "(2022-)" and ranged "(2022-2024)" both
# get normalised to "(2022)" so the dual-year logic in _parse_dates assigns
# the start year as the volume.
_VOLUME_YEAR_RANGE_RE = re_compile(r"\(([12]\d{3})-(?:[12]\d{3})?\)")
REGEX_SUBS: MappingProxyType[Pattern, tuple[str, int]] = MappingProxyType(
    {
        _DOUBLE_UNDERSCORE_RE: (r"(\1)", 0),
        _TOKEN_DIVIDERS_RE: (TOKEN_DELIMITER, 1),
        _SPACE_EQUIVALENT_RE: (r" ", 0),
        _EXTRA_SPACES_RE: (r" ", 0),
        _LEFT_PAREN_EQUIVALENT_RE: (r"(", 0),
        _RIGHT_PAREN_EQUIVALENT_RE: (r")", 0),
        _VOLUME_YEAR_RANGE_RE: (r"(\1)", 0),
    }
)

### DATES
_YEAR_RE_EXP = r"(?P<year>[12]\d{3})"
_MONTH_ALPHA_RE_EXP = r"(" + "(?P<alpha_month>" + r"|".join(MONTHS) + r")\.?)"
_MONTH_NUMERIC_RE_EXP = r"(?P<month>0?\d|1[0-2]?)"
_MONTH_RE_EXP = r"(" + _MONTH_ALPHA_RE_EXP + r"|" + _MONTH_NUMERIC_RE_EXP + r")"
_ALPHA_MONTH_RANGE = (
    r"\b"  # noqa: ISC003
    + r"("
    + r"|".join(MONTHS)
    + r")"
    + r"("
    + r"\.?-"
    + r"("
    + r"|".join(MONTHS)
    + r")"
    + r")\b"
)
ALPHA_MONTH_RANGE_RE: Pattern = re_compile(_ALPHA_MONTH_RANGE)

_DAY_RE_EXP = r"(?P<day>([0-2]?\d|(3)[0-1]))"
_DATE_DELIM = r"[-\s]+"
_MONTH_FIRST_DATE_RE_EXP = (
    r"((\b|\(?)"
    # Month
    + _MONTH_RE_EXP
    # Day
    + r"("
    + _DATE_DELIM
    + _DAY_RE_EXP
    + r")?"
    # Year
    + r"[,]?"
    + _DATE_DELIM
    + _YEAR_RE_EXP
    + r"(\)?|\b))"
)
_YEAR_FIRST_DATE_RE_EXP = (
    r"(\b\(?"
    + _YEAR_RE_EXP
    + _DATE_DELIM
    + _MONTH_RE_EXP
    + _DATE_DELIM
    + _DAY_RE_EXP
    + r"\b\)?)"
)

MONTH_FIRST_DATE_RE: Pattern = re_compile(_MONTH_FIRST_DATE_RE_EXP)
YEAR_FIRST_DATE_RE: Pattern = re_compile(_YEAR_FIRST_DATE_RE_EXP)
YEAR_TOKEN_RE: Pattern = re_compile(_YEAR_RE_EXP, parenthify=True)
YEAR_END_RE: Pattern = re_compile(_YEAR_RE_EXP + r"\/|$")

# PAREN GROUPS
_OF_PATTERNS = r"|".join(ORIGINAL_FORMAT_PATTERNS)
_ORIGINAL_FORMAT_RE_EXP = r"(?P<original_format>" + _OF_PATTERNS + r")"
_SCAN_INFO_RE_EXP = r"(?P<scan_info>[^()]*)"
_ORIGINAL_FORMAT_SCAN_INFO_RE_EXP = (
    _ORIGINAL_FORMAT_RE_EXP + r"\s*[\(:-]" + _SCAN_INFO_RE_EXP  # + r")?"
)
# Keep this even though comicfn2dict doesn't use it directly
ORIGINAL_FORMAT_NAKED_RE: Pattern = re_compile(_ORIGINAL_FORMAT_RE_EXP)
ORIGINAL_FORMAT_RE: Pattern = re_compile(_ORIGINAL_FORMAT_RE_EXP, parenthify=True)
ORIGINAL_FORMAT_SCAN_INFO_RE: Pattern = re_compile(
    _ORIGINAL_FORMAT_SCAN_INFO_RE_EXP, parenthify=True
)
ORIGINAL_FORMAT_SCAN_INFO_SEPARATE_RE: Pattern = re_compile(
    r"\(" + _ORIGINAL_FORMAT_RE_EXP + r"\).*\(" + _SCAN_INFO_RE_EXP + r"\)"
)
# Tight variant: format and scan_info in adjacent paren groups separated only
# by whitespace. Tried before the combined-format pattern so compound formats
# like "(digital-mobile) (Empire)" are recognised as format + scan_info
# instead of being split into format=digital, scan_info=mobile.
ORIGINAL_FORMAT_SCAN_INFO_ADJACENT_RE: Pattern = re_compile(
    r"\(" + _ORIGINAL_FORMAT_RE_EXP + r"\)\s+\(" + _SCAN_INFO_RE_EXP + r"\)"
)

SCAN_INFO_SECONDARY_RE: Pattern = re_compile(r"\b(?P<secondary_scan_info>c2c)\b")

# ISSUE
_ISSUE_RE_EXP = r"(?P<issue>-?\w*(½|\d+)[\.\d+]*\w*)"
_ISSUE_COUNT_RE_EXP = r"\(of\s*(?P<issue_count>\d+)\)"
ISSUE_NUMBER_RE: Pattern = re_compile(
    r"(\(?#" + _ISSUE_RE_EXP + r"\)?)" + r"(\W*" + _ISSUE_COUNT_RE_EXP + r")?"
)
ISSUE_WITH_COUNT_RE: Pattern = re_compile(
    r"(\(?" + _ISSUE_RE_EXP + r"\)?" + r"\W*" + _ISSUE_COUNT_RE_EXP + r")"
)
ISSUE_END_RE: Pattern = re_compile(r"([\/\s]\(?" + _ISSUE_RE_EXP + r"\)?(\/|$))")
ISSUE_BEGIN_RE: Pattern = re_compile(r"((^|\/)\(?" + _ISSUE_RE_EXP + r"\)?[\/|\s])")
# Letter-only issue tokens explicitly marked with '#' (e.g. "#Omega",
# "#Alpha"). The '#' prefix is required so we don't grab series words.
ISSUE_LETTER_RE: Pattern = re_compile(r"\(?#(?P<issue>[A-Za-z]+)\)?")

# Volume
_VOLUME_COUNT_RE_EXP = r"\(of\s*(?P<volume_count>\d+)\)"
_VOLUME_RE_EXP = (
    r"((?:v(?:ol(?:ume)?)?\.?)\s*(?P<volume>\d+)(\W*"
    + _VOLUME_COUNT_RE_EXP
    + r")?"
    + r")"
)
VOLUME_RE: Pattern = re_compile(_VOLUME_RE_EXP)
VOLUME_WITH_COUNT_RE: Pattern = re_compile(
    r"(\(?" + r"(?P<volume>\d+)" + r"\)?" + r"\W*" + _VOLUME_COUNT_RE_EXP + r")"
)
# Word-number volumes: "Book One" through "Book Twenty". The match for
# the volume captures the word; ComicFilenameParser._normalize_volume
# converts it to a digit string after parsing.
WORD_NUMBERS: tuple[str, ...] = (
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
    "twenty",
)
WORD_NUMBER_TO_DIGIT: MappingProxyType[str, str] = MappingProxyType(
    {word: str(index + 1) for index, word in enumerate(WORD_NUMBERS)}
)
BOOK_VOLUME_RE: Pattern = re_compile(
    r"(?P<title>book\s*(?P<volume>\d+|" + r"|".join(WORD_NUMBERS) + r"))\b"
)

# Publisher
_PUBLISHER_UNAMBIGUOUS_RE_EXP = (
    r"(\b(?P<publisher>" + r"|".join(PUBLISHERS_UNAMBIGUOUS) + r")\b)"
)
_PUBLISHER_AMBIGUOUS_RE_EXP = (
    r"(\b(?P<publisher>" + r"|".join(PUBLISHERS_AMBIGUOUS) + r")\b)"
)
PUBLISHER_UNAMBIGUOUS_TOKEN_RE: Pattern = re_compile(
    r"(^|\/)" + _PUBLISHER_UNAMBIGUOUS_RE_EXP + r"($|\/)"
)
PUBLISHER_AMBIGUOUS_TOKEN_RE: Pattern = re_compile(
    r"(^|\/)" + _PUBLISHER_AMBIGUOUS_RE_EXP + r"($|\/)"
)
PUBLISHER_UNAMBIGUOUS_RE: Pattern = re_compile(_PUBLISHER_UNAMBIGUOUS_RE_EXP)
PUBLISHER_AMBIGUOUS_RE = re_compile(_PUBLISHER_AMBIGUOUS_RE_EXP)

# LONG STRINGS
REMAINING_GROUP_RE: Pattern = re_compile(r"^[^\(].*[^\)]")
# Replace dots between letters with spaces ("Avengers.Hulk" -> "Avengers Hulk",
# "A.X.E." -> "A X E.") without disturbing dots adjacent to spaces or digits
# ("vs. Marvel" stays put, "0.0.1" stays put). Applied iteratively because
# acronyms have overlapping matches: A.X.E -> A X.E -> A X E.
LETTER_DOT_RE: Pattern = re_compile(r"([a-zA-Z])\.([a-zA-Z])")
# After LETTER_DOT_RE flattens an acronym, a trailing dot remains on the last
# letter ("S.H.I.E.L.D." -> "S H I E L D."). Strip dots that follow a single
# letter that's at the start of the value or preceded by whitespace, when the
# dot is followed by whitespace or end-of-string. Multi-letter abbreviations
# like "Dr.", "Inc.", or "vs." are not preceded by a space-bounded single
# letter, so they're left alone.
ACRONYM_TRAIL_DOT_RE: Pattern = re_compile(r"(^|\s)([A-Za-z])\.(\s|$)")

# Strip a trailing "by Author Names" attribution from a series. Requires at
# least three whitespace-delimited tokens after "by" so legitimate names like
# "Step By Bloody Step" (one trailing token), "Werewolf By Night" (one
# trailing token), or "Thor was Raised by Frost Giants" (two trailing tokens)
# stay intact. Three-token trails cover the common comic-credits forms:
# "by First Middle Last", "by Author1 & Author2", "by Author1 and Author2".
BY_AUTHOR_RE: Pattern = re_compile(r"\s+by\s+\S+\s+\S+\s+\S+(?:\s+\S+)*\s*$")

# Either " - " or "word- " is treated as a series/title separator when it
# occurs exactly once in the remaining token. The "word- " variant catches
# filenames where the user typed "Captain America- Reborn" (no space before
# the dash) as a substitute for the canonical "Captain America: Reborn".
# Hyphens inside compound words like "X-Men" don't match because they aren't
# followed by whitespace.
DASH_SEPARATOR_RE: Pattern = re_compile(r"(?:(?<=\w)-\s+|\s+-\s+)(?=\S)")

REMAINDER_PAREN_GROUPS_RE: Pattern = re_compile(r"(?P<remainders>\(.*\))")
# A leftover paren group whose content is Title Case, alphabetic-only (no
# digits, no commas), used to promote FCBD-style subtitles like
# "Free Comic Book Day 2015 (Avengers)" -> title="Avengers". Only fires when
# it's the sole remaining paren group, which avoids confusing it with
# scan_info releaser groups like "(Shadowcat-Empire)" that follow another
# paren. The (?-i:...) inline group disables IGNORECASE on the leading
# letter so lowercase content like "(repaired)" or "(extras only)" is not
# promoted.
TITLE_PAREN_RE: Pattern = re_compile(
    r"\((?P<title>(?-i:[A-Z])[A-Za-z\s\-']*[A-Za-z])\)\s*$"
)
