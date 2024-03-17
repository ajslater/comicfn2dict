"""Parsing regexes."""

from re import IGNORECASE, Pattern, compile
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
    r"(One|1)[-\s]Shot",
    r"Annual",
    r"Annotation[s]?",
    r"Box[-\s]Set",
    r"Digital",
    r"Director[’']?s\sCut",  # noqa: RUF001
    r"Giant([-\s]Size(d)?)?",
    r"Graphic\sNovel",
    r"GN",
    r"Hard[-\s]?Cover",
    r"HC",
    r"HD-Upscaled",
    r"King[-\s]Size(d)?",
    r"Magazine",
    r"Manga?",
    r"Omnibus",
    r"PDF([-\s]Rip)?",
    r"Preview",
    r"Prologue",
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

TOKEN_DELIMETER: str = r"/"


def re_compile(exp: str, parenthify: bool = False) -> Pattern:
    """Compile regex with options."""
    if parenthify:
        exp = r"\(" + exp + r"\)"
    return compile(exp, flags=IGNORECASE)


# CLEAN
_TOKEN_DIVIDERS_RE = re_compile(r":")
_SPACE_EQUIVALENT_RE = re_compile(r"_")
_EXTRA_SPACES_RE = re_compile(r"\s\s+")
_LEFT_PAREN_EQUIVALENT_RE = re_compile(r"\[")
_RIGHT_PAREN_EQUIVALENT_RE = re_compile(r"\]")
_DOUBLE_UNDERSCORE_RE = re_compile(r"__(.*)__")
REGEX_SUBS: MappingProxyType[Pattern, tuple[str, int]] = MappingProxyType(
    {
        _DOUBLE_UNDERSCORE_RE: (r"(\1)", 0),
        _TOKEN_DIVIDERS_RE: (TOKEN_DELIMETER, 1),
        _SPACE_EQUIVALENT_RE: (r" ", 0),
        _EXTRA_SPACES_RE: (r" ", 0),
        _LEFT_PAREN_EQUIVALENT_RE: (r"(", 0),
        _RIGHT_PAREN_EQUIVALENT_RE: (r")", 0),
    }
)

### DATES
_YEAR_RE_EXP = r"(?P<year>[12]\d{3})"
_MONTH_ALPHA_RE_EXP = r"(" + "(?P<alpha_month>" + r"|".join(MONTHS) + r")\.?" r")"
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

SCAN_INFO_SECONDARY_RE: Pattern = re_compile(r"\b(?P<secondary_scan_info>c2c)\b")

# ISSUE
_ISSUE_RE_EXP = r"(?P<issue>\w*(½|\d+)[\.\d+]*\w*)"
_ISSUE_COUNT_RE_EXP = r"\(of\s*(?P<issue_count>\d+)\)"
ISSUE_NUMBER_RE: Pattern = re_compile(
    r"(\(?#" + _ISSUE_RE_EXP + r"\)?)" + r"(\W*" + _ISSUE_COUNT_RE_EXP + r")?"
)
ISSUE_WITH_COUNT_RE: Pattern = re_compile(
    r"(\(?" + _ISSUE_RE_EXP + r"\)?" + r"\W*" + _ISSUE_COUNT_RE_EXP + r")"
)
ISSUE_END_RE: Pattern = re_compile(r"([\/\s]\(?" + _ISSUE_RE_EXP + r"\)?(\/|$))")
ISSUE_BEGIN_RE: Pattern = re_compile(r"((^|\/)\(?" + _ISSUE_RE_EXP + r"\)?[\/|\s])")

# Volume
_VOLUME_COUNT_RE_EXP = r"\(of\s*(?P<volume_count>\d+)\)"
VOLUME_RE: Pattern = re_compile(
    r"(" + r"(?:v(?:ol(?:ume)?)?\.?)\s*(?P<volume>\d+)"  # noqa: ISC003
    r"(\W*" + _VOLUME_COUNT_RE_EXP + r")?" + r")"
)
VOLUME_WITH_COUNT_RE: Pattern = re_compile(
    r"(\(?" + r"(?P<volume>\d+)" + r"\)?" + r"\W*" + _VOLUME_COUNT_RE_EXP + r")"
)
BOOK_VOLUME_RE: Pattern = re_compile(r"(?P<title>" + r"book\s*(?P<volume>\d+)" + r")")

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
NON_NUMBER_DOT_RE: Pattern = re_compile(r"(\D)\.(\D)")

REMAINDER_PAREN_GROUPS_RE: Pattern = re_compile(r"(?P<remainders>\(.*\))")
