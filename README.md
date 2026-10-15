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

An Astro static site with an Apple-inspired design: system San Francisco/Inter type, white and light-grey (`#f5f5f7`) bands, large headlines, rounded image tiles, a translucent global nav with full-width flyout menus, and subtle scroll reveals. **All text and images are GACL's own, imported from the crawl**. Nothing is rewritten.

```bash
# 1. import content from the crawl (re-run after a new crawl)
python scraper/build_products.py           # product specs   -> site/src/data/products.json
python scraper/extract_pages.py            # every page      -> site/src/content/pages/*.json + site/public/media/*.webp
cd scraper && python extract_home.py       # homepage, menu, footer -> site/src/content/{home,nav,footer}.json

# 2. run / build the site
cd site && npm install && npm run dev      # http://localhost:4321
npm run build                              # static output in site/dist/
```

How it fits together:

| Piece | What it does |
| --- | --- |
| `scraper/extract_pages.py` | Walks each page's Elementor document and turns it into ordered sections of typed blocks (heading, text, list, image, cards, table, accordion, gallery, button, video, map). Reads background images from the page CSS and converts every image to WebP. |
| `scraper/extract_home.py` | Pulls the homepage's custom sections (10-slide hero, key figures, company intro and video, product cards, client logos, sustainability, Materials & Services, media, testimonials, investor strip, quick links), plus the menu and footer. |
| `site/src/pages/index.astro` | The homepage, laid out section by section. |
| `site/src/pages/[...slug].astro` | Every other page, at the **same URL as on gacl.com** (e.g. `/the-corporate-world/`). |
| `site/src/components/Section.astro` | Chooses a layout per section: centered headline + reading column, split image/text, card grid, year timeline (Our Journey), or a dark call-to-action band. |
| `site/src/components/ProductGroup.astro` | The product-group pages: specification tables, applications, cautions, and Leaflet/MSDS/Enquiry buttons. |
| `site/src/components/Nav.astro`, `Footer.astro` | Global nav with flyouts (from the original menu) and footer (original columns, addresses and legal lines). |

66 pages are imported. The 6 Safety "services" pages have no body text on the live site, so they aren't generated. Their links, and links to anything not imported (logins, forms), go to the page on gacl.com.
