# InstaLead

Lead discovery via Google search → Instagram profile parsing, exporting to CSV and optionally uploading to Grist.

## Requirements
- Python 3.12+
- Google Chrome installed
- ChromeDriver managed by Selenium (bundled in Selenium 4 typically) and a Chrome instance running with remote debugging on port 9222

## Setup
1) Create and activate a virtual environment
   - `python3 -m venv venv && source venv/bin/activate`
2) Install dependencies
   - `pip install -r requirements.txt`
   - Or using uv: `uv sync`
3) Configure environment (optional but recommended for Grist upload)
   - Create a `.env` file in the project root:
     - `GRIST_API_KEY=...`
     - `GRIST_DOC_ID=...`

## Start Chrome for Selenium
Run Chrome with remote debugging (keep this window open while scraping):
- Linux: `google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/selenium`
- macOS: `/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/selenium`
- Windows (PowerShell): `"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\\selenium`

## Usage
Run the scraper and follow prompts for query and page range:
- `python main.py`

The script will:
- Search Google for Instagram profiles, filter links, and parse each profile.
- Extract name, website, followers, following, emails, and phones.
- Write results to a CSV named after your query (e.g., `real_estate_agents_in_san_diego.csv`).
- Attempt to upload results to Grist if `GRIST_API_KEY` and `GRIST_DOC_ID` are provided.

Notes
- CSV files and `.env` are git-ignored by default.
- Respect Google/Instagram Terms of Service and rate limits.

## Contributing
See `AGENTS.md` for project structure, coding style, testing, and PR guidelines.
