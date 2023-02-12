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

def normalize(text):
    # Replace smart quotes/apostrophes and normalize unicode 
    # (unicodedata hasn't been replacing smart quotes or EN/EM dashes, so it's being done separately)
    normalized = unicodedata.normalize("NFKD", text.replace("\u2019", "'").replace("\u2013", "-").replace("\u2014", "-"))
    return normalized

def scrape():
    year = datetime.today().year

    """
    Scrape admissions updates
    """
    # Grab HTML of the corresponding site
    url_adm = "https://www.bemarianopolis.ca/admissions/updates/"
    html_adm = requests.get(url_adm).text

    soup = BeautifulSoup(html_adm, "lxml") # Parse with LXML parser

    """
    The class list/selector used below is quite specific due to it being a WordPress site.
    Depending on the site structure after new updates are posted, this may need to be modified.
    """
    update_section = soup.find("div", class_ = "x-section e4336-e11 m3cg-0 m3cg-4")

    # Search for paragraphs containing updates
    updates = update_section.children

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
    with open("README.md", "w", encoding='utf-8') as f:
        # Set horizontal rule Markdown syntax to variable to print/write after each section
        hr = "---\n\n"

        # Write introduction, Web Scrape workflow badge and some headings
        f.write(f"# Marianopolis College updates {year}\n\n")
        f.write("[![Web Scrape](https://github.com/cw118/mari-updates/actions/workflows/scrape.yml/badge.svg)](https://github.com/cw118/mari-updates/actions/workflows/scrape.yml)\n\n")
        f.write("This runs on a web scraper built with Python and Beautiful Soup, which updates and writes to the README in this repo once a day thanks to GitHub Actions automation.\n\n")
        f.write("*Refer to [DOCS.md](DOCS.md) for this repository's documentation.*\n\n" + hr) # hr = horizontal rule

        # Write admissions updates, iterating over and checking all children of the section <div>
        f.write("## [Admissions updates](https://www.bemarianopolis.ca/admissions/admissions-updates/)\n\n")

        # Iterate over all children of the update section <div>
        for update in updates:         
            # Write as <h3> if text is wrapped in <h5> tags (the update "title")
            # All spans used seem to have `style="text-decoration: underline;"`, meaning they should be emphasized
            if update.find("h5"):
                # Ensure there's more than a newline to avoid injecting empty formatting tags
                # If the text content contains more than a newline, make it a level 3 heading
                if update.text != "\n":
                    update_text = normalize(update.text).strip()
                    f.write(f"### {update_text}\n\n")
            else:
                update_text = normalize(update.text).strip()
                f.write(f"\n{update_text}\n\n")
        # Suggest source link/page to readers as the scraper doesn't preserve rich text/hyperlinks
        f.write("***\*\*Visit the [Marianopolis College website](https://www.bemarianopolis.ca/admissions/updates/) for details.***\n\n" + hr)

        # Write calendar names and their corresponding links
        f.write("## [Calendars](https://www.marianopolis.edu/campus-life/calendar/)\n\n")
        f.write("Looking for Marianopolis' course and academic calendars? See the list below for past and current published calendars:\n\n")

        for calendar in calendars:
            calendar_url = calendar["href"] # Loop through each calendar link (anchor tag) and extract its href attribute (its URL)
            calendar_title = normalize(calendar.text)  # Save the "title" of the calendar

            # Write calendar links (which all, hopefully, have the word "calendar" in their title at some point)
            if "calendar" in calendar_title.lower():
                f.write(f"- *{calendar_title}:* <{calendar_url}>\n") # Use a string literal for users to more easily identify what calendar each link leads to
        f.write("\n" + hr) # Newline and horizontal rule in between two sections

        # Write current year's admissions articles
        f.write("## [Admission articles](https://www.bemarianopolis.ca/category/admissions/)\n\n")
        f.write("Recent articles published by the Marianopolis staff and recruitment team. Click on the title(s) to read the full text:\n\n")
        # Prepare table (head and separator)
        f.write("| Article | Publish Date | Excerpt |\n")
        f.write("| ------- | ------------ | ------- |\n")

        # For loop with if condition that only retrieves information of articles published in current year
        for article in articles:
            if str(year) in (article.select_one("p.p-meta > span > time.entry-date").text):
                # Get entry title (the .strip removes newlines, tabs and returns to prevent Markdown rendering errors)
                article_title = normalize(article.find("h2", class_ = "entry-title").text).strip()
                article_excerpt = article.find("div", class_ = "entry-content excerpt") # Get excerpt div (contains links and snippets/summaries)

                article_pubdate = normalize(article.select_one("p.p-meta > span > time.entry-date").text) # Get publish date in text form
                article_link = article.find("h2", class_ = "entry-title").find("a")["href"].strip() # Get article link from article title
                article_snippet = normalize(article_excerpt.find("p").text) # Get snippets/summaries of the articles

                # Write article data to table row (Markdown)
                f.write(f"| [{article_title}]({article_link}) |{article_pubdate} | {article_snippet}|\n")

        # Retrieve and write (current) timestamp of the last scraper and URL check run
        timestamp = datetime.now(timezone('America/Toronto')) # Convert to EST timezone (Toronto is a commonly used standard timezone that matches our purposes)
        day = timestamp.strftime("%a %b. %d, %Y")
        time = timestamp.strftime("%H:%M %p")
        # Write horizontal rule before timestamp
        f.write("\n" + hr)
        f.write(f"*Last updated on {day} at {time} (EST).*\n")

if __name__ == "__main__":
    main()
