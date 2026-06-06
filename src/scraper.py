#!/usr/bin/env python3

"""
Author: Bhavyai Gupta
Description: CLI entrypoint to scrape the website "https://open.epic.com/Interface/" for all set of APIs
"""

import click

from parser import beginParse, generateHTML
from utils import configure_logging


@click.command()
def main() -> None:
    """Scrape https://open.epic.com/Interface/ for all set of APIs,
    saving to JSON and generating HTML.
    """
    configure_logging()
    beginParse()
    generateHTML()


if __name__ == "__main__":
    main()
