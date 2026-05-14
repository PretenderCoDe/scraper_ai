# Playwright wiki scrape practice

Goal: practice Playwright (Node.js) by scraping a single page title, meta description, and table of contents.

## Learning steps

1. Install Node.js LTS.
2. Initialize the project with npm and install Playwright.
3. Learn Playwright basics: browser launch, page navigation, selectors, and waits.
4. Scrape the target page and print JSON output.
5. Add simple retries, timeouts, and a polite delay to avoid stressing the site.
6. Document ethical scraping habits and GDPR-aware behavior.

## Setup

From this folder:

```bash
npm install
npx playwright install
```

## Run the scraper

```bash
npm run scrape
```

Optional environment toggles:

- `HEADLESS=0` to show the browser
- `TIMEOUT_MS=45000` to increase timeouts
- `RETRIES=3` to retry more times
- `RATE_DELAY_MS=1500` to slow down

## Output

The script prints JSON with `pageTitle`, `pageDescription`, and `tableOfContents`.

## GDPR-friendly and ethical notes

- Scrape only public content and avoid personal data.
- Keep request volume low and avoid crawling.
- Check the site robots.txt and terms of use before automating.
- Store only the fields you need and avoid user data.

## Why `npm run scrape`

- `npm run scrape` or `node scraper.js`
- `npm run scrape` preset to run javascript file -> run `node scraper.js`