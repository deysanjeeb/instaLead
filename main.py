from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import re

def get_instagram_links(driver, query, num_pages):
    """Scrapes Google for Instagram profile links."""
    driver.get("https://www.google.com")
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query + " site:instagram.com")
    search_box.send_keys(Keys.RETURN)

    links = []
    for page in range(num_pages):
        time.sleep(2)
        results = driver.find_elements(By.CSS_SELECTOR, "a[href*='instagram.com']")
        for result in results:
            href = result.get_attribute("href")
            if href and "google.com" not in href:
                links.append(href)
        try:
            next_button = driver.find_element(By.ID, "pnnext")
            next_button.click()
        except:
            break
    return links

from bs4 import BeautifulSoup

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
    phone_pattern = r"(?:\+?\d{1,4}?[-.\s]?)?(?:\(?\d{1,3}?\)?[-.\s]?)?[\d\s-]{7,}"
    
    emails = re.findall(email_pattern, page_text)
    phones = re.findall(phone_pattern, page_text)

    return {
        "url": profile_url,
        "name": name,
        "website": website,
        "emails": list(set(emails)),
        "phones": list(set(phones))
    }

if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)

    query = input("Enter your search query (e.g., 'real estate agents in new york'): ")
    num_pages = int(input("Enter the number of Google pages to scrape: "))

    insta_links = get_instagram_links(driver, query, num_pages)
    
    print(f"Found {len(insta_links)} Instagram profiles.")

    print("\n--- Links to be Scraped ---")
    for link in insta_links:
        print(link)
    print("---------------------------\n")

    all_leads = []
    for link in insta_links:
        print(f"Scraping {link}...")
        lead_data = get_profile_info(driver, link)
        all_leads.append(lead_data)
        try:
            print(f"  Name: {lead_data['name']}")
            print(f"  Website: {lead_data['website']}")
            print(f"  Emails: {', '.join(lead_data['emails'])}")
            print(f"  Phones: {', '.join(lead_data['phones'])}")
        except TypeError as e:
            print(f"  Error processing data for this profile: {e}")
        except Exception as e:
            print(f"  An unexpected error occurred: {e}")
        print("-" * 20)

    # The browser is not closed, as it's a shared session.
