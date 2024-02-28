# comicfn2dict

An API and CLI for extracting structured comic metadata from filenames.

## Install

<!-- eslint-skip -->

```sh
pip install comicfn2dict
```

## API

<!-- eslint-skip -->

```python
from comicfn2dict import comicfn2dict, dict2comicfn

path = "Comic Series #001 Title (2024).cbz"

metadata: dict[str, str| tuple[str,...]] = comicfn2dict(path, verbose=0)

filename: str = dict2comicfn(metadata, bool=True, verbose=0)
```

## CLI

<!-- eslint-skip -->

```sh
comicfn2dict "Series Name #01 - Title (2023).cbz"
{'ext': 'cbz',
'issue': '001',
'series': 'Series Name',
'title': 'Title',
'year': '2023'}
```
