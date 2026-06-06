#!/usr/bin/env python3

"""
Author: Bhavyai Gupta
Description: CLI entrypoint to scrape the website "https://open.epic.com/Interface/" for all set of APIs
"""

from pathlib import Path

import click

from parser import beginParse, generateSingleHTML
from utils import configure_logging


@click.group()
def cli() -> None:
    """Scrape https://open.epic.com/Interface/ for all set of APIs."""
    configure_logging()


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(writable=True, path_type=Path),
    default=Path("output/scrape_results.json"),
    help="Path to save output JSON.",
)
def parse(output: Path) -> None:
    """Parse the data from the website."""
    beginParse(output)


@cli.command()
@click.option(
    "-i",
    "--input-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=Path("output/scrape_results.json"),
    help="Path to source JSON file.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(writable=True, path_type=Path),
    default=Path("output/scrape_results.html"),
    help="Path to save generated HTML.",
)
def generate(input_file: Path, output: Path) -> None:
    """Generate HTML from the parsed data."""
    generateSingleHTML(input_file, output)


if __name__ == "__main__":
    cli()
