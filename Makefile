.PHONY: init update format lint parse html

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

parse:
	@uv run python src/scraper.py --parse

html:
	@uv run python src/scraper.py --generate
