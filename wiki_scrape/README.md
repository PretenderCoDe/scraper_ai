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

## Running with TypeScript

This project can be run two ways when using TypeScript code in `src/`:

- Run directly with `tsx` (fast for development, no build step).
- Compile with `tsc` and run the emitted JavaScript (recommended for CI/production).

Recommended setup (from the `wiki_scrape` folder):

```bash
npm install --save-dev tsx typescript @types/node
npx playwright install
```

Run with `tsx` (dev, no build):

```bash
npx tsx src/scraper.ts
```

Run by compiling with `tsc` (build then run):

```bash
npx tsc
node dist/scraper.js
```

Suggested `package.json` scripts to add:

```json
"scripts": {
	"build": "tsc",
	"scrape": "npm run build && node dist/scraper.js",
	"dev:scrape": "tsx src/scraper.ts"
}
```

Environment variable examples:

- Bash / WSL:

```bash
HEADLESS=0 npx tsx src/scraper.ts
```

TypeScript checks and troubleshooting

- Run a type-only check without emitting JS:

```bash
npx tsc --noEmit
```

- If you installed `@types/node` but still see `process` or other Node globals as unknown, ensure `tsconfig.json` includes `"types": ["node"]` (or remove the `types` field to auto-include).
- If VS Code shows stale problems after changing types, run: **TypeScript: Restart TS Server** from the Command Palette or reload the window.

See [wiki_scrape/src/scraper.ts](src/scraper.ts) for the TypeScript source and [wiki_scrape/tsconfig.json](tsconfig.json) for compiler settings.