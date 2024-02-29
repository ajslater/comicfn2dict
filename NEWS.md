# 📰 comicfn2dict News

## v0.2.0

- The `-` character no longer breaks up tokens
- Titles are now parsed only if they occur after the series token AND after
  either issue, year or volume.
- A more sophisticated date parser.
- Issue numbers that lead with a '#' character may start with alphabetical
  characters.
- If volume exists, but issue number does not, then issue number becomes
  the volume number.
- ComicFilenameParser and ComicFilenameSerializer classes are available as well
  as the old function API.
- New test cases thanks to @lordwelch & @bpepple

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
