# Epic Open API Scraper

A scraper that scrapes APIs from the [Epic Open API website](https://open.epic.com/Interface/). It saves the results to a structured JSON file and generates a clean, minimalist HTML report.

## Features

- **Unified Flow**: A single command runs the parser and immediately generates the HTML report.
- **Centralized Configuration**: All outputs and network settings are centralized in a single configuration file.
- **Modular Design**: Separates the scraper CLI, parser/HTML generator, and shared utilities.
- **Quality Ensured**: Codebase is fully formatted with `ruff` and type-checked with `mypy`.
- **Logs**: Execution logs are written to `logs/scraper.log`.

## Quick Start

1. Install dependencies

   ```shell
   make init
   ```

2. Run the scraper

   ```shell
   make run
   ```

3. The HTML report is generated at [output/scrape_results.html](output/scrape_results.html)
