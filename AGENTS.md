# Repository Guidelines

## Project Structure & Module Organization
- Root script: `main.py` (entry point for scraping and Grist upload).
- Config: `.env` (required: `GRIST_API_KEY`, `GRIST_DOC_ID`).
- Python metadata: `pyproject.toml` (Python >= 3.12), `requirements.txt`.
- Outputs: CSV files written to repo root (e.g., `real_estate_agents_in_*.csv`).
- Virtual envs: `venv/` or `.venv/` (ignored by Git).

## Build, Test, and Development Commands
- Create venv: `python3 -m venv venv && source venv/bin/activate`.
- Install deps: `pip install -r requirements.txt` (or `uv sync`).
- Run locally: `python main.py`.
- Optional with uv: `uv run python main.py`.
- Chrome for Selenium: start a local Chrome with debugging: `google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/selenium` (adjust binary name per OS).

## Coding Style & Naming Conventions
- Style: PEP 8, 4-space indentation.
- Names: `snake_case` for functions/variables, `UPPER_SNAKE_CASE` for constants/env keys.
- Docstrings: short, imperative summaries for public functions.
- Imports: standard lib → third-party → local; group and alphabetize within groups.

## Testing Guidelines
- Framework: `pytest` (recommended; not yet included). Add tests under `tests/` with `test_*.py` filenames.
- Unit focus: pure helpers like `parse_count` are good candidates.
- Run tests: `pytest -q` (after `pip install pytest`). Aim for ~80% coverage where practical.

## Commit & Pull Request Guidelines
- Commits: concise, imperative mood (e.g., "extract followers and following", "skip dead profiles"). Scope-first prefix optional (e.g., `scraper:`).
- PRs must include: purpose, key changes, run steps, and risks. Link issues. Add sample console output or CSV snippet when relevant.
- Keep diffs small and focused; update README/this guide if behavior or commands change.

## Security & Configuration Tips
- Secrets: never commit `.env`. Provide sample keys in docs only.
- Network use: Selenium + Requests access external sites; respect target ToS and rate limits.
- Grist: ensure `GRIST_API_KEY` and `GRIST_DOC_ID` are set; default server `https://docs.getgrist.com` is used in `main.py`.

## Architecture Overview
- Google search via Selenium yields Instagram profile URLs.
- Per-profile page parsed with BeautifulSoup; contact/follower data extracted.
- Results appended to CSV and optionally uploaded to Grist via REST API.
