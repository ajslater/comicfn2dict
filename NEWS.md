# 📰 comicfn2dict News

## v1.1.0

### 💥 Breaking Changes

- `dict2comicfn()` leaves out a month that isn't a number from 1 to 12, with its
  day, with or without a year. Such months never read back. With no year, a
  month from 1 to 12 is written as its name: `(Jan)`, `(Dec-31)`.
- `unparse.issue_formatter()` takes a str or int issue and returns the written
  token, `#001`, instead of a format string.

### ✨ Added

- [Filename Format](https://comicfn2dict.readthedocs.io/FILENAMES/) page: an
  EBNF grammar for the names `dict2comicfn()` writes, and the conventions
  `comicfn2dict()` reads.
- A JSON Schema for the metadata dict, shipped as
  `comicfn2dict/schemas/comicfn2dict.schema.json` and rendered as the
  [Metadata Schema](https://comicfn2dict.readthedocs.io/schema/comicfn2dict.schema/)
  page.
- Leftover text is kept in `remainders` instead of dropped.

### 🐛 Fixed

- What `dict2comicfn()` writes now reads back: `(2020-12)`, `(Dec)` and
  `(Dec-31)` read as dates, `v1 (of 3)` as a volume and its count, `#-001` and
  `#Omega` as their issues, and the `[...]` remainders group as one remainder,
  as written, instead of as the title.
- The parser's internal `/` delimiter no longer leaks into values, so
  `dict2comicfn()` can't write a path separator. `(c2c)`, `(Digital: Empire)`
  and paren groups on both sides of other fields were the usual causes.
- `(c2c) (Group)` reads the group as the scan info, and `(Digital: Empire)` and
  `(Digital - Empire)` read as format and scan info.
- A known format or publisher alone in parens, such as `(Digital)`, `(TPB)` or
  `(DC)`, reads as one instead of as the title.
- A year-first date after another field no longer leaves a stray `(` or swallows
  the title.
- Months outside 1 to 12 and days outside 1 to 31 no longer read as dates, as in
  `(13-31-2000)`.
- Year, day, volume and counts read only ASCII digits, as the schema says.
- `Name.` has no extension on every Python version.
- Counts are padded on the left: `(of 005)`, not `(of 500)`.
- A day without a month is left out instead of being written as a month.
- A `str` `remainders` is written whole instead of as its characters.
- An `int` issue is padded like a `str` one instead of raising.
- An empty `date` no longer hides the year, month and day, and an empty or
  `None` `ext` writes `.cbz`.
- A one-letter series or title, `S #001`, reads as one instead of as a
  remainder.
- Leftover paren groups are read one at a time, so
  `(4 covers) Series Name (repaired) #001` keeps its series, and a lone `-`
  between fields is dropped instead of kept as a remainder.
- README API and CLI examples.

## v1.0.2

### 🔥 Removed

- Remove dependency on typing-extensions

## v1.0.1

### 🔒 Security

- Security update

## v1.0.0 - Python 3.11

### 💥 Breaking Changes

- Require Python 3.11.

### 🐛 Fixed

- Long digit runs in filenames no longer stall parsing.

## v0.3.2

### 🐛 Fixed

- A parenthesized group wrapped in brackets (e.g. `[(5 covers)]`) no longer
  gains a redundant second layer of parens, so it round-trips as `[(5 covers)]`
  instead of `[((5 covers))]`.

## v0.3.1

### ✨ Added

- Add Sweet Shop kebab case filename format. Courtesy of @bpepple.

## v0.3.0

### ✨ Added

- New format patterns recognized.
- Handle lots of FCBD naming patterns.
- Word-number volumes are recognized: "Book One" through "Book Twenty"
- Strip trailing "by \<Author Names>" attribution from a series when three or
  more tokens follow "by". Single-author tails like "Werepenguin By Night" or
  "Step By Bloody Step" are preserved.
- A single dash separator (" - " or "word- ") now splits a series and title to
  align with the canonical ":" convention that filesystems disallow. Multi-dash
  co-headlining names like "Hanuman - Foolish One - Deep Target" stay in the
  series.

### 🐛 Fixed

- Smarter dot handling for Mega.Dude and B.U.C.K.L.E.R. without compromising Dr.
  or 0.0.1 versions.
- Keep publishers from sometimes being mistaken for titles.
- Year (2022-) handled correctly
- Handle #Alpha as an issue indicator more properly.

## v0.2.5

### ♻️ Changed

- Slightly expanded range of publishing format detection.

## v0.2.4

### 🐛 Fixed

- Fix parsing negative issue numbers

## v0.2.3

### 🔒 Security

- Dependencies security update

## v0.2.2

### 🐛 Fixed

- Fix extra paren groups parsed into series and title
- Parse "titles" with the exact same name as printing formats as original_format

## v0.2.1

### ✨ Added

- Support Python 3.9, thanks to @lordwelch

## v0.2.0

### ✨ Added

- Issue numbers that lead with a '#' character may start with alphabetical
  characters.
- ComicFilenameParser and ComicFilenameSerializer classes are available as well
  as the old function API.

### ♻️ Changed

- The `-` character no longer breaks up tokens
- Titles are now parsed only if they occur after the series token AND after
  either issue, year or volume.
- A more sophisticated date parser.
- If volume exists, but issue number does not, then issue number becomes the
  volume number.

### 🧑‍💻 Developer

- New test cases thanks to @lordwelch & @bpepple

## v0.1.4

### 💥 Breaking Changes

- Require Python 3.10

## v0.1.3

### 🐛 Fixed

- Fix README

## v0.1.2

### ✨ Added

- Add GN to format types.

## v0.1.1

### 🐛 Fixed

- Fix cli script installation.

## v0.1.0

### ✨ Added

- Initial release
