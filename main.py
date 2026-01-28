from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import re
import csv
import os
from bs4 import BeautifulSoup
import requests
from load_dotenv import load_dotenv

load_dotenv()
GRIST_API_KEY = os.getenv("GRIST_API_KEY")
GRIST_DOC_ID = os.getenv("GRIST_DOC_ID")


def get_instagram_links(driver, query, start_page, end_page):
    """Scrapes Google for Instagram profile links within a specified page range."""
    links = []
    for page in range(start_page, end_page + 1):
        # Construct the Google search URL for the specific page
        if page == 1:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}+site:instagram.com&num=100"
        else:
            start_index = (page - 1) * 10
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}+site:instagram.com&start={start_index}&num=100"

        driver.get(search_url)
        time.sleep(2)

        results = driver.find_elements(By.CSS_SELECTOR, "a[href*='instagram.com']")
        for result in results:
            href = result.get_attribute("href")
            if (
                href
                and "google.com" not in href
                and "#:~:text=" not in href
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
        website = ""

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

    unique_emails = list(set(emails))

    if unique_emails:
        if len(unique_emails) >= 2:
            print("Multiple emails found, joining them.")
            unique_emails = ", ".join(unique_emails)
        else:
            unique_emails = unique_emails[0]
    else:
        unique_emails = ""

    unique_phones = list(set(phones))
    if unique_phones:
        if len(unique_phones) >= 2:
            print("Multiple phones found, joining them.")
            unique_phones = ", ".join(unique_phones)
        else:
            unique_phones = unique_phones[0]
    else:
        unique_phones = ""

    return {
        "url": profile_url,
        "name": name,
        "website": website,
        "emails": unique_emails,
        "phones": unique_phones,
        "followers": followers,
        "following": following,
    }


def is_post_url(url):
    """Checks if a URL points to an Instagram post or reel."""
    return any(token in url for token in ("/p/", "/reel/", "/tv/"))


def is_profile_path(path):
    """Checks if a path looks like an Instagram profile path."""
    if not path or not path.startswith("/"):
        return False
    parts = path.strip("/").split("/")
    if len(parts) != 1:
        return False
    if parts[0] in {
        "explore",
        "p",
        "reel",
        "reels",
        "tv",
        "stories",
        "accounts",
        "about",
        "developer",
        "terms",
        "privacy",
    }:
        return False
    return True


def resolve_profile_url(driver, url):
    """Resolves post/reel URLs to their profile URLs."""
    if not is_post_url(url):
        return url

    driver.get(url)
    time.sleep(3)
    try:
        profile_el = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[2]/section/main/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div/span/div/div/span[1]/span/div/a/div/div/span",
        )
        profile_el.click()
        time.sleep(2)
        return driver.current_url
    except Exception:
        pass
    soup = BeautifulSoup(driver.page_source, "html.parser")

    profile_url = None
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        match = re.match(
            r"^([A-Za-z0-9._]+)\s+on Instagram", og_title["content"].strip()
        )
        if match:
            profile_url = f"https://www.instagram.com/{match.group(1)}/"

    if not profile_url:
        header = soup.find("header")
        if header:
            for anchor in header.find_all("a", href=True):
                href = anchor["href"]
                if is_profile_path(href):
                    profile_url = f"https://www.instagram.com{href}"
                    break

    if not profile_url:
        match = re.search(
            r"https://www\.instagram\.com/([A-Za-z0-9._]+)/", driver.page_source
        )
        if match:
            profile_url = f"https://www.instagram.com/{match.group(1)}/"

    if not profile_url:
        return None

    driver.get(profile_url)
    time.sleep(2)
    return driver.current_url or profile_url


def upload_to_grist(api_key, server, doc_id, table_name, data):
    """Uploads data to a Grist database using REST API."""
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        # List tables to check if the table exists
        list_tables_url = f"{server}/api/docs/{doc_id}/tables"
        response = requests.get(list_tables_url, headers=headers)
        response.raise_for_status()
        tables = response.json()["tables"]
        # Capitalize the first letter of the table name
        table_name = table_name.capitalize()

        if table_name not in [t["id"] for t in tables]:
            print(f"Table '{table_name}' not found in Grist document. Creating it...")
            create_table_url = f"{server}/api/docs/{doc_id}/tables"
            columns = [{"id": key} for key in data[0].keys()]
            payload = {"tables": [{"id": table_name, "columns": columns}]}
            response = requests.post(create_table_url, headers=headers, json=payload)
            response.raise_for_status()
            print(f"Table '{table_name}' created successfully.")

        # Prepare records for upload
        records_to_upload = [{"fields": item} for item in data]
        add_records_url = f"{server}/api/docs/{doc_id}/tables/{table_name}/records"
        response = requests.post(
            add_records_url, headers=headers, json={"records": records_to_upload}
        )
        response.raise_for_status()

        print(f"Successfully uploaded {len(data)} records to Grist.")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while communicating with Grist: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during Grist upload: {e}")


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)

    query = input("Enter your search query (e.g., 'real estate agents in new york'): ")
    start_page = int(input("Enter the starting page number: "))
    end_page = int(input("Enter the ending page number: "))

    insta_links = get_instagram_links(driver, query, start_page, end_page)
    insta_links = sorted(list(set(insta_links)))

    print(f"Found {len(insta_links)} Instagram links.")

    resolved_links = []
    seen_profiles = set()
    for link in insta_links:
        profile_url = resolve_profile_url(driver, link)
        if not profile_url:
            print(f"Skipping {link} (could not resolve profile).")
            continue
        if profile_url not in seen_profiles:
            resolved_links.append(profile_url)
            seen_profiles.add(profile_url)

    print(f"Resolved {len(resolved_links)} unique profile links.")
    print("\n--- Profiles to be Scraped ---")
    for link in resolved_links:
        print(link)
    print("---------------------------\n")

    all_leads = []
    for link in resolved_links:
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
                print(f"  Emails: {lead_data['emails']}")
                print(f"  Phones: {lead_data['phones']}")
            except TypeError as e:
                print(f"  Error processing data for this profile: {e}")
            except Exception as e:
                print(f"  An unexpected error occurred: {e}")
        else:
            print("  Skipping profile due to missing name, followers, or following.")
        print("-" * 20)

    # Save to CSV
    if all_leads:
        output_dir = "scraped_data"
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"{query.replace(' ', '_')}.csv")
        file_exists = os.path.isfile(filename)

        with open(filename, "a", newline="", encoding="utf-8") as csvfile:
            fieldnames = all_leads[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerows(all_leads)
        print(f"\nSuccessfully saved {len(all_leads)} leads to {filename}")

    # Upload to Grist
    # upload_grist = input("\nUpload to Grist? (y/n): ").lower()
    # if upload_grist == "y":
    grist_server = "https://docs.getgrist.com"
    grist_table_name = query.replace(" ", "_")
    upload_to_grist(
        GRIST_API_KEY, grist_server, GRIST_DOC_ID, grist_table_name, all_leads
    )

    # The browser is not closed, as it's a shared session.
