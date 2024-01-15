# comicfn2dict

An API and CLI for extracting structured comic metadata from filenames.

## Install

```sh
pip install comicfn2dict
```

## API

look at `comicfn2dict/comicfn2dict.py`

## CLI

```sh
comicfn2dict "Series Name #01 - Title (2023).cbz"
{'ext': 'cbz',
'issue': '001',
'series': 'Series Name',
'title': 'Title',
'year': '2023'}
```
