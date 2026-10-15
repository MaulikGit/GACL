"""Convert crawled gacl.com pages into structured content for the new site.

The original site is built with Elementor. This importer walks each page's
main Elementor document and turns it into an ordered list of sections, each
holding typed blocks (heading, text, list, image, cards, table, accordion,
gallery, button, video, map). Text is kept exactly as published; images are
converted to WebP and copied into the site.

Outputs (under --out, default site/src/content):
    pages/<slug>.json   one file per page
    home.json           the homepage's custom sections
    nav.json            the main menu
    footer.json         footer columns and addresses

Usage:
    python scraper/extract_pages.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

from scrapling.parser import Selector

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "scrape/output/pages"
CSS_DIR = ROOT / "scrape/output/css"
ASSETS = ROOT / "scrape/output/assets"
SITEMAP = ROOT / "scrape/output/sitemap.json"
BASE = "https://gacl.com/"

INLINE_TAGS = {"strong", "b", "em", "i", "a", "br", "sub", "sup", "span", "u"}
SKIP_WIDGETS = {
    "divider.default", "spacer.default", "social-icons.default", "ekit-nav-menu.default",
    "eael-simple-menu.default", "industrium_decoration.default", "icon.default",
}
HIDDEN = ("elementor-hidden-desktop", "elementor-hidden-widescreen")
LAZY_ATTRS = ("data-src", "data-lazy-src", "data-original", "src")


# ---------------------------------------------------------------- helpers

def clean(text: str | None) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def text_of(el) -> str:
    return clean(el.get_all_text(separator=" ", strip=True))


def classes(el) -> str:
    return el.attrib.get("class", "") or ""


def is_hidden(el) -> bool:
    cls = classes(el)
    return any(h in cls for h in HIDDEN) or re.search(r"(?<![\w-])elementor-hidden(?![\w-])", cls) is not None


def img_src(img) -> str:
    for attr in LAZY_ATTRS:
        v = (img.attrib.get(attr) or "").strip()
        if v and not v.startswith("data:"):
            return urljoin(BASE, v.replace("https: //", "https://"))
    srcset = img.attrib.get("data-srcset") or img.attrib.get("srcset") or ""
    if srcset:
        return urljoin(BASE, srcset.split(",")[-1].split()[0])
    return ""


def full_size(url: str) -> str:
    """WordPress serves resized copies (-1024x432.jpg); prefer the original."""
    return re.sub(r"-\d+x\d+(?=\.\w+$)", "", url)


def inline_html(el) -> str:
    """Serialise an element's children keeping only safe inline markup."""
    html = el.html_content
    html = re.sub(r"<(script|style)\b.*?</\1>", "", html, flags=re.S | re.I)
    inner = re.sub(r"^<[^>]+>|</[^>]+>$", "", html.strip(), count=1)
    inner = re.sub(r"</[^>]+>$", "", inner.strip())

    def tag(m):
        closing, name, attrs = m.group(1), m.group(2).lower(), m.group(3) or ""
        if name not in INLINE_TAGS:
            return " " if name in {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6"} else ""
        if name == "span":
            return ""
        if name == "br":
            return "<br>"
        if closing:
            return f"</{name}>"
        if name == "a":
            href = re.search(r'href="([^"]*)"', attrs)
            return f'<a href="{rewrite_link(href.group(1)) if href else "#"}">'
        return f"<{name}>"

    out = re.sub(r"<(/?)([a-zA-Z0-9]+)([^>]*)>", tag, inner)
    out = re.sub(r"&nbsp;", " ", out)
    out = re.sub(r"\s+", " ", out).strip()
    out = re.sub(r"(<br>\s*)+$", "", out)
    return out


def rewrite_link(href: str) -> str:
    """Point internal page links at the new site; keep documents on gacl.com."""
    href = href.strip()
    if not href or href.startswith(("mailto:", "tel:", "#", "javascript:")):
        return href
    url = urljoin(BASE, href)
    p = urlparse(url)
    if p.netloc.removeprefix("www.") in {"gacl.com", "gaclsite.com"} and "/wp-content/" not in p.path:
        path = p.path if p.path.endswith("/") or "." in p.path.rsplit("/", 1)[-1] else p.path + "/"
        return path + (f"?{p.query}" if p.query else "")
    return url


# ---------------------------------------------------------------- images

class Images:
    """Collects image URLs and converts them to WebP inside the site."""

    def __init__(self, out_dir: Path):
        self.out_dir = out_dir
        self.map: dict[str, str] = {}
        manifest = ROOT / "scrape/output/images.json"
        self.local = json.loads(manifest.read_text()) if manifest.exists() else {}

    def __call__(self, url: str, width: int = 1600) -> str:
        if not url:
            return ""
        url = url.replace("http://", "https://")
        if url in self.map:
            return self.map[url]
        for candidate in (full_size(url), url):
            src = self._local_file(candidate)
            if src:
                break
        else:
            return ""
        name = Path(urlparse(url).path).stem[:60]
        digest = hashlib.md5(url.encode()).hexdigest()[:6]
        is_svg = src.suffix.lower() == ".svg"
        rel = f"/media/{name}-{digest}{'.svg' if is_svg else '.webp'}"
        target = self.out_dir / rel.lstrip("/")
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            if is_svg:
                target.write_bytes(src.read_bytes())
            else:
                from PIL import Image
                try:
                    im = Image.open(src)
                    im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
                    if im.width > width:
                        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
                    im.save(target, "WEBP", quality=80, method=5)
                except Exception as exc:  # noqa: BLE001
                    print(f"  ! image failed {url}: {exc}")
                    return ""
        self.map[url] = rel
        return rel

    def _local_file(self, url: str) -> Path | None:
        p = urlparse(url)
        path = ASSETS / p.netloc.removeprefix("www.") / p.path.lstrip("/")
        if path.exists():
            return path
        alt = ASSETS / "gacl.com" / p.path.lstrip("/")
        if alt.exists():
            return alt
        # Not downloaded during the crawl (e.g. only referenced from CSS): fetch it now.
        try:
            from scrapling.fetchers import Fetcher
            resp = Fetcher.get(url, impersonate="chrome", timeout=40, retries=1)
            if resp.status == 200 and len(resp.body) > 200:
                alt.parent.mkdir(parents=True, exist_ok=True)
                alt.write_bytes(resp.body)
                return alt
        except Exception:  # noqa: BLE001
            pass
        return None


# ---------------------------------------------------------------- CSS backgrounds

def load_backgrounds() -> dict[str, str]:
    """Map Elementor element ids to their background image URLs."""
    bgs: dict[str, str] = {}
    rule = re.compile(r"\.elementor-element-([0-9a-f]{6,8})(?:[^{,]*?)\{([^}]*)\}")
    for css in CSS_DIR.glob("*.css"):
        text = css.read_text(encoding="utf-8", errors="ignore")
        for m in rule.finditer(text):
            url = re.search(r'background-image:\s*url\("?([^")]+)"?\)', m.group(2))
            if url and m.group(1) not in bgs:
                bgs[m.group(1)] = url.group(1)
    return bgs


# ---------------------------------------------------------------- blocks

class Extractor:
    def __init__(self, images: Images, backgrounds: dict[str, str], url: str):
        self.img = images
        self.bgs = backgrounds
        self.url = url

    # generic HTML (custom HTML widgets, text editors, accordion bodies)
    def generic(self, root) -> list[dict]:
        blocks: list[dict] = []
        taken: list = []
        nodes = root.xpath(
            ".//h1|.//h2|.//h3|.//h4|.//h5|.//h6|.//p|.//ul|.//ol|.//table|.//img|.//iframe"
            "|.//a[contains(@class,'btn') or contains(@class,'button') or contains(@class,'link2')]"
        )
        for node in nodes:
            if any(self._inside(node, t) for t in taken) or is_hidden(node) or self._in_chrome(node, root):
                continue
            tag = node.tag
            if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
                t = text_of(node)
                if t:
                    blocks.append({"type": "heading", "level": int(tag[1]), "text": t})
                    taken.append(node)
            elif tag == "p":
                h = inline_html(node)
                if clean(re.sub(r"<[^>]+>", "", h)):
                    blocks.append({"type": "text", "html": h})
                taken.append(node)
            elif tag in {"ul", "ol"}:
                items = [inline_html(li) for li in node.children if li.tag == "li"]
                items = [i for i in items if clean(re.sub(r"<[^>]+>", "", i))]
                if items:
                    blocks.append({"type": "list", "ordered": tag == "ol", "items": items})
                taken.append(node)
            elif tag == "table":
                rows = [[inline_html(c) for c in tr.css("th, td")] for tr in node.css("tr")]
                rows = [r for r in rows if any(clean(re.sub(r"<[^>]+>", "", c)) for c in r)]
                if rows:
                    blocks.append({"type": "table", "rows": rows})
                taken.append(node)
            elif tag == "img":
                src = self.img(img_src(node))
                if src and not re.search(r"(arrow|linkIcon|blank)", src, re.I):
                    blocks.append({"type": "image", "src": src, "alt": clean(node.attrib.get("alt"))})
            elif tag == "iframe":
                src = node.attrib.get("src") or node.attrib.get("data-src") or ""
                if src:
                    blocks.append({"type": "embed", "src": src})
            elif tag == "a":
                t = text_of(node)
                if t:
                    blocks.append({"type": "button", "text": t, "href": rewrite_link(node.attrib.get("href", ""))})
                taken.append(node)
        return blocks

    @staticmethod
    def _in_chrome(node, root) -> bool:
        """True for sidebars, share bars, post navigation and similar theme chrome."""
        p = node.parent
        while p is not None and p._root is not root._root:
            c = classes(p) + " " + (p.attrib.get("id") or "")
            if re.search(r"sidebar|widget-area|post-navigation|comment|related|share|post-meta|breadcrumbs|elementor-location-(header|footer|popup)", c):
                return True
            if p.tag in ("aside", "nav", "header", "footer"):
                return True
            p = p.parent
        return False

    @staticmethod
    def _inside(node, ancestor) -> bool:
        target = ancestor._root
        el = node._root.getparent()
        while el is not None:
            if el is target:
                return True
            el = el.getparent()
        return False

    # Elementor widgets
    def widget(self, w) -> list[dict]:
        kind = w.attrib.get("data-widget_type", "")
        if kind in SKIP_WIDGETS:
            return []
        if kind in {"heading.default", "industrium_heading.default"}:
            h = w.css("h1, h2, h3, h4, h5, h6")
            t = text_of(w)
            if not t:
                return []
            level = int(h[0].tag[1]) if h else 3
            sub = w.css(".industrium-heading-subtitle, .subtitle")
            if sub and text_of(sub[0]) and text_of(sub[0]) != t:
                return [{"type": "eyebrow", "text": text_of(sub[0])},
                        {"type": "heading", "level": level, "text": text_of(h[0]) if h else t}]
            return [{"type": "heading", "level": level, "text": text_of(h[0]) if h else t}]
        if kind == "image.default":
            img = w.css("img")
            if not img:
                return []
            src = self.img(img_src(img[0]))
            cap = w.css("figcaption")
            link = w.css("a[href]")
            return [{"type": "image", "src": src, "alt": clean(img[0].attrib.get("alt")),
                     "caption": text_of(cap[0]) if cap else "",
                     "href": rewrite_link(link[0].attrib.get("href", "")) if link else ""}] if src else []
        if kind == "icon-list.default":
            items = []
            for li in w.css("li"):
                a = li.css("a[href]")
                t = text_of(li)
                if t:
                    items.append(f'<a href="{rewrite_link(a[0].attrib["href"])}">{t}</a>' if a else t)
            return [{"type": "list", "ordered": False, "items": items}] if items else []
        if kind in {"elementskit-icon-box.default", "icon-box.default", "image-box.default"}:
            return [self.card(w)]
        if kind in {"button.default", "industrium_button.default"}:
            a = w.css("a")
            t = text_of(w)
            return [{"type": "button", "text": t, "href": rewrite_link(a[0].attrib.get("href", "")) if a else ""}] if t else []
        if kind in {"image-carousel.default", "gallery.default", "industrium_image_carousel.default"}:
            seen, imgs = set(), []
            for i in w.css("img"):
                src = self.img(img_src(i))
                if src and src not in seen:
                    seen.add(src)
                    imgs.append({"src": src, "alt": clean(i.attrib.get("alt"))})
            for a in w.css("a[href]"):
                href = a.attrib["href"]
                if re.search(r"\.(jpe?g|png|webp)$", href, re.I):
                    src = self.img(href)
                    if src and src not in seen:
                        seen.add(src)
                        imgs.append({"src": src, "alt": ""})
            return [{"type": "gallery", "images": imgs}] if imgs else []
        if kind in {"accordion.default", "toggle.default", "tabs.default", "eael-adv-tabs.default",
                    "elementskit-simple-tab.default"}:
            titles = w.css(".elementor-tab-title, .eael-tab-title, .elementskit-tab-nav li, .eael-tabs-nav li")
            bodies = w.css(".elementor-tab-content, .eael-tab-content-item, .elementskit-tab-pane, .tab-pane")
            items = []
            for i, b in enumerate(bodies):
                title = text_of(titles[i]) if i < len(titles) else f"Item {i + 1}"
                items.append({"title": title, "blocks": self.generic(b)})
            # Elementor renders tab titles twice (desktop + mobile); de-duplicate.
            uniq, seen = [], set()
            for it in items:
                key = (it["title"], json.dumps(it["blocks"])[:200])
                if key not in seen:
                    seen.add(key)
                    uniq.append(it)
            return [{"type": "accordion", "items": uniq}] if uniq else []
        if kind == "video.default":
            settings = w.attrib.get("data-settings", "")
            m = re.search(r'(?:youtube_url|vimeo_url|hosted_url)\\?":\\?"([^"\\]+)', settings.replace("\\/", "/"))
            return [{"type": "video", "url": m.group(1)}] if m else []
        if kind == "google_maps.default":
            f = w.css("iframe")
            return [{"type": "embed", "src": f[0].attrib.get("src", "")}] if f else []
        if kind == "counter.default":
            num = w.css(".elementor-counter-number")
            return [{"type": "stat", "value": num[0].attrib.get("data-to-value", text_of(num[0])) if num else "",
                     "suffix": text_of(w.css(".elementor-counter-number-suffix")[0]) if w.css(".elementor-counter-number-suffix") else "",
                     "label": text_of(w.css(".elementor-counter-title")[0]) if w.css(".elementor-counter-title") else ""}]
        if kind == "eael-data-table.default":
            return self.generic(w)
        # text-editor, special text, html, shortcode, template, listings, everything else
        return self.generic(w)

    def card(self, root) -> dict:
        img = root.css("img")
        title = root.css("h1, h2, h3, h4, h5, h6, .elementskit-info-box-title, .elementor-icon-box-title, .elementor-image-box-title")
        desc = root.css("p, .elementor-icon-box-description, .elementor-image-box-description, .box-body")
        link = root.css("a[href]")
        title_text = text_of(title[0]) if title else ""
        text_html = " ".join(inline_html(d) for d in desc if text_of(d) and text_of(d) != title_text)
        btn = [a for a in link if text_of(a) and text_of(a) != title_text]
        return {
            "type": "card",
            "image": self.img(img_src(img[0]), 900) if img else "",
            "title": title_text,
            "html": text_html.strip(),
            "href": rewrite_link(link[0].attrib.get("href", "")) if link else "",
            "cta": text_of(btn[0]) if btn else "",
        }

    # containers
    def container(self, node, depth: int = 0) -> list[dict]:
        if is_hidden(node):
            return []
        if node.attrib.get("data-widget_type"):
            return self.widget(node)
        kids = [c for c in node.children if c.tag in ("div", "section") and not is_hidden(c)]
        child_containers = [c for c in kids if "e-con" in classes(c) or "elementor-column" in classes(c)
                            or "elementor-section" in classes(c) or "elementor-widget-wrap" in classes(c)]
        # Repeated "image/icon + title + text" children become a card grid.
        if len(child_containers) >= 2:
            cards = [self.as_card(c) for c in child_containers]
            if all(cards) and len(cards) == len(kids):
                return [{"type": "cards", "items": cards}]
        blocks: list[dict] = []
        for c in kids:
            blocks.extend(self.container(c, depth + 1))
        return blocks

    def as_card(self, node) -> dict | None:
        widgets = node.css("[data-widget_type]")
        kinds = [w.attrib.get("data-widget_type") for w in widgets if w.attrib.get("data-widget_type") not in SKIP_WIDGETS]
        if not kinds or len(kinds) > 5:
            return None
        if any(k in {"accordion.default", "eael-data-table.default", "image-carousel.default", "html.default",
                     "toggle.default", "video.default"} for k in kinds):
            return None
        heads = [k for k in kinds if "heading" in k or "icon-box" in k or "image-box" in k]
        imgs = node.css("img")
        if len(heads) != 1 or len(imgs) > 1:
            return None
        if len(text_of(node)) > 900 or node.css("table"):
            return None
        if not imgs and "icon-box" not in heads[0]:
            return None
        c = self.card(node)
        return c if c["title"] else None

    def section_bg(self, node) -> str:
        did = node.attrib.get("data-id")
        if did and did in self.bgs:
            return self.img(self.bgs[did], 2000)
        style = node.attrib.get("style", "")
        m = re.search(r'background-image:\s*url\(["\']?([^"\')]+)', style)
        return self.img(m.group(1), 2000) if m else ""


def merge_cards(blocks: list[dict]) -> list[dict]:
    out: list[dict] = []
    for b in blocks:
        if b["type"] == "card":
            if out and out[-1]["type"] == "cards":
                out[-1]["items"].append(b)
            else:
                out.append({"type": "cards", "items": [b]})
        else:
            out.append(b)
    # a single card is just content
    flat: list[dict] = []
    for b in out:
        if b["type"] == "cards" and len(b["items"]) == 1:
            c = b["items"][0]
            if c["image"]:
                flat.append({"type": "image", "src": c["image"], "alt": c["title"]})
            if c["title"]:
                flat.append({"type": "heading", "level": 3, "text": c["title"]})
            if c["html"]:
                flat.append({"type": "text", "html": c["html"]})
        else:
            flat.append(b)
    return flat


def dedupe(blocks: list[dict]) -> list[dict]:
    out, last = [], None
    for b in blocks:
        key = json.dumps(b, sort_keys=True)
        if key != last:
            out.append(b)
        last = key
    return out


# ---------------------------------------------------------------- pages

def page_title(page) -> str:
    t = page.css("title")
    return re.sub(r"\s+[-–|]\s+Gujarat Alkalies.*$", "", text_of(t[0])) if t else ""


def extract_page(path: Path, url: str, images: Images, bgs: dict[str, str]) -> dict | None:
    page = Selector(path.read_text(encoding="utf-8"), url=url)
    docs = [d for d in page.css("[data-elementor-type]")
            if d.attrib.get("data-elementor-type") in {"wp-page", "wp-post", "single-post", "single-page", "single"}]
    ex = Extractor(images, bgs, url)
    sections = []
    if docs:
        doc = docs[0]
        tops = [c for c in doc.children if c.tag in ("div", "section")]
        if len(tops) == 1 and "elementor-inner" in classes(tops[0]):
            tops = tops[0].css(".elementor-section-wrap > section, .elementor-section-wrap > div") or tops
        for top in tops:
            if is_hidden(top):
                continue
            blocks = dedupe(merge_cards(ex.container(top)))
            if blocks:
                sections.append({"bg": ex.section_bg(top), "blocks": blocks})
    else:
        # Theme (non-Elementor) templates: news posts, team profiles, services.
        main = next((m for sel in (".post-content", ".team-content", ".content-wrapper .content") if (m := page.css(sel))), None)
        if main:
            blocks = [b for b in ex.generic(main[0]) if not (b["type"] == "image" and re.search(r"logo", b["src"], re.I))]
            featured = page.css(".post-media img, .single-post .wp-post-image, .post-thumbnail img")
            if featured and (src := images(img_src(featured[0]))):
                blocks.insert(0, {"type": "image", "src": src, "alt": clean(featured[0].attrib.get("alt"))})
            heading = page.css(".single-post h1, .post-title, h1.entry-title")
            if heading and not any(b["type"] == "heading" for b in blocks[:2]):
                blocks.insert(1 if blocks and blocks[0]["type"] == "image" else 0,
                              {"type": "heading", "level": 1, "text": text_of(heading[0])})
            date = page.css(".post-meta-date, time, .post-date")
            if date and text_of(date[0]):
                blocks.insert(0, {"type": "eyebrow", "text": text_of(date[0])})
            blocks = dedupe(merge_cards(blocks))
            if sum(len(json.dumps(b)) for b in blocks) < 400:
                blocks = []
            if blocks:
                sections.append({"bg": "", "blocks": blocks})
    if not sections:
        return None
    hero = ""
    first = sections[0]["blocks"]
    if first and first[0]["type"] == "image":
        hero = first.pop(0)["src"]
        if not first:
            sections.pop(0)
    meta = page.css('meta[name="description"]')
    return {
        "title": page_title(page),
        "description": meta[0].attrib.get("content", "") if meta else "",
        "hero": hero,
        "sections": sections,
    }


SKIP_SLUG = re.compile(r"^(\d{4}__\d{2}__\d{2}|category__.*|gacl-news__[0-9a-f]{8}|home)$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "site/src/content"))
    ap.add_argument("--public", default=str(ROOT / "site/public"))
    args = ap.parse_args()
    out = Path(args.out)
    (out / "pages").mkdir(parents=True, exist_ok=True)
    images = Images(Path(args.public))
    bgs = load_backgrounds()
    sitemap = json.loads(SITEMAP.read_text())
    written = 0
    for url, info in sitemap.items():
        if info.get("status") != 200 or "/wp-content/" in url:
            continue
        slug = info["slug"]
        if SKIP_SLUG.match(slug):
            continue
        data = extract_page(PAGES / f"{slug}.html", url, images, bgs)
        if not data:
            print(f"  - no content: {slug}")
            continue
        data["slug"] = slug
        data["path"] = urlparse(url).path.rstrip("/") + "/"
        (out / "pages" / f"{slug}.json").write_text(json.dumps(data, indent=1, ensure_ascii=False))
        written += 1
    print(f"{written} pages, {len(images.map)} images")
    (out / "_images.json").write_text(json.dumps(images.map, indent=1))


if __name__ == "__main__":
    main()
