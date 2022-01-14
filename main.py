from bs4 import BeautifulSoup
import requests
import unicodedata # Used to normalize unicode and prevent errors from characters like &nbsp; (\xa0)
from datetime import datetime
from pytz import timezone

def main():
    scrape()

"""
Simple web scraper for Marianopolis College's admissions updates and calendars
Modified from my web scraper built for LHD: Build day 4
"""

def check_url(url):
    # Verify HTTP status codes returned by GET requests to URLs
    if requests.get(url).status_code != 200:
        with open("ERRORS.md", "w") as f:
            f.write(f"This link needs to be updated (moved or deleted): {url}\n")
        return 1
    else:
        return 0

def scrape():
    """
    Scrape admissions updates
    """
    # Grab HTML of the corresponding site
    url_adm = "https://www.bemarianopolis.ca/admissions/admissions-updates/"
    html_adm = requests.get(url_adm).text

    soup = BeautifulSoup(html_adm, "lxml") # Parse with LXML parser

    """
    The class list/selector used below is quite specific due to it being a WordPress site.
    Depending on the site structure after new updates are posted, may need to be modified.
    """
    update_section = soup.find("div", class_ = "x-section e4336-11 m3cg-0 m3cg-3 m3cg-4")

    # Search for paragraphs containing updates
    updates = update_section.find_all("p")

    """
    Scrape calendars (links)
    """
    # Grab HTML of the corresponding site
    url_cal = "https://www.marianopolis.edu/campus-life/calendar/"
    html_cal = requests.get(url_cal).text

    soup = BeautifulSoup(html_cal, "lxml") # Parse with LXML parser

    calendar_section = soup.find("article", class_ = "content") # The page being scraped here only links to calendars within the article.content tags with a few exceptions

    # Search for links in the content <article> (this should exclude any navbar and footer links)
    calendars = calendar_section.find_all("a")

    """
    Open README file and write if URL checks for both links pass
    """
    if (check_url(url_adm) == 0) and (check_url(url_cal) == 0):
        with open("README.md", "w") as f:
            # Write introduction and some headings
            f.write("## Marianopolis College updates\n\n")
            f.write("This runs on a web scraper built with Python and Beautiful Soup, which updates and writes to the README in this repo daily thanks to GitHub Actions automation.\n\n")
            f.write("### Admissions updates\n\n")

            # Write admissions updates
            for update in updates:
                update_text = unicodedata.normalize("NFKD", update.text)
                f.write(update_text + "\n\n")

            f.write("### Calendars\n\n")

            for calendar in calendars:
                calendar_url = calendar["href"] # Loop through each calendar link (anchor tag) and extract its href attribute (its URL)
                calendar_title = unicodedata.normalize("NFKD", calendar.text)  # Save the "title" of the calendar

                # Write calendar links (which all, hopefully, have the word "calendar" in their title at some point)
                if "calendar" in calendar_title.lower():
                    f.write(f"- {calendar_title}: {calendar_url}\n") # Use a string literal for users to more easily identify what calendar each link leads to

            # Retrieve and write (current) timestamp of the last scraper and URL check run
            timestamp = datetime.now(timezone('America/Toronto')) # Convert to EST timezone (Toronto is a commonly used standard timezone that matches our purposes)
            day = timestamp.strftime("%a %b. %d, %Y")
            time = timestamp.strftime("%H:%M")
            f.write("\n") # Write a newline before timestamp
            f.write(f"*Last updated on {day} at {time} (EST).*")

if __name__ == "__main__":
    main()
