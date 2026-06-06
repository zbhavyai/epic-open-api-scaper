.PHONY: init update format lint run

help:
	@uv run python src/scraper.py --help

init:
	@ln -sf $(CURDIR)/.hooks/pre-commit.sh .git/hooks/pre-commit
	@uv sync

update:
	@uv lock --upgrade
	@uv sync

format:
	@uv run ruff format --force-exclude -- src

lint:
	@uv run ruff check --quiet --force-exclude -- src
	@uv run mypy --pretty -- src

run:
	@uv run python src/scraper.py

