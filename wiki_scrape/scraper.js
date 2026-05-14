import { chromium } from "playwright";

const URL = "https://hypixelskyblock.minecraft.wiki/w/Stats";

const HEADLESS = process.env.HEADLESS !== "0";
const TIMEOUT_MS = Number(process.env.TIMEOUT_MS ?? "30000");
const RETRIES = Number(process.env.RETRIES ?? "2");
const RATE_DELAY_MS = Number(process.env.RATE_DELAY_MS ?? "1000");

const USER_AGENT =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36";

const cleanText = (value) => (value ?? "").replace(/\s+/g, " ").trim();

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

const extractPageData = async (page) => {
  const titleTag = await page.title();
  const heading = await page
    .locator("h1#firstHeading")
    .first()
    .textContent()
    .catch(() => null);

  const metaDescription = await page
    .locator('meta[name="description"]')
    .getAttribute("content")
    .catch(() => null);
  const ogDescription = await page
    .locator('meta[property="og:description"]')
    .getAttribute("content")
    .catch(() => null);

  const tocSelectors = [
    "#toc .toctext",
    ".vector-toc .vector-toc-text",
    "nav#toc .vector-toc-text",
    "div#toc li a .toctext"
  ];

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

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

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

      await page.goto(URL, { waitUntil: "domcontentloaded", timeout: TIMEOUT_MS });
      await page.waitForSelector("h1#firstHeading", { timeout: TIMEOUT_MS });
      await page.waitForTimeout(RATE_DELAY_MS);

      const data = await extractPageData(page);
      console.log(JSON.stringify(data, null, 2));
      await browser.close();
      return;
    } catch (error) {
      lastError = error;
      if (attempt < RETRIES) {
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

scrape();
