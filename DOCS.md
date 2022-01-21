# About `mari-updates`

Thanks for visiting my `mari-updates` repo! If you're wondering how it works and why it was created, you're in the right place. If you'd like to run or test the web scraper on your local machine, skip to [Running the scraper locally](#running-the-scraper-locally).

*To see the self-updating README with the scraped updates, please go to [README.md](README.md).*

## Web scraper

The most central "piece" of code in this repo is the web scraper component — this is written in Python and uses the Beautiful Soup and `requests` libraries to scrape content from two sites. The Python script that does all this is `main.py` — there are also comments alongside the code that explain the role of certain lines and parts of the code, so do take a look at the file to see exactly how everything was programmed.

The `scrape()` function contains the code that scrapes the sites, and does the following:

- Sends a `GET` request to each of the two websites
- If the request(s) result(s) in `200 OK` HTTP codes, the script fetches the text content of the specified URL (link)
  - `requests.get(<url>).status_code` returns the HTTP status code returned by a `GET` request
  - *A "fallback" was implemented in case the resulting HTTP code is **not** the expected `200`. See [Troubleshooting](#troubleshooting) for more information.*
- The BeautifulSoup library is used to parse the text content as LXML:
  - For the admissions updates section of the scraper, the program searches for the `<div>` with the classes `x-section e4336-11 m3cg-0 m3cg-3 m3cg-4`, which contains all updates posted by the admissions teams (and that's what we want!)
  - For the calendar links section, the program searches inside an `<article>` tag (where the calendar links tend to be included) for links, or anchor tags `<a>`, containing the word "calendar" (case-insensitive)
- The desired site content scraped from above is then written to `README.md` every time the scraper script is run
  - The `datetime` and `pytz` Python modules are used to retrieve and update the time of the latest scraper/workflow run, written at the very end of `README.md`. `datetime` retrieves the current time, then the `timezone` function from `pytz` converts it to Eastern Standard Time, and finally the `strftime` function formats the timestamp as *"Last updated on {weekday} {month}. {day}, {year} at {time AM/PM} (EST)"* — you'll find this timestamp the bottom of the [README](README.md).
  - **See [Self-updating workflow](#self-updating-workflow) to see how the script executes through automation).**

### Self-updating workflow

This part of the repo is just as important, because it's an Actions workflow that's automating the process of running the scraper program, and thus updating the README once a day. *("Actions workflow" is referring to a [GitHub Actions workflow](https://docs.github.com/en/actions). It's an incredibly useful and powerful feature of GitHub that can help programmers automate, test, and deploy programs right from their repositories.)*

The workflow responsible for running the scraper is named "Web Scrape", and can be found in the `scrape.yml` file of this repo (the file path is `.github/workflows/scrape.yml`). It uses several Actions and steps:

- The [Checkout V2](https://github.com/actions/checkout) action (*"Checkout repo content"*): check-out the `mari-updates` repo to allow the workflow to access it
- The [setup-python V2](https://github.com/actions/setup-python) action (*"Setup Python"*): setup Python version `3.10.0`, which will be used to run the scraper script (`main.py`)
- The "Install requirements" step: install requirements, which are listed in the `requirements.txt` file of the repo, with the `pip` Python package installer
- The "Execute scraper script" step: run/interpret the `main.py` Python web scraping script
- The [Add & Commit](https://github.com/EndBug/add-and-commit) action (*"Commit updates (scrape results)"*): commit changes made in previous steps of this workflow directly to the repo, sets me as the commit author and GitHub Actions as the committer

The entire workflow runs on a `schedule` thanks to this `cron` syntax: `"30 3 * * *"`. This causes the workflow to run at 03:30 AM (UTC) every day, thereby scraping the sites and updating the README accordingly.

### Troubleshooting

A fallback option was implemented in case any errors arose with making a request to either of the websites, or with parsing the code/text. 

While testing the scraper program locally, an error was discovered where the program is unable to parse code or write text to the README if certain unicode characters like the no-breaking space (`U+00A0`) are present. The solution was to normalize the text using the built-in `unicodedata` Python module, which in turn removes any problematic unicode characters to prevent such errors.

An important issue is that websites tend to evolve and change, including URL paths, so it's best if web scrapers have fallbacks in preparation to handle these situations. This is where the `checkurl()` function comes in: if it discovers that the HTTP status code returned by a `request` isn't `200 OK`, it'll write the problematic URL to the `ERRORS.md` file and return `1`. In the `scrape()` function, if `checkurl()` doesn't return a value of `0`, which essentially means "all good" for the links, then it won't write anything to the README. This was done to preserve the last scraped version of the text, even if it may be out-of-date, rather than injecting Python code errors or just failing the entire Actions workflow.

## Running the scraper locally

You can also clone this repo, or at the very least `main.py` and `requirements.txt` *(to avoid errors, you may want to create/download `ERRORS.md` as well if you preserve the code that writes to this file)*, to your computer to run/test locally. If you'd like to use or try all of the implemented functionality of this scraper, it's recommended that you simply clone the repository.

1. To clone `mari-updates`, first fork this repo by clicking the "Fork" button on the GitHub interface. This will create a copy of `mari-updates` in your own account, giving you full permissions and control over the forked version.

2. Clone your fork of this repo to your local machine. Navigate to the directory (folder) where you'd like to "place" your files (you'll likely need the `cd` command for this), then you can use the following `Git` command **(replace `<username>` with your GitHub username!)**: `git clone https://github.com/<username>/mari-updates.git`.

3. Ensure that you're in the same directory (folder) as your `main.py` file of this scraper. Open your terminal, then type `pip install -r requirements.txt` to install all necessary Python libraries and modules used in the program.

4. To run the scraper, simply type `python main.py` to run the Python script. Results should be written to `README.md` or `ERRORS.md`, depending on the status code(s) returned by the websites.

And that's it!
