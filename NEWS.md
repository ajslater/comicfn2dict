# 📰 comicfn2dict News

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
