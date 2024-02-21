# 📰 comicfn2dict News

## v0.2.0

- Titles are now parsed only if they occur after the series token AND after
  either issue, year or volume.
- A more sophisticated date parser.
- Issue numbers that lead with a '#' character may start with alphabetical
  characters.
- If volume is parsed, but issue number is not, the issue number is copied from
  the volume number.
- ComicFilenameParser and ComicFilenameSerializer classes are available as well
  as the old function API.

## v0.1.4

- Require Python 3.10

## v0.1.3

- Fix README

## v0.1.2

- Add GN to format types.

## v0.1.1

- Fix cli script installation.

## v0.1.0

- Initial release
