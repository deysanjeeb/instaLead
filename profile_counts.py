"""Simple helper to report follower/following counts for a single Instagram profile.

Launch Chrome with remote debugging enabled before running, e.g.:
    google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/selenium
"""

import argparse
import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def parse_count(count_str: str):
    """Parse abbreviated follower/following counts like 10.5k or 1.2m."""
    count_str = count_str.lower().replace(",", "")
    if "k" in count_str:
        return int(float(count_str.replace("k", "")) * 1000)
    if "m" in count_str:
        return int(float(count_str.replace("m", "")) * 1_000_000)
    if count_str.isdigit():
        return int(count_str)
    return count_str


def get_profile_info(driver: webdriver.Chrome, profile_url: str):
    """Extract limited profile info directly (followers/following)."""
    driver.get(profile_url)
    time.sleep(5)  # allow dynamic content to load

    soup = BeautifulSoup(driver.page_source, "html.parser")

    followers = "Not found"
    following = "Not found"

    try:
        followers_link = soup.find("a", href=lambda href: href and "followers" in href)
        if followers_link:
            followers_span = followers_link.find("span", {"class": "x5n08af"})
            if followers_span:
                followers = parse_count(followers_span.get("title", ""))

        following_link = soup.find("a", href=lambda href: href and "following" in href)
        if following_link:
            following_span = following_link.find("span", {"class": "x5n08af"})
            if following_span:
                following = parse_count(following_span.get_text(strip=True))
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Error parsing followers/following: {exc}")

    return {"followers": followers, "following": following}


def build_driver(debugger_address: str) -> webdriver.Chrome:
    """Attach Selenium to an existing Chrome instance."""
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", debugger_address)
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Retrieve follower/following counts for a single Instagram account."
    )
    parser.add_argument("url", help="Full Instagram profile URL to inspect.")
    parser.add_argument(
        "--debugger-address",
        default="127.0.0.1:9222",
        help="Chrome debugger address (default: %(default)s).",
    )
    args = parser.parse_args()

    driver = build_driver(args.debugger_address)
    try:
        profile_info = get_profile_info(driver, args.url)
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    followers = profile_info.get("followers", "Not found")
    following = profile_info.get("following", "Not found")

    print(f"Followers: {followers}")
    print(f"Following: {following}")
    if "Not found" in (followers, following):
        print(
            "One or both counts were not found. Ensure the profile is public and fully loaded."
        )


if __name__ == "__main__":
    main()
