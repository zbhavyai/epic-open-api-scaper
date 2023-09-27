# EPIC Open API Scraper

### About

EPIC System has a documentation of their APIs at [https://open.epic.com/](https://open.epic.com/). These set of APIs are grouped together via `Category` and via the `Standard`.

When given a task about getting information about all those APIs (categorized by `Standard`) in a single document for a quick reference, I decided to write a scraper to get all the information and put it in a single document. Manully copying and pasting the information in a Google document caused a lot of formatting issues and it was not a good use of my time.

The [scaper.py](./scraper.py) script that I wrote scrapes the information from the EPIC Open API website and dumps the API information in a JSON file. Then the same script reads the very JSON file and put in an HTML file, without any additional CSS. This makes the content easy to copy and paste in a Google document.

### How to use

1. Scape the information from the EPIC Open API website and dump it in a JSON file

```bash
./scraper.py --parse
```

2. Read the JSON file and dump the information in an HTML file

```bash
./scraper.py --generate
```
