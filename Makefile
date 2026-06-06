.PHONY: init update format lint run

help: ## show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-10s - %s\n", $$1, $$2}'

init: ## install hook and dependencies
	@ln -sf $(CURDIR)/.hooks/pre-commit.sh .git/hooks/pre-commit
	@uv sync

update: ## update dependencies
	@uv lock --upgrade
	@uv sync

format: ## format the codebase
	@uv run ruff format --force-exclude -- src

lint: ## lint the codebase
	@uv run ruff check --quiet --force-exclude -- src
	@uv run mypy --pretty -- src

run: ## run the scraper
	@uv run python src/scraper.py

