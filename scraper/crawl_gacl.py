"""Crawl every page of the GACL website with Scrapling and save its content.

Output layout (under --out, default ``scrape/output``):
    pages/<slug>.html      raw HTML of each page
    pages/<slug>.json      structured content: title, meta, nav, headings,
                           text blocks, lists, tables, images, links
    assets/...             downloaded images (and documents with --documents)
    sitemap.json           every crawled URL -> slug, title, status, depth
    navigation.json        the site's main menu tree, taken from the homepage

Usage:
    python scraper/crawl_gacl.py                       # full crawl of gacl.com
    python scraper/crawl_gacl.py --max-pages 50        # quick partial crawl
    python scraper/crawl_gacl.py --dynamic             # render pages in Chromium
    python scraper/crawl_gacl.py --documents           # also save PDFs/DOCs
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from collections import deque
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

from scrapling.fetchers import DynamicFetcher, Fetcher

DEFAULT_START = "https://www.gacl.com/"
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".avif"}
DOC_EXT = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip"}
SKIP_EXT = IMAGE_EXT | DOC_EXT | {".mp4", ".mp3", ".css", ".js", ".xml", ".rar"}
SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "whatsapp:", "data:")


def normalize(url: str) -> str:
    url, _ = urldefrag(url.strip())
    parsed = urlparse(url)
    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    host = parsed.netloc.lower().removeprefix("www.")
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{parsed.scheme}://{host}{path}{query}"


def slugify(url: str) -> str:
    parsed = urlparse(url)
    slug = parsed.path.strip("/").replace("/", "__") or "home"
    if parsed.query:
        slug += "__" + hashlib.md5(parsed.query.encode()).hexdigest()[:8]
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", slug)
    return re.sub(r"\.(html?|php|aspx?|jsp)$", "", slug)[:150]


def clean(text: str | None) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def text_of(el) -> str:
    return clean(el.get_all_text(separator=" ", strip=True))


def extract_nav(page) -> list[dict]:
    """Build the menu tree from the first <nav>/header menu on the page."""

    def walk(ul) -> list[dict]:
        items = []
        for li in ul.children:
            if li.tag != "li":
                continue
            link = li.css("a")
            label = text_of(link[0]) if link else clean(li.text)
            href = page.urljoin(link[0].attrib.get("href", "")) if link else ""
            sub = next((c for c in li.children if c.tag == "ul"), None)
            if sub is None:
                sub = next(iter(li.css("ul")), None)
            items.append({"label": label, "url": href, "children": walk(sub) if sub else []})
        return items

    for selector in ("nav ul", "header ul", "#menu ul", ".menu", ".navbar-nav", "ul.nav"):
        menus = page.css(selector)
        if menus:
            tree = walk(max(menus, key=lambda m: len(m.css("a"))))
            if tree:
                return tree
    return []


def extract_content(page, url: str) -> dict:
    main = None
    for selector in ("main", "#content", ".content", "article", "#main", ".main-content"):
        found = page.css(selector)
        if found:
            main = found[0]
            break
    body = page.css("body")
    root = main if main is not None else (body[0] if body else page)

    headings = [
        {"level": int(h.tag[1]), "text": text_of(h)}
        for h in root.css("h1, h2, h3, h4, h5, h6")
        if text_of(h)
    ]
    paragraphs = [t for t in (text_of(p) for p in root.css("p")) if len(t) > 1]
    lists = [
        items
        for items in ([text_of(li) for li in ul.css("li")] for ul in root.css("ul, ol"))
        if items and not all(len(i) < 2 for i in items)
    ]
    tables = []
    for table in root.css("table"):
        rows = [[text_of(c) for c in tr.css("th, td")] for tr in table.css("tr")]
        rows = [r for r in rows if any(r)]
        if rows:
            tables.append(rows)

    images = []
    for img in page.css("img"):
        src = img.attrib.get("src") or img.attrib.get("data-src") or img.attrib.get("data-lazy-src")
        if src and not src.startswith("data:"):
            images.append({"src": page.urljoin(src), "alt": clean(img.attrib.get("alt"))})
    for img in page.css("img[srcset], source[srcset], img[data-srcset]"):
        srcset = img.attrib.get("srcset") or img.attrib.get("data-srcset") or ""
        for candidate in srcset.split(","):
            if candidate.strip():
                images.append({"src": page.urljoin(candidate.split()[0]), "alt": clean(img.attrib.get("alt"))})
    for el in page.css("[style*='background']"):
        for bg in re.findall(r"url\(['\"]?([^'\")]+)", el.attrib.get("style", "")):
            images.append({"src": page.urljoin(bg), "alt": "", "background": True})

    links = []
    for a in page.css("a[href]"):
        href = a.attrib.get("href", "").strip()
        if href and not href.lower().startswith(SKIP_SCHEMES) and not href.startswith("#"):
            links.append({"text": text_of(a), "url": page.urljoin(href)})
    contacts = sorted(
        {a.attrib["href"] for a in page.css("a[href^='mailto:'], a[href^='tel:']")}
    )

    meta = {
        (m.attrib.get("name") or m.attrib.get("property")): m.attrib.get("content", "")
        for m in page.css("meta")
        if (m.attrib.get("name") or m.attrib.get("property")) and m.attrib.get("content")
    }
    title = page.css("title")
    return {
        "url": url,
        "title": text_of(title[0]) if title else "",
        "meta": meta,
        "headings": headings,
        "paragraphs": paragraphs,
        "lists": lists,
        "tables": tables,
        "images": images,
        "links": links,
        "contacts": contacts,
        "full_text": text_of(root),
    }


class Crawler:
    def __init__(self, args):
        self.args = args
        self.start = args.start
        self.host = urlparse(normalize(self.start)).netloc
        self.out = Path(args.out)
        self.pages_dir = self.out / "pages"
        self.assets_dir = self.out / "assets"
        self.pages_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.seen: set[str] = set()
        self.sitemap: dict[str, dict] = {}
        self.assets: dict[str, str] = {}
        self.documents: set[str] = set()

    def same_site(self, url: str) -> bool:
        return urlparse(url).netloc.lower().removeprefix("www.") == self.host

    def render(self, url: str):
        options = {"network_idle": True, "timeout": 60000}
        if self.args.chromium_path:
            options["executable_path"] = self.args.chromium_path
        return DynamicFetcher.fetch(url, **options)

    def fetch(self, url: str):
        if self.args.dynamic:
            return self.render(url)
        page = Fetcher.get(url, impersonate="chrome", stealthy_headers=True, timeout=30, retries=3)
        # Fall back to a real browser when the static HTML is an empty JS shell.
        if page.status == 200 and len(page.css("a[href]")) < 3 and not self.args.no_fallback:
            page = self.render(url)
        return page

    def download(self, url: str) -> str | None:
        if url in self.assets:
            return self.assets[url]
        parsed = urlparse(url)
        local = self.assets_dir / parsed.netloc / parsed.path.lstrip("/")
        if local.suffix == "" or local.name == "":
            local = local / "index.bin"
        rel = str(local.relative_to(self.out))
        if not local.exists():
            try:
                resp = Fetcher.get(url, impersonate="chrome", timeout=60, retries=2)
                if resp.status != 200:
                    return None
                local.parent.mkdir(parents=True, exist_ok=True)
                local.write_bytes(resp.body)
            except Exception as exc:  # noqa: BLE001 - keep crawling on asset errors
                print(f"   ! asset failed {url}: {exc}", file=sys.stderr)
                return None
        self.assets[url] = rel
        return rel

    def download_all_images(self):
        """Download every same-site image referenced anywhere in the saved HTML
        (src, srcset, lazy-load attributes, inline CSS), skipping WordPress
        resized copies when the original is also referenced."""
        pattern = re.compile(
            r"https?://(?:www\.)?" + re.escape(self.host) +
            r"/[^\s\"'()<>]+?\.(?:png|jpe?g|gif|webp|svg|avif|ico)", re.I)
        urls: set[str] = set()
        for html in self.pages_dir.glob("*.html"):
            text = html.read_text(encoding="utf-8", errors="ignore").replace("\\/", "/")
            urls.update(pattern.findall(text))
        originals = {re.sub(r"-\d+x\d+(?=\.\w+$)", "", u) for u in urls}
        wanted = sorted(u for u in urls if u in originals or re.sub(r"-\d+x\d+(?=\.\w+$)", "", u) not in urls)
        print(f"Downloading {len(wanted)} images ({len(urls)} referenced)")
        manifest = {u: self.download(u) for u in wanted}
        (self.out / "images.json").write_text(json.dumps(manifest, indent=2))
        print(f"Saved {sum(1 for v in manifest.values() if v)} images -> {self.assets_dir}")

    def run(self):
        queue = deque([(self.start, 0)])
        self.seen.add(normalize(self.start))
        nav_saved = False
        while queue and len(self.sitemap) < self.args.max_pages:
            url, depth = queue.popleft()
            print(f"[{len(self.sitemap) + 1}] depth={depth} {url}")
            try:
                page = self.fetch(url)
            except Exception as exc:  # noqa: BLE001
                print(f"   ! fetch failed: {exc}", file=sys.stderr)
                self.sitemap[url] = {"status": "error", "error": str(exc), "depth": depth}
                continue

            slug = slugify(normalize(url))
            entry = {"slug": slug, "status": page.status, "depth": depth, "final_url": page.url}
            self.sitemap[url] = entry
            if page.status != 200:
                continue

            (self.pages_dir / f"{slug}.html").write_bytes(page.body)
            content = extract_content(page, url)
            entry["title"] = content["title"]

            if not nav_saved:
                nav = extract_nav(page)
                (self.out / "navigation.json").write_text(json.dumps(nav, indent=2, ensure_ascii=False))
                nav_saved = True

            if not self.args.no_assets:
                for img in content["images"]:
                    img["local"] = self.download(img["src"])

            for link in content["links"]:
                fetch_url = urldefrag(link["url"])[0]
                target = normalize(fetch_url)
                ext = Path(urlparse(target).path).suffix.lower()
                if not self.same_site(target):
                    continue
                if ext in DOC_EXT:
                    self.documents.add(link["url"])
                    if self.args.documents:
                        link["local"] = self.download(link["url"])
                    continue
                if ext in SKIP_EXT or target in self.seen:
                    continue
                if depth + 1 <= self.args.max_depth:
                    self.seen.add(target)
                    queue.append((fetch_url, depth + 1))

            (self.pages_dir / f"{slug}.json").write_text(json.dumps(content, indent=2, ensure_ascii=False))
            time.sleep(self.args.delay)

        (self.out / "sitemap.json").write_text(json.dumps(self.sitemap, indent=2, ensure_ascii=False))
        (self.out / "documents.json").write_text(json.dumps(sorted(self.documents), indent=2))
        ok = sum(1 for e in self.sitemap.values() if e.get("status") == 200)
        print(f"\nDone: {ok}/{len(self.sitemap)} pages saved, {len(self.assets)} assets, "
              f"{len(self.documents)} documents found -> {self.out}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--out", default="scrape/output")
    parser.add_argument("--max-pages", type=int, default=2000)
    parser.add_argument("--max-depth", type=int, default=10)
    parser.add_argument("--delay", type=float, default=0.5, help="seconds between page requests")
    parser.add_argument("--dynamic", action="store_true", help="render every page in Chromium")
    parser.add_argument(
        "--chromium-path",
        default=os.environ.get("CHROMIUM_PATH"),
        help="Chromium binary to use instead of Playwright's bundled one (or set CHROMIUM_PATH)",
    )
    parser.add_argument("--no-fallback", action="store_true", help="never fall back to Chromium")
    parser.add_argument("--no-assets", action="store_true", help="skip image downloads")
    parser.add_argument("--documents", action="store_true", help="download linked PDFs/DOCs too")
    parser.add_argument("--images-only", action="store_true",
                        help="skip crawling; download every image referenced in already-saved pages")
    args = parser.parse_args()
    crawler = Crawler(args)
    if args.images_only:
        crawler.download_all_images()
        return
    crawler.run()
    if not args.no_assets:
        crawler.download_all_images()


if __name__ == "__main__":
    main()
