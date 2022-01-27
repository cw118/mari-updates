from bs4 import BeautifulSoup
import requests
import unicodedata # Used to normalize unicode and prevent errors from characters like &nbsp; (\xa0)
from datetime import datetime
from pytz import timezone

def main():
    scrape()

"""
Simple web scraper for Marianopolis College's admissions updates, calendars and events
Modified from my web scraper built for LHD: Build day 4 (see my lhd_build repo)
"""

def check_url(url):
    # Verify HTTP status codes returned by GET requests to URLs
    if requests.get(url).status_code != 200:
        with open("ERRORS.md", "w") as f:
            # Write problematic links that don't return a 200 OK status to the ERRORS.md file
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
    Depending on the site structure after new updates are posted, this may need to be modified.
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
    Scrape admissions articles published in 2022 (title, date published, summary, link to article/event)
    """
    # Grab HTML of the corresponding site section
    url_articles = "https://www.bemarianopolis.ca/category/admissions/"
    html_articles = requests.get(url_articles).text

    soup = BeautifulSoup(html_articles, "lxml") # Also parse with LXML parser

    # Find all <article> elements, each of which have the link to an article,
    # The title, publish date, and a preview snippet/excerpt
    articles = soup.find_all("article", class_ = "type-post")

    """
    Open README file and write if URL checks for all links pass
    """
    if (check_url(url_adm) == 0) and (check_url(url_cal) == 0):
        with open("README.md", "w") as f:
            # Write introduction and some headings
            f.write("## Marianopolis College updates\n\n")
            f.write("This runs on a web scraper built with Python and Beautiful Soup, which updates and writes to the README in this repo twice daily thanks to GitHub Actions automation.\n\n")
            f.write("*Refer to [DOCS.md](DOCS.md) for this repository's documentation.*\n\n")
            f.write("### [Admissions updates](https://www.bemarianopolis.ca/admissions/admissions-updates/)\n\n")

            # Write admissions updates
            for update in updates:
                update_text = unicodedata.normalize("NFKD", update.text.replace("\u2019", "'"))
                f.write(update_text + "\n\n")

            f.write("### [Calendars](https://www.marianopolis.edu/campus-life/calendar/)\n\n")

            for calendar in calendars:
                calendar_url = calendar["href"] # Loop through each calendar link (anchor tag) and extract its href attribute (its URL)
                calendar_title = unicodedata.normalize("NFKD", calendar.text.replace("\u2019", "'"))  # Save the "title" of the calendar

                # Write calendar links (which all, hopefully, have the word "calendar" in their title at some point)
                if "calendar" in calendar_title.lower():
                    f.write(f"- {calendar_title}: {calendar_url}\n") # Use a string literal for users to more easily identify what calendar each link leads to

            # Write current year's admissions articles
            f.write("\n### [Admission articles](https://www.bemarianopolis.ca/category/admissions/)\n\n")
            # Prepare table (head and separator)
            f.write("| Article | Publish Date | Excerpt |\n")
            f.write("| ------- | ------------ | ------- |\n")

            for article in articles:
                if "2022" in (article.select_one("p.p-meta > span > time.entry-date").text):
                    article_title = unicodedata.normalize("NFKD", article.find("h2", class_ = "entry-title").text.replace("\u2019", "'").strip("\n")) # Get entry title
                    article_excerpt = article.find("div", class_ = "entry-content excerpt") # Get excerpt div (contains links and snippets/summaries)

                    article_pubdate = unicodedata.normalize("NFKD", article.select_one("p.p-meta > span > time.entry-date").text.replace("\u2019", "'")) # Get publish date in text form
                    article_link = article_excerpt.find("a")["href"].strip("\n") # Get article link (scraped from the "Read More" link button in the excerpt divs)
                    article_snippet = unicodedata.normalize("NFKD", article_excerpt.find("p").text.replace("\u2019", "'")) # Get snippets/summaries of the articles


                    # Write article data to table row (Markdown)
                    f.write(f"| [{article_title}]({article_link}) | {article_pubdate} | {article_snippet} |\n")

            # Retrieve and write (current) timestamp of the last scraper and URL check run
            timestamp = datetime.now(timezone('America/Toronto')) # Convert to EST timezone (Toronto is a commonly used standard timezone that matches our purposes)
            day = timestamp.strftime("%a %b. %d, %Y")
            time = timestamp.strftime("%H:%M %p")
            f.write("\n") # Write a newline before timestamp
            f.write(f"*Last updated on {day} at {time} (EST).*")

if __name__ == "__main__":
    main()
