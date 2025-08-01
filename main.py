from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import re
import csv
from bs4 import BeautifulSoup


def get_instagram_links(driver, query, start_page, end_page):
    """Scrapes Google for Instagram profile links within a specified page range."""
    links = []
    for page in range(start_page, end_page + 1):
        # Construct the Google search URL for the specific page
        if page == 1:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}+site:instagram.com"
        else:
            start_index = (page - 1) * 10
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}+site:instagram.com&start={start_index}"

        driver.get(search_url)
        time.sleep(2)

        results = driver.find_elements(By.CSS_SELECTOR, "a[href*='instagram.com']")
        for result in results:
            href = result.get_attribute("href")
            if (
                href
                and "google.com" not in href
                and ".com/p/" not in href
                and ".com/reel/" not in href
            ):
                links.append(href)

    return links


def parse_count(count_str):
    """Parses abbreviated follower/following counts (e.g., 10.5k, 1.2m)."""
    count_str = count_str.lower().replace(",", "")
    if "k" in count_str:
        return int(float(count_str.replace("k", "")) * 1000)
    if "m" in count_str:
        return int(float(count_str.replace("m", "")) * 1000000)
    if count_str.isdigit():
        return int(count_str)
    return count_str  # Return original string if not a recognized format


def get_profile_info(driver, profile_url):
    """Extracts information from an Instagram profile using Selenium and BeautifulSoup."""
    driver.get(profile_url)
    time.sleep(5)  # Allow time for dynamic content to load

    soup = BeautifulSoup(driver.page_source, "html.parser")

    try:
        # Instagram's structure for the name can vary, we'll try a common selector
        name = soup.find("h2").get_text()
    except:
        name = "Not found"

    try:
        # The website is often a link with a 'rel' attribute containing 'me'
        website = soup.find("a", rel=lambda r: r and "me" in r).get_text()
    except:
        website = "Not found"

    # Regex to find emails and phone numbers in the page text
    page_text = soup.get_text()
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_pattern = r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}"

    emails = re.findall(email_pattern, page_text)

    # Find potential phone numbers and filter for 10-digit numbers
    potential_phones = re.findall(phone_pattern, page_text)
    phones = [
        phone for phone in potential_phones if len(re.sub(r"\D", "", phone)) == 10
    ]

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

    except Exception as e:
        print(f"Error parsing followers/following: {e}")
        pass

    return {
        "url": profile_url,
        "name": name,
        "website": website,
        "emails": list(set(emails)),
        "phones": list(set(phones)),
        "followers": followers,
        "following": following,
    }


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)

    query = input("Enter your search query (e.g., 'real estate agents in new york'): ")
    start_page = int(input("Enter the starting page number: "))
    end_page = int(input("Enter the ending page number: "))

    insta_links = get_instagram_links(driver, query, start_page, end_page)
    insta_links = sorted(list(set(insta_links)))

    print(f"Found {len(insta_links)} Instagram profiles.")

    print("\n--- Links to be Scraped ---")
    for link in insta_links:
        print(link)
    print("---------------------------\n")

    all_leads = []
    for link in insta_links:
        print(f"Scraping {link}...")
        lead_data = get_profile_info(driver, link)
        if (
            lead_data["name"] != "Not found"
            and lead_data["followers"] != "Not found"
            and lead_data["following"] != "Not found"
        ):
            all_leads.append(lead_data)
            try:
                print(f"  Name: {lead_data['name']}")
                print(f"  Website: {lead_data['website']}")
                print(f"  Followers: {lead_data['followers']}")
                print(f"  Following: {lead_data['following']}")
                print(f"  Emails: {', '.join(lead_data['emails'])}")
                print(f"  Phones: {', '.join(lead_data['phones'])}")
            except TypeError as e:
                print(f"  Error processing data for this profile: {e}")
            except Exception as e:
                print(f"  An unexpected error occurred: {e}")
        else:
            print("  Skipping profile due to missing name, followers, or following.")
        print("-" * 20)

    # Save to CSV
    if all_leads:
        filename = query.replace(" ", "_") + ".csv"
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = all_leads[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_leads)
        print(f"\nSuccessfully saved {len(all_leads)} leads to {filename}")

    # The browser is not closed, as it's a shared session.
