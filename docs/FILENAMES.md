# Filename Format

comicfn2dict writes comic filenames in one form and reads them in many. This
page defines the form that `dict2comicfn()` writes as a grammar, then lists the
conventions that `comicfn2dict()` recognises when it reads. The
[Metadata Schema](schema/comicfn2dict.schema.md) defines the dict that both
functions use. The package ships it as
`comicfn2dict/schemas/comicfn2dict.schema.json`.

## Writing filenames

The grammar uses the EBNF notation of the
[XML specification](https://www.w3.org/TR/xml/#sec-notation):

- `Symbol ::= expression` defines a symbol.
- `"text"` is a literal, `#xN` is the character with hex code `N`, and `[0-9]`
  or `[^/]` is a character class or its complement.
- `A?` is optional, `A*` is zero or more, `A+` is one or more, and `A | B` is
  either.
- `/* ... */` is a comment. Here it names the metadata key that a symbol writes.
- `[ wfc: Name ]` names a constraint that the productions can't express. Each is
  defined under [Constraints](#constraints).

```text
[1]  Filename       ::= Basename Extension?
[2]  Basename       ::= Fields? Remainders?
[3]  Fields         ::= Series? (S? Volume)? (S? VolumeCount)? (S? Issue)?
                        (S? IssueCount)? (S? Date)? (S? Title)? (S? Publisher)?
                        (S? OriginalFormat)? (S? ScanInfo)?
                        [ wfc: Field Separation ]
[4]  Series         ::= Text                          /* series */
[5]  Volume         ::= "v" Digit+                    /* volume */
[6]  VolumeCount    ::= Count                         /* volume_count */
[7]  Issue          ::= "#" Digit Digit Digit Char*   /* issue */
                        [ wfc: Issue Padding ]
[8]  IssueCount     ::= Count                         /* issue_count */
[9]  Date           ::= "(" DateValue ")"
[10] DateValue      ::= Year ("-" Month ("-" Day)?)?  /* year, month, day */
                      | MonthName ("-" Day)?          /* month, day */
                      | Month ("-" Day)?              /* month, day */
                      | Text                          /* date */
                        [ wfc: Month Name ]
[11] Year           ::= [12] Digit Digit Digit
[12] Month          ::= Digit Digit?
[13] Day            ::= Digit Digit?
[14] MonthName      ::= "Jan" | "Feb" | "Mar" | "Apr" | "May" | "Jun"
                      | "Jul" | "Aug" | "Sep" | "Oct" | "Nov" | "Dec"
[15] Title          ::= Text                          /* title */
[16] Publisher      ::= "(" Text ")"                  /* publisher */
[17] OriginalFormat ::= "(" Text ")"                  /* original_format */
[18] ScanInfo       ::= "(" Text ")"                  /* scan_info */
[19] Remainders     ::= "[" Text (S Text)* "]"        /* remainders */
[20] Extension      ::= "." Text                      /* ext */
[21] Count          ::= "(of " Digit Digit Digit+ ")"
                        [ wfc: Count Padding ]
[22] Text           ::= Char+
[23] Char           ::= [^/#x0]
[24] Digit          ::= [0-9]
[25] S              ::= #x20
```

`Text` is any run of characters a filename can hold. `dict2comicfn()` writes
each value as it is, so keeping `/` out of the values is up to the caller.

Read as a parser, this grammar is ambiguous. `Text` can hold spaces,
parentheses, `#` and `-`, so a filename can split into fields more than one way.
The grammar says how `dict2comicfn()` writes;
[Reading filenames](#reading-filenames) says how `comicfn2dict()` reads.

### Fields

- **Fields** come in a fixed order: series, volume, volume count, issue, issue
  count, date, title, publisher, original format, scan info.
- **Date** is the `date` key when it is set. Otherwise it's built from `year`,
  `month` and `day`, joined with `-`. A day without a month is left out, because
  it would read back as a month.
- **Remainders** joins the `remainders` strings with spaces, inside one pair of
  square brackets. A single string is written as it is.
- **Extension** is the `ext` key, or `cbz` when the key is missing. It's left
  off when `dict2comicfn()` is called with `ext=False`.

### Constraints

**Field Separation:** one space separates adjacent fields, and none comes before
the first. Each field is trimmed of surrounding whitespace. A field whose key is
missing or empty is left out, with its space. `Remainders` and `Extension`
follow the last field with no space.

**Issue Padding:** the issue is padded on the left with zeros until it starts
with three digits. An issue that already does is written as it is: `1` becomes
`#001`, `1.5` becomes `#001.5`, `27AU` becomes `#027AU`, `½` becomes `#000½` and
`1024` stays `#1024`.

**Month Name:** with no year, a month from 1 to 12 is written as its name, so
`12` becomes `Dec`. Any other month is written as it is, so `0` stays `0`. A
month that follows a year is always written as it is.

**Count Padding:** a count shorter than three digits is padded on the left with
zeros to three, whether it's a string or an int: `"5"`, `"05"` and `5` are all
written `(of 005)`.

### Examples

```python
from comicfn2dict import dict2comicfn

dict2comicfn(
    {
        "series": "Long Series Name",
        "volume": "1",
        "issue": "1",
        "year": "2000",
        "title": "Title",
        "original_format": "TPB",
        "scan_info": "Releaser & Releaser-Releaser",
        "ext": "cbr",
    }
)
# 'Long Series Name v1 #001 (2000) Title (TPB) (Releaser & Releaser-Releaser).cbr'

dict2comicfn({"series": "Series Name", "year": "2000", "month": "12", "day": "31"})
# 'Series Name (2000-12-31).cbz'

dict2comicfn({"series": "Series Name", "month": "12", "day": "31"})
# 'Series Name (Dec-31).cbz'

dict2comicfn(
    {
        "series": "Conan the Barbarian",
        "issue": "001",
        "year": "2025",
        "title": "Scourge of the Serpent",
        "original_format": "Digital",
        "scan_info": "Mephisto-Empire",
        "remainders": ("(5 covers)",),
    }
)
# 'Conan the Barbarian #001 (2025) Scourge of the Serpent (Digital) (Mephisto-Empire)[(5 covers)].cbz'
```

## Reading filenames

`comicfn2dict()` reads far more than the written form. It works in passes. Each
pass is a regular expression that takes the part of the name it recognises, and
the text left at the end becomes the series, title and remainders. A name can
often match these conventions more than one way, and the order of the passes
decides. So the reader has no grammar. These are the conventions it recognises,
with examples from its test cases. Each result lists only the keys that the
example is about.

### Separators

The last suffix is the extension. `_` reads as a space, and runs of spaces
collapse to one. `[` and `]` read as `(` and `)`, and `__text__` reads as
`(text)`. The first `:` splits the name into separate runs of text.

| Filename                                                                            | Reads                                                                                |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `Batman_-_Superman_#020_(2021).cbr`                                                 | `series: Batman`, `title: Superman`, `ext: cbr`                                      |
| `Monster_Island_v1_#2__repaired__c2c.cbz`                                           | `series: Monster Island`, `remainders: ("(repaired)",)`                              |
| `Cory Doctorow's Futuristic Tales of the Here and Now: Anda's Game #001 (2007).cbz` | `series: Cory Doctorow's Futuristic Tales of the Here and Now`, `title: Anda's Game` |

### Issue

The issue is a number after `#`, which may carry a decimal, a fraction, a sign
or a suffix. A `#` before letters gives a letter issue. Without a `#`, the issue
is a number before `(of N)`, a number after the word `issue`, or a number that
ends or starts a run of text.

| Filename                                                                  | Reads                               |
| ------------------------------------------------------------------------- | ----------------------------------- |
| `The Walking Dead #002 (2003).cbz`                                        | `issue: 002`                        |
| `Earth X #½.cbz`                                                          | `issue: ½`                          |
| `The Sensational Spider-Man v1 #-1 (1997).cbz`                            | `issue: -1`                         |
| `The Amazing Spider-Man #54.LR.cbz`                                       | `issue: 54.LR`                      |
| `Crimson Saga #Omega (2022).cbz`                                          | `issue: Omega`                      |
| `King of Skittles 01 (of 05) (2020) (digital) (Son of Ultron-Empire).cbr` | `issue: 01`, `issue_count: 05`      |
| `radiant-black-issue-1.pdf`                                               | `series: radiant black`, `issue: 1` |
| `A Fractional Comic 8.54.cbz`                                             | `issue: 8.54`                       |

### Volume

The volume follows `v`, `Vol.` or `Volume`, comes before `(of N)` once the name
has an issue, or is the number in `Book N`, where `N` may be a word from `One`
to `Twenty`. When a name holds two parenthesized years, the first is the volume.
A year range such as `(2022-)` or `(2020-2024)` reads as its first year. With no
issue, the volume is also the issue.

| Filename                                                                  | Reads                                          |
| ------------------------------------------------------------------------- | ---------------------------------------------- |
| `33475 OMAC v3 2.cbr`                                                     | `volume: 3`, `issue: 2`                        |
| `Kartalk Library Edition v01 (1992) (digital) (Son of Ultron-Empire).cbr` | `volume: 01`, `issue: 01`                      |
| `Elephantmen 2259 #008 - Simple Truth 03 (of 06) (2021).cbr`              | `volume: 03`, `volume_count: 06`, `issue: 008` |
| `Brick Walker's Beanbag Book One.cbz`                                     | `volume: 1`, `title: Book One`                 |
| `Super Strange Yarns (1957) #92 (1969).cbz`                               | `volume: 1957`, `year: 1969`                   |
| `Cosmic Battles - Hermit (2022-) #001 (2023).cbz`                         | `volume: 2022`, `year: 2023`                   |

### Date

The year is four digits starting with `1` or `2`, in parentheses, in a date, or
ending a run of text. A date runs month first or year first, with the month as a
number or a name. Of a month range such as `Sep-Oct`, only the first month is
kept.

| Filename                                                                                                                 | Reads                                |
| ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------ |
| `Night of 1000 Wolves 001 (2013).cbz`                                                                                    | `year: 2013`                         |
| `Marvel Previews #002 (January 2022).cbr`                                                                                | `year: 2022`, `month: 01`            |
| `Test Numeric Year #2 2001-02-24.cbz`                                                                                    | `year: 2001`, `month: 02`, `day: 24` |
| `Test Month First Date 02-24-2001.cbz`                                                                                   | `year: 2001`, `month: 02`, `day: 24` |
| `Wonder Woman #49 DC Sep-Oct 1951 digital [downsized, lightened, 4 missing story pages restored] (Shadowcat-Empire).cbz` | `year: 1951`, `month: 09`            |

### Original format and scan info

An original format is one of a list of known formats, such as `TPB`, `Digital`
or `HC`. The scan info is the parenthesized group after it, or the text after a
`-` or `:` inside the format's group. A bare `c2c` is scan info when there is no
other.

| Filename                                                    | Reads                                                |
| ----------------------------------------------------------- | ---------------------------------------------------- |
| `Darkwad 011 (2019) (Digital) (Zone-Empire).cbr`            | `original_format: Digital`, `scan_info: Zone-Empire` |
| `Jeremy John - Not A Title (2017) (digital-Minutement).cbz` | `original_format: digital`, `scan_info: Minutement`  |
| `Marvel Two In One V1 #090  c2c.cbr`                        | `scan_info: c2c`                                     |

### Series and title

The series is the first run of text left after the other passes. The title is
the next run, when it comes after an issue, volume, year or month and before the
original format and scan info. When only one run is left, a single dash followed
by a space splits it into series and title. Two or more such dashes stay in the
series. A lone parenthesized group in Title Case is a title. A lowercase one is
a remainder.

Dots between letters become spaces, and an acronym loses its trailing dot. A
trailing credit of three or more words after `by` is dropped from the series.

| Filename                                                 | Reads                                                   |
| -------------------------------------------------------- | ------------------------------------------------------- |
| `Long Series Name 001 (2000) Title (TPB) (Releaser).cbz` | `series: Long Series Name`, `title: Title`              |
| `Bardude - The Last Thing I Remember.cbz`                | `series: Bardude`, `title: The Last Thing I Remember`   |
| `Knight Hour- Repealed #001 (2009).cbz`                  | `series: Knight Hour`, `title: Repealed`                |
| `Sea King - Bow Hunter - Deep Object #001 (2021).cbr`    | `series: Sea King - Bow Hunter - Deep Object`           |
| `Festival Showcase 2001 (Hidden Realm) #001 (2001).cbz`  | `series: Festival Showcase 2001`, `title: Hidden Realm` |
| `Free Comic Book Day - Avengers.Hulk (2021).cbz`         | `series: Free Comic Book Day`, `title: Avengers Hulk`   |
| `Z.O.O. - Wandering Heroes #001 (2022).cbz`              | `series: Z O O`, `title: Wandering Heroes`              |
| `Avengers By Brian Michael Bendis volume 03 (2013).cbz`  | `series: Avengers`                                      |
| `Watchman By Moonlight #001 (2023).cbz`                  | `series: Watchman By Moonlight`                         |

### Publisher

A publisher is one of a list of known names, such as `DC`, `Marvel` or `Image`.
A publisher that stands as its own run of text, beside other runs, is taken out
of the name. Otherwise it stays in the series as well.

| Filename                                                                                                                 | Reads                                          |
| ------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------- |
| `Wonder Woman #49 DC Sep-Oct 1951 digital [downsized, lightened, 4 missing story pages restored] (Shadowcat-Empire).cbz` | `publisher: DC`, `series: Wonder Woman`        |
| `Marvel Previews #002 (January 2022).cbr`                                                                                | `publisher: Marvel`, `series: Marvel Previews` |
| `Mirage #001 (2020).cbz`                                                                                                 | `publisher: Mirage`, `series: Mirage`          |

### Remainders

Parenthesized groups that no pass took stay together as one remainder. Runs of
text that no pass took stay together as another: a run that is out of place for
a title, such as one after the scan info, and any runs left once the series and
title are taken.

| Filename                                                              | Reads                                         |
| --------------------------------------------------------------------- | --------------------------------------------- |
| `Jeremy John 003 (2007) (4 covers) (digital) (Minutemen-Faessla).cbz` | `remainders: ("(4 covers)",)`                 |
| `Quagmire (or how to fix everything) #001 (2023).cbz`                 | `remainders: ("(or how to fix everything)",)` |
| `Long Series Name 001 (2000) (TPB-Releaser) Title.cbz`                | `remainders: ("Title",)`                      |
| `Long Series Name 001 (2000) Title (TPB) (Releaser) Extra.cbz`        | `title: Title`, `remainders: ("Extra",)`      |
| `Long Series Name 001 (2000) (TPB-Releaser) Out: Of Place.cbz`        | `remainders: ("Out Of Place",)`               |
