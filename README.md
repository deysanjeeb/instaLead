# InstaLead

Automated Instagram lead generation tool that discovers profiles through Google search, extracts contact information, and exports data to CSV or Grist.

## Features

- **Google Search Integration**: Search Instagram profiles using custom queries with configurable page ranges
- **Profile Data Extraction**: Name, website, emails, phone numbers, follower/following counts
- **URL Resolution**: Converts Instagram post/reel URLs to profile URLs automatically
- **CSV Export**: Saves data to organized CSV files with append mode
- **Grist Integration**: Upload data directly to Grist documents via REST API
- **Duplicate Prevention**: Deduplicates profiles and contact information

## Requirements

- Python 3.12+
- Google Chrome installed
- Chrome running with remote debugging enabled on port 9222

## Setup

1. Create and activate a virtual environment

```bash
python3 -m venv venv && source venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
# Or using uv:
uv sync
```

3. Configure Grist (optional but recommended)

Create a `.env` file in the project root:

```env
GRIST_API_KEY=your_api_key_here
GRIST_DOC_ID=your_document_id_here
```

## Start Chrome for Selenium

Run Chrome with remote debugging and keep it open while scraping:

**Linux:**
```bash
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/selenium
```

**macOS:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/selenium
```

**Windows:**

**Command Prompt (cmd):**
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\selenium
```

**PowerShell:**
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\selenium
```

**Desktop Shortcut:**
1. Right-click desktop → New → Shortcut
2. Location: `"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\selenium`
3. Name it "Chrome Remote Debugging" and double-click to launch

### Verify Remote Debugging is Working

After starting Chrome, open http://localhost9222/json in a browser tab. You should see a JSON response with browser information.

## Usage

Run the main script:

```bash
python main.py
```

Follow the prompts:
1. Enter your search query (e.g., "real estate agents in San Francisco")
2. Enter the starting page number
3. Enter the ending page number

The script will:
- Search Google for Instagram profiles
- Resolve post/reel URLs to profile URLs
- Scrape each profile for contact information
- Save results to CSV
- Upload to Grist (if configured)

## Output

CSV files are saved in the `scraped_data/` directory, named after your search query:
- Example: `scraped_data/real_estate_agents_in_san_francisco.csv`

### CSV Structure

| Field | Description | Example |
|-------|-------------|---------|
| url | Instagram profile URL | https://www.instagram.com/johndoe/ |
| name | Profile display name | John Doe |
| website | Website URL | https://johndoe.com |
| emails | Comma-separated emails | john@example.com |
| phones | Comma-separated phones | 5551234567 |
| followers | Follower count | 10500 |
| following | Following count | 250 |

## Example Output

```
Found 45 Instagram links.
Resolved 38 unique profile links.

--- Profiles to be Scraped ---
https://www.instagram.com/johndoe/
https://www.instagram.com/janesmith/
https://www.instagram.com/realtorbob/
...

Scraping https://www.instagram.com/johndoe/...
  Name: John Doe
  Website: https://johndoe.com
  Followers: 10500
  Following: 250
  Emails: john@example.com
  Phones: 5551234567
--------------------

Successfully saved 38 leads to scraped_data/real_estate_agents_in_san_francisco.csv
Successfully uploaded 38 records to Grist.
```

## Project Structure

```
instaLead/
├── main.py              # Main entry point
├── profile_counts.py    # Helper script for profile metrics
├── requirements.txt      # Python dependencies
├── pyproject.toml       # Project metadata
├── .env                 # Grist credentials (not in git)
├── scraped_data/        # CSV output directory
├── PRD.md              # Product Requirements Document
├── AGENTS.md           # Developer guidelines
└── README.md           # This file
```

## Troubleshooting

**Chrome connection fails**
- Ensure Chrome is running with remote debugging on port 9222
- Check that no other Chrome instances are using that port

**Windows-specific issues:**

*"Chrome is already running" error*
- Close all Chrome instances using Task Manager (End task for chrome.exe)
- Then start Chrome with remote debugging again

*Port 9222 already in use*
- Change to a different port: `--remote-debugging-port=9223`
- Update `main.py` line 262: `chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9223")`

*Permission issues with user-data-dir*
- Use a different directory: `--user-data-dir=%TEMP%\selenium`
- Create the directory manually: `mkdir C:\selenium` (run as Administrator if needed)
- Firewall prompts may appear - click "Allow" to enable network access

**Missing profile data**
- Only public profiles can be scraped
- Some profiles may have restricted follower counts
- Check if Instagram has changed their HTML structure

**Grist upload fails**
- Verify your `.env` file contains valid API key and document ID
- Ensure you have write permissions for the target document

## Notes

- **Terms of Service**: Respect Google and Instagram's terms of service and rate limits
- **Data Quality**: Email/phone extraction uses regex patterns and may include false positives
- **Performance**: Typical scrape time is 3-5 seconds per profile
- **Security**: Never commit `.env` or CSV files to version control

## Additional Scripts

**profile_counts.py**: Quick lookup for follower/following counts of a single profile

```bash
python profile_counts.py https://www.instagram.com/username/
```

## Documentation

- **PRD.md**: Comprehensive product requirements document
- **AGENTS.md**: Development guidelines, coding standards, and testing instructions

## License

This project is provided as-is for educational and research purposes.
