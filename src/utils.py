import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import requests

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

SESSION = requests.Session()
SESSION.headers.update(DEFAULT_HEADERS)

logger = logging.getLogger("scraper")


def configure_logging() -> None:
    log_file_path = Path("output/scraper.log")
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    handlers: list[logging.Handler] = [
        logging.StreamHandler(),
        RotatingFileHandler(
            log_file_path,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
        ),
    ]

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )


def getBaseURL() -> str:
    return "https://open.epic.com"


def getHTMLContent(url: str) -> str:
    """Returns the page content for the given URL."""
    response = SESSION.get(url, timeout=10)
    response.raise_for_status()
    return response.text


def readDataJSON(filepath: Path) -> list[dict]:
    """Reads the data from a JSON file."""
    with filepath.open() as infile:
        return json.load(infile)


def storeDataJSON(allResults: list[dict], filepath: Path) -> None:
    """Stores the data in a JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with filepath.open("w") as outfile:
        json.dump(allResults, outfile, indent=2)
