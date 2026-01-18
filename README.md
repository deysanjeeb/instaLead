# InstaLead

Discover Instagram leads by searching Google, parsing profile pages, exporting to CSV, and optionally uploading to Grist.

## What it does
- Searches Google for Instagram profile URLs based on your query.
- Scrapes each profile for name, website, followers, following, emails, and phones.
- Appends results to a CSV in the repo root.
- Uploads rows to Grist when credentials are available.

## Requirements
- Python 3.12+
- Google Chrome installed
- Chrome running with remote debugging enabled on port 9222

## Setup
1) Create and activate a virtual environment
   - `python3 -m venv venv && source venv/bin/activate`
2) Install dependencies
   - `pip install -r requirements.txt`
   - Or: `uv sync`
3) (Optional) Configure Grist
   - Create `.env` in the project root:
     - `GRIST_API_KEY=...`
     - `GRIST_DOC_ID=...`

## Start Chrome for Selenium
Run Chrome with remote debugging and keep it open while scraping:
- Linux: `google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/selenium`
- macOS: `/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/selenium`
- Windows (PowerShell): `"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\\selenium`

## Run
- `python main.py`

Follow the prompts for your query and page range. Output is written to a CSV named after the query, for example `real_estate_agents_in_san_diego.csv`.

## Output
- CSV files are written to the repo root.
- `.env` and CSVs are git-ignored by default.

## Notes
- Respect Google/Instagram terms of service and rate limits.
- Grist uploads use `https://docs.getgrist.com` by default.

## Project guide
See `AGENTS.md` for project structure, coding style, and testing guidance.
