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
| `assets/` | Downloaded images |

## 2. Rebuild the site

Pending: the site will be built from the scraped content.
