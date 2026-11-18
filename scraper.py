# scraper.py
# Collects public page text from Wasalt and DarGlobal and saves it to data.json
# Run it with:  .venv/bin/python scraper.py
# A browser window will open. If a "verify you are human" box appears, click it.

import json
import time
from playwright.sync_api import sync_playwright

# ---- Pages to collect (public pages only) ----
WASALT_PAGES = [
    "https://wasalt.sa/en",
    "https://wasalt.sa/en/apartments-for-sale-in-riyadh",
    "https://wasalt.sa/en/apartments-for-rent-in-riyadh",
    "https://wasalt.sa/en/villas-for-sale-in-riyadh",
    "https://wasalt.sa/en/villas-for-rent-in-riyadh",
    "https://wasalt.sa/en/lands-for-sale-in-riyadh",
    "https://wasalt.sa/en/apartments-for-sale-in-jeddah",
    "https://wasalt.sa/en/apartments-for-rent-in-jeddah",
    "https://wasalt.sa/en/villas-for-sale-in-jeddah",
    "https://wasalt.sa/en/properties-for-sale-in-dammam",
    "https://wasalt.sa/en/properties-for-rent-in-dammam",
    "https://wasalt.sa/en/properties-for-sale-in-makkah",
    "https://wasalt.sa/en/properties-for-sale-in-madinah",
    "https://wasalt.sa/en/properties-for-sale-in-al-khobar",
]

DARGLOBAL_START = "https://www.darglobal.co.uk/en/projects"
MAX_DARGLOBAL_PAGES = 30

# Text that means "this is not a real page"
BAD_SIGNS = ["Performing security verification", "Just a moment", "This Page cannot be found"]


def is_bad(text):
    return len(text) < 300 or any(sign in text for sign in BAD_SIGNS)


def get_text(page, url):
    """Open a page and return its visible text.
    If a security check is shown, wait up to 60 seconds so you can click it."""
    page.goto(url, timeout=60000)
    page.wait_for_timeout(5000)
    text = page.inner_text("body").strip()
    waited = 0
    while "security verification" in text.lower() and waited < 60:
        if waited == 0:
            print("     -> Security check shown. Please click the box in the browser window.")
        page.wait_for_timeout(3000)
        waited += 3
        text = page.inner_text("body").strip()
    return text


def main():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # visible window
        page = browser.new_page()

        # 1) Wasalt - its Cloudflare check blocks automated browsers, so Wasalt pages
        #    are copied by hand instead (see add_manual_pages.py). Set to True to try anyway.
        SCRAPE_WASALT = False
        for url in (WASALT_PAGES if SCRAPE_WASALT else []):
            try:
                text = get_text(page, url)
                if is_bad(text):
                    print("SKIP", url, "(blocked or empty)")
                else:
                    results.append({"source": "Wasalt", "url": url, "text": text})
                    print("OK  ", url, len(text), "chars")
            except Exception as e:
                print("FAIL", url, e)
            time.sleep(2)  # be polite to the website

        # 2) DarGlobal: open the projects page, then visit the project links on it
        try:
            text = get_text(page, DARGLOBAL_START)
            links = page.eval_on_selector_all("a[href]", "els => els.map(a => a.href)")
            if not is_bad(text):
                results.append({"source": "DarGlobal", "url": DARGLOBAL_START, "text": text})
                print("OK  ", DARGLOBAL_START, len(text), "chars")
        except Exception as e:
            print("FAIL", DARGLOBAL_START, e)
            links = []

        project_links = []
        for link in links:
            link = link.split("#")[0].split("?")[0]
            if ("darglobal.co.uk" in link and link != DARGLOBAL_START
                    and "/ar/" not in link  # skip Arabic duplicates
                    and not link.endswith((".pdf", ".jpg", ".png"))
                    and link not in project_links):
                project_links.append(link)
        print(f"Found {len(links)} links, {len(project_links)} DarGlobal pages to visit")

        for url in project_links[:MAX_DARGLOBAL_PAGES]:
            try:
                text = get_text(page, url)
                if is_bad(text):
                    print("SKIP", url, "(blocked or 404)")
                else:
                    results.append({"source": "DarGlobal", "url": url, "text": text})
                    print("OK  ", url, len(text), "chars")
            except Exception as e:
                print("FAIL", url, e)
            time.sleep(2)

        browser.close()

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    wasalt = sum(1 for r in results if r["source"] == "Wasalt")
    print(f"\nSaved {len(results)} pages to data.json  (Wasalt: {wasalt}, DarGlobal: {len(results) - wasalt})")


if __name__ == "__main__":
    main()
