# Amazon Dual-Mode E-Commerce Matrix Intelligence Engine

A production-grade, asynchronous Amazon search-results data extraction engine designed for large-scale market research and SEO keyword tracking. Equipped with a **Dual-Mode Switching Architecture**, it addresses the core pain points of cross-border e-commerce data analysts by elegantly separating or aggregating organic rankings and sponsored advertisement matrixes.

---

## Core Commercial Value & Architecture

Unlike basic, fragile scraping scripts that break under Amazon's frequent structural A/B tests or dynamic layouts, this engine introduces enterprise-grade data sanitation and a resilient fallback mechanism. 

### Featured Highlights:
* **Dual-Mode Toggle (`RUN_MODE`)**: 
    * `organic`: Drops all banners, videos, and carousel ads via deep DOM parent-traversal auditing. Delivers a clean sheet of the **top 22 pure organic rankings** for accurate SEO weight tracking.
    * `matrix`: Captures the full competitive landscape (**34+ items per page**), sweeping up Sponsored Brands, Video Ads, and Carousel Recommendations for complete PPC competitor matrix analysis.
* **Four-Stage Anti-Lazy-Load Stimulation**: Utilizes coordinated pixel-scrolling scripts via advanced headless scenarios to extract products dynamically injected at the absolute bottom of Amazon's layout.
* **Dynamic Hydration Fallback Guard**: Detects and intercepts Amazon's asynchronous dynamic rendering (Lazy Hydration) traps. Instead of dumping raw `N/A` or corrupted `0` review fields that confuse business users, it gracefully isolates un-hydrated ad units with clear enterprise-level tracking tags (`Sponsored (Ad Dynamic)`).
* **Zero-Cost Smart Local Caching**: Implements MDS-hashed local payload caching to drastically reduce proxy credits during debugging phases and allow lightning-fast local re-parsing.

---

## Technical Stack & Dependencies

* **Language**: Python 3.8+
* **Scraping Core**: `BeautifulSoup4` + `lxml` parser, `requests`
* **Targeting Logic**: Dynamic DOM Node Traversal & Fallback Regular Expressions
* **Proxy Integration**: ScraperAPI Premium Gateway (Headless JS Scenario Engine Enabled)

---

## ⚙️ How It Works: The Pipeline
[Target Search URL]\
│\
▼\
[ScraperAPI Gateway] ──(4-Stage Scroll JS Scenario)──► [Fully Hydrated DOM]\
│\
▼\
[MDS Cache Verification]\
│\
▼\
[RUN_MODE Policy Evaluator]\
├── organic: DOM Parent Ad-Filter Ray\
└── matrix:  Full Matrix Sweeper\
│\
▼\
[Data Sanitation Guard]\
├── Price Regex Extractor ($XX.XX)\
└── Anti-Star Review Disambiguator\
│\
▼\
[amazon_niche_data.csv]\
---

## 📊 Sample Output Data (Scannability Showcase)

The final `.csv` output is perfectly tailored for business presentation. Notice how asynchronous ad dynamic data is seamlessly handled:

| Date | Keyword | ASIN | Price | Reviews | Title |\
| :--- | :--- | :--- | :--- | :--- | :--- |\
| 2026-05-18 16:34:15 | 3D printer nozzle 0.4mm | B0CXYZ7890 | $12.99 | 1420 | Creality Original 3D Printer Nozzles Pack... |\
| 2026-05-18 16:34:15 | 3D printer nozzle 0.4mm | B0G34DV6HW | **Sponsored (Ad Dynamic)** | **Sponsored (Ad Dynamic)** | Upgraded Quick-Swap Nozzle Compatible with Flashforge AD5X... |

---

##  Quick Start

### 1. Installation
install the minimal dependencies:
```bash
pip install beautifulsoup4 lxml requests
```

### 2. Configuration
Open amazon_scraper.py and input your ScraperAPI credentials and preferred analytical mode:
```python
SCRAPER_API_KEY = 'YOUR_SCRAPER_API_KEY'
RUN_MODE = "matrix"  # Options: "organic" | "matrix"
```

3. Execution
Run the engine to extract data or parse from your local cache directory (amazon_cache/):
```bash
python amazon_scraper.py
```

## Production-Ready Resiliency Features
### 1. Anti-Star Review Disambiguator
Standard regex scrapers regularly misinterpret strings like "3.8 out of 5 stars (150 reviews)" and merge them into corrupted values like 385150. This engine isolates review counts through an strict layer architecture: prioritizing s-underline-text targets, explicitly filtering out star tokens within aria-label definitions, and leveraging a parenthetical fallback regex layer \(\d+[\d,]*\).

### 2. Physical Structural Defense Guard
When dynamic Amazon layouts obscure traditional advertising class signatures (such as ad-preview or s-sponsored), the engine deploys a deterministic validation check. If a crawled object simultaneously returns null states for both pricing and user metrics within a high-velocity page zone, it automatically deploys a dynamic banner tag, ensuring zero output pollution in the final spreadsheet.


---