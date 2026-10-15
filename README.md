# GACL website redesign

Redesign of [gacl.com](https://www.gacl.com/), the Gujarat Alkalies and Chemicals Limited site: modern, elegant, white-background theme.

## 1. Scrape the existing site

`scraper/crawl_gacl.py` crawls every page of the current site with [Scrapling](https://github.com/D4Vinci/Scrapling). It saves each page's raw HTML plus its structured content (headings, text, lists, tables, images, links), the main menu tree, and the site's images. All of this is source material for the rebuild.

```bash
pip install -r scraper/requirements.txt
python scraper/crawl_gacl.py                   # full crawl -> scrape/output/
python scraper/crawl_gacl.py --max-pages 20    # quick test
python scraper/crawl_gacl.py --documents       # also download linked PDFs
python scraper/crawl_gacl.py --dynamic         # render every page in Chromium
python scraper/crawl_gacl.py --images-only     # download every image referenced in saved pages
python scraper/build_products.py               # product specs -> site/src/data/products.json
python scraper/build_directory.py              # dealers + tenders -> site/src/data/*.json
```

Pages are fetched with Scrapling's `Fetcher`, which impersonates Chrome. When the static HTML looks like an empty JavaScript shell, the crawler falls back to `DynamicFetcher` (headless Chromium). If Playwright's bundled Chromium doesn't match your installed version, pass `--chromium-path /path/to/chromium` or set `CHROMIUM_PATH`.

Output (`scrape/output/`):

| Path | Contents |
| --- | --- |
| `pages/<slug>.html` | Raw HTML |
| `pages/<slug>.json` | Title, meta, headings, paragraphs, lists, tables, images, links, contacts |
| `navigation.json` | Main menu tree |
| `sitemap.json` | Every crawled URL with status, depth, title |
| `documents.json` | Linked PDFs and other documents |
| `images.json` | Every referenced image URL -> local file |
| `assets/` | Downloaded images (git-ignored; 97 MB, re-download with `--images-only`) |

The last crawl (15 Oct 2026) saved 140 of 143 pages and 739 images, and listed 876 linked documents. The three failures are a broken link on the live site, one board-member profile and one notice page.

## 2. The new site (`site/`)

A static multi-page site built with [Astro](https://astro.build): white background, GACL blue as the single accent colour, and green reserved for sustainability. It has 29 pages.

```bash
cd site
npm install
npm run dev       # http://localhost:4321
npm run build     # static output in site/dist/
```

| Section | Pages |
| --- | --- |
| Home | Hero, key numbers, company intro, product bento grid, industries, sustainability, timeline, news, investors |
| Company | Corporate World, Philosophy, Governing Body, Journey (timeline + archive photos), Honours & Recognitions |
| Products | Overview with live product finder, plus one page per group (10) with spec tables, applications, cautions, leaflet & MSDS links |
| Sustainability | Environment, Safety & Health, CSR, Governance & Certificates |
| Investors | Filings links, tickers, grievance redressal contact |
| Partners | Materials & Services, Tenders (open/closed status computed at build), searchable Dealer Network |
| Careers, Media, Contact | Life at GACL, news & events, enquiry form that routes to the right desk |

Where the content comes from:

- `site/src/data/products.json`, `dealers.json` and `tenders.json` are generated from the crawl by the scripts above.
- `site/src/data/site.ts` holds facts taken from the crawl (figures, timeline, board, awards, addresses, emails). The descriptive copy was rewritten for the new design.
- `site/public/images/` holds 27 photos from the crawl, converted to WebP (2.8 MB in total).

Links for investor filings, vendor registration, current openings and login portals still point to the matching pages on gacl.com until those systems are migrated.

### Design system

Tokens live in `site/src/styles/global.css`: colours, type (Manrope display, Inter body), radii, shadows and spacing. Shared pieces are in `site/src/components/`: `Header` (sticky, mega-menu, mobile drawer), `Footer`, `PageHero` and `Icon` (a hand-drawn line icon set). Section patterns were inspired by 21st.dev: a lamp-glow hero, a bento grid, a marquee and a framed CTA footer. All of them are re-implemented here in plain Astro and CSS, with no React dependency.
