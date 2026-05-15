# scraper_ai

Playwright scraping practice is located in [wiki_scrape/](wiki_scrape).

Quick start:

1. Install dependencies: `npm install`
2. Install browser binaries: `npx playwright install`
3. Run the scraper: `npm run scrape`

See [wiki_scrape/README.md](wiki_scrape/README.md) for the learning plan, GDPR notes, and details.

Install Typescript

1. Install Typescript: `npm install typescript`
2. Init: `npx tsc --init`
3. Install @types `npm install --save-dev typescript @types/node`

ts-node vs tsx
1. ts-node: use require runtime type-checking
2. tsx: fast development
e.g. `npx tsx /src/scraper.ts` or `node dist/scraper.js`