# PubMed Fetcher

## Install

```bash
git clone https://github.com/yourusername/pubmed-fetcher.git
cd pubmed-fetcher
poetry install
```

## Usage

```bash
poetry run get-papers-list "cancer therapy" -f output.csv --debug
```

## Features

- Fetches paper metadata using PubMed APIs.
- Filters out academic affiliations using heuristics.
- Exports CSV with required details.
