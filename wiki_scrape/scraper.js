import { chromium } from "playwright";

/*
  Simple Playwright scraper (beginner-friendly)

  Purpose: load a single public wiki page and extract three pieces of information:
  - page title (the visible H1)
  - meta description (from <meta> tags)
  - table of contents entries

  Run: from the `wiki_scrape` folder run `npm run scrape` or `node scraper.js`.

  Environment variables (optional):
  - HEADLESS=0         show the browser (default headless)
  - TIMEOUT_MS         navigation/selector timeout in milliseconds (default 30000)
  - RETRIES            number of retry attempts on failure (default 2)
  - RATE_DELAY_MS      polite delay after load before extracting (default 1000)
*/

const URL = "https://hypixelskyblock.minecraft.wiki/w/Stats";

// Simple runtime toggles and limits (read from env for convenience)
const HEADLESS = process.env.HEADLESS !== "0";
const TIMEOUT_MS = Number(process.env.TIMEOUT_MS ?? "30000");
const RETRIES = Number(process.env.RETRIES ?? "2");
const RATE_DELAY_MS = Number(process.env.RATE_DELAY_MS ?? "1000");

// Use a common user-agent string so requests look like a normal browser
const USER_AGENT =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36";

// Utility: normalize whitespace and trim text
const cleanText = (value) => (value ?? "").replace(/\s+/g, " ").trim();

// Utility: deduplicate text entries while preserving order
const uniqueText = (values) => {
  const seen = new Set();
  const result = [];
  for (const value of values) {
    const cleaned = cleanText(value);
    if (cleaned && !seen.has(cleaned)) {
      seen.add(cleaned);
      result.push(cleaned);
    }
  }
  return result;
};

/*
  extractPageData(page)
  - `page` is a Playwright Page instance already navigated to the target URL
  - returns a plain object with the fields we care about
  Notes for beginners:
  - We attempt multiple selector strategies for the TOC because different MediaWiki skins
    render the table-of-contents with different class names.
  - We use `catch(() => null)` on optional lookups so the script doesn't throw if a tag
    is missing; instead we fall back to other values.
*/
const extractPageData = async (page) => {
  // page.title() returns the <title> tag value; site also has an H1 we prefer for the human title
  const titleTag = await page.title();
  const heading = await page
    .locator("h1#firstHeading")
    .first()
    .textContent()
    .catch(() => null);

  // meta description: try the standard name and OpenGraph as fallback
  const metaDescription = await page
    .locator('meta[name="description"]')
    .getAttribute("content")
    .catch(() => null);
  const ogDescription = await page
    .locator('meta[property="og:description"]')
    .getAttribute("content")
    .catch(() => null);

  // A list of selectors to locate TOC text across different wiki skins
  const tocSelectors = [
    "#toc .toctext",
    ".vector-toc .vector-toc-text",
    "nav#toc .vector-toc-text",
    "div#toc li a .toctext"
  ];

  // Try each selector until we find some items
  let tocItems = [];
  for (const selector of tocSelectors) {
    const items = await page.locator(selector).allTextContents();
    if (items.length) {
      tocItems = items;
      break;
    }
  }

  return {
    url: URL,
    pageTitle: cleanText(heading || titleTag),
    pageDescription: cleanText(metaDescription || ogDescription),
    tableOfContents: uniqueText(tocItems)
  };
};

// Small helper to pause (used for polite delays and backoff)
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/*
  Main scrape flow:
  - Launch browser and open a new page
  - Navigate to the URL and wait for the H1 to appear
  - Pause briefly (RATE_DELAY_MS) to allow any client-side rendering
  - Extract data and print JSON
  - On errors, retry a small number of times with exponential backoff
*/
const scrape = async () => {
  let lastError = null;

  for (let attempt = 0; attempt <= RETRIES; attempt += 1) {
    let browser;
    try {
      browser = await chromium.launch({ headless: HEADLESS });
      const context = await browser.newContext({
        userAgent: USER_AGENT,
        viewport: { width: 1280, height: 720 }
      });
      const page = await context.newPage();

      // Navigate and wait for main heading (this reduces race conditions)
      await page.goto(URL, { waitUntil: "domcontentloaded", timeout: TIMEOUT_MS });
      await page.waitForSelector("h1#firstHeading", { timeout: TIMEOUT_MS });
      // Be polite: small delay before scraping so dynamic pieces can settle
      await page.waitForTimeout(RATE_DELAY_MS);

      const data = await extractPageData(page);
      console.log(JSON.stringify(data, null, 2));
      await browser.close();

      // Mark success: return from function
      return;
    } catch (error) {
      // Save the last error to report if all retries fail
      lastError = error;
      if (attempt < RETRIES) {
        // Simple backoff: wait longer before the next attempt
        await wait(1000 * (attempt + 1));
      }
    } finally {
      if (browser) {
        await browser.close();
      }
    }
  }

  console.error("Scrape failed after retries.");
  if (lastError) {
    console.error(String(lastError));
  }
  process.exitCode = 1;
};

// Start the scraping job
scrape();
