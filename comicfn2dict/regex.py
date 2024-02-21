"""Parsing regexes."""
import re


def re_compile(exp, parenthify=False):
    """Compile regex with options."""
    if parenthify:
        exp = r"\(" + exp + r"\)"
    return re.compile(exp, flags=re.IGNORECASE)


ORIGINAL_FORMAT_PATTERNS = (
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

MONTHS = (
    r"Jan(uary)?",
    r"Feb(ruary)?",
    r"Mar(ch)?",
    r"Apr(il)?",
    r"May",
    r"Jun(e)?",
    r"Jul(y)?",
    r"Aug(ust)?",
    r"Sept(ember)?",
    r"Oct(ober)?",
    r"Nov(ember)?",
    r"Dec(ember)?",
)

# CLEAN
NON_SPACE_DIVIDER_RE = re_compile(r"[_\+]")
EXTRA_SPACES_RE = re_compile(r"\s\s+")

### DATES
_YEAR_RE_EXP = r"(?P<year>[12]\d{3})"
_MONTH_ALPHA_RE_EXP = r"(?P<alpha_month>" + r"|".join(MONTHS) + r")\.?"
_MONTH_NUMERIC_RE_EXP = r"(?P<month>0?\d|1[0-2]?)"
_MONTH_RE_EXP = r"(" + _MONTH_ALPHA_RE_EXP + r"|" + _MONTH_NUMERIC_RE_EXP + r")"

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

MONTH_FIRST_DATE_RE = re_compile(_MONTH_FIRST_DATE_RE_EXP)
YEAR_FIRST_DATE_RE = re_compile(_YEAR_FIRST_DATE_RE_EXP)
YEAR_TOKEN_RE = re_compile(_YEAR_RE_EXP, parenthify=True)

# PAREN GROUPS
ISSUE_COUNT_RE = re_compile(r"of\s*(?P<issue_count>\d+)", parenthify=True)
_OF_PATTERNS = r"|".join(ORIGINAL_FORMAT_PATTERNS)
_ORIGINAL_FORMAT_RE_EXP = r"(?P<original_format>" + _OF_PATTERNS + r")"
_SCAN_INFO_RE_EXP = r"(?P<scan_info>[^()]*)"
_ORIGINAL_FORMAT_SCAN_INFO_RE_EXP = (
    _ORIGINAL_FORMAT_RE_EXP + r"\s*[\(:-]" + _SCAN_INFO_RE_EXP  # + r")?"
)
ORIGINAL_FORMAT_SCAN_INFO_RE = re_compile(
    _ORIGINAL_FORMAT_SCAN_INFO_RE_EXP, parenthify=True
)
ORIGINAL_FORMAT_SCAN_INFO_SEPARATE_RE = re_compile(
    r"\(" + _ORIGINAL_FORMAT_RE_EXP + r"\).*\(" + _SCAN_INFO_RE_EXP + r"\)"
)

# REGULAR TOKENS
VOLUME_RE = re_compile(r"((?:v(?:ol(?:ume)?)?\.?)\s*(?P<volume>\d+))")
_ISSUE_NUMBER_RE_EXP = r"(?P<issue>[\w½]+\.?\d*\w*)"
ISSUE_NUMBER_RE = re_compile(r"(#" + _ISSUE_NUMBER_RE_EXP + r")")
_ISSUE_RE_EXP = r"(?P<issue>[\d½]+\.?\d*\w*)"

ISSUE_END_RE = re_compile(r"([\/\s]" + _ISSUE_RE_EXP + r"(\/|$))")
ISSUE_BEGIN_RE = re_compile(r"((^|\/)" + _ISSUE_RE_EXP + r"[\/|\s])")
ISSUE_ANYWHERE_RE = re_compile(r"\b(" + _ISSUE_RE_EXP + r")\b")

# LONG STRINGS
REMAINING_GROUP_RE = re_compile(r"^[^\()].*[^\)]")

NON_NUMBER_DOT_RE = re_compile(r"(\D)\.(\D)")
