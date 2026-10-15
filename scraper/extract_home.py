"""Extract the gacl.com homepage, menu and footer into structured content.

Writes site/src/content/home.json, nav.json and footer.json. Text is kept as
published; images go through the same WebP pipeline as extract_pages.py.

Usage:
    python scraper/extract_home.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from scrapling.parser import Selector

from extract_pages import ROOT, Images, clean, img_src, inline_html, rewrite_link, text_of

PAGES = ROOT / "scrape/output/pages"
OUT = ROOT / "site/src/content"


def first(el, sel):
    found = el.css(sel)
    return found[0] if found else None


def t(el, sel) -> str:
    node = first(el, sel)
    return text_of(node) if node else ""


def bg_url(el) -> str:
    m = re.search(r"url\(([^)]+)\)", el.attrib.get("data-bg-image", "") or el.attrib.get("style", ""))
    return m.group(1).strip("'\"") if m else ""


def home(images: Images) -> dict:
    page = Selector((PAGES / "home.html").read_text(encoding="utf-8"), url="https://gacl.com/")
    doc = first(page, '[data-elementor-type="wp-page"]')

    slides = []
    for sl in doc.css(".banner_slider"):
        img = first(sl, "img.desktop_image") or first(sl, "img")
        p = first(sl, "p.lightText")
        if not p:
            continue
        lead = next((c for c in p.children if c.tag in ("span", "strong")), None)
        html = inline_html(p)
        if lead is not None and "<br>" in html and not first(p, "a"):
            title = text_of(lead)
            sub = clean(re.sub(r"<[^>]+>", " ", html).replace(title, "", 1))
            slides.append({"image": images(img_src(img), 2400) if img else "", "title": title, "text": sub, "html": ""})
        else:
            slides.append({"image": images(img_src(img), 2400) if img else "", "title": "", "text": "", "html": html})

    figures_heading = t(doc, ".about_heading")
    figures = []
    for card in doc.css(".about_wrapper_cards_inner"):
        img = first(card, "img")
        h2 = first(card, "h2")
        count = first(card, ".count")
        figures.append({
            "icon": images(img_src(img), 300) if img else "",
            "value": text_of(count) if count else "",
            "title": text_of(h2) if h2 else "",
            "html": inline_html(first(card, "p")) if first(card, "p") else "",
        })

    company = {}
    for sec in doc.css("section"):
        if sec.css("a.video_link"):
            box = first(sec, ".left_right_image_content_image")
            content = first(sec, ".left_right_image_content_content") or sec
            link = first(content, "a[href]")
            company = {
                "image": images(bg_url(box), 1600) if box is not None else "",
                "badge": t(sec, ".big_text"),
                "video": first(sec, "a.video_link").attrib.get("href", ""),
                "eyebrow": t(content, ".title h3, h3"),
                "paragraphs": [inline_html(p) for p in content.css("p") if text_of(p)],
                "link": rewrite_link(link.attrib.get("href", "")) if link else "",
            }
            break

    products_block = first(doc, ".our_product")
    product_wrappers = products_block.css(".our_product_wrapper") if products_block else []
    products = {}
    clients = {}
    if product_wrappers:
        pw = product_wrappers[0]
        products = {
            "title": t(pw, ".our_product_heading"),
            "subtitle": t(pw, ".small_heading"),
            "text": inline_html(first(pw, "p")) if first(pw, "p") else "",
            "items": [
                {
                    "title": t(g, ".product_title"),
                    "href": rewrite_link(first(g, "a").attrib.get("href", "")),
                    "image": images(img_src(first(g, "img")), 1000),
                }
                for g in pw.css(".our_product_inner_group_wrapper")
            ],
        }
    if products_block:
        cw = product_wrappers[1] if len(product_wrappers) > 1 else products_block
        seen, logos = set(), []
        group_imgs = {img_src(i) for i in products_block.css(".our_product_inner_group_wrapper img")}
        for img in products_block.css("img"):
            if img_src(img) in group_imgs:
                continue
            src = images(img_src(img), 400)
            if src and src not in seen and "arrow" not in src.lower():
                seen.add(src)
                logos.append({"src": src, "alt": clean(img.attrib.get("alt"))})
        clients = {"title": t(cw, ".our_product_heading"), "logos": logos}

    green = {}
    gc = first(doc, "section.green_cards")
    if gc:
        cols = gc.css(".fl-col")
        intro = cols[0] if cols else gc
        btn = first(intro, "a")
        green = {
            "title": t(intro, "h2"),
            "subtitle": t(intro, "h4"),
            "text": inline_html(first(intro, "p")) if first(intro, "p") else "",
            "cta": {"text": text_of(btn), "href": rewrite_link(btn.attrib.get("href", ""))} if btn else None,
            "cards": [
                {
                    "image": images(img_src(first(c, "img")), 1200) if first(c, "img") else "",
                    "title": t(c, "h4"),
                    "text": inline_html(first(c, "p")) if first(c, "p") else "",
                }
                for c in cols[1:]
                if t(c, "h4") and first(c, "img")
            ],
        }
        seen_titles = set()
        green["cards"] = [c for c in green["cards"] if not (c["title"] in seen_titles or seen_titles.add(c["title"]))]

    services = {}
    st = first(doc, ".services_main-title")
    if st:
        sec = first(doc, ".service_main-card")
        cards, photos = [], []
        for cards_row in sec.css(".service_cards"):
            for item in cards_row.children:
                if item.tag != "div":
                    continue
                body = first(item, ".service_card-body")
                if body:
                    icon = first(body, "img")
                    link = first(body, "a")
                    cards.append({
                        "icon": images(img_src(icon), 200) if icon else "",
                        "title": t(body, ".service_card-title"),
                        "text": t(body, ".service_card-text"),
                        "href": rewrite_link(link.attrib.get("href", "")) if link else "",
                        "cta": text_of(link) if link else "",
                    })
                else:
                    img = first(item, "img")
                    if img:
                        photos.append(images(img_src(img), 1200))
        for i, c in enumerate(cards):
            c["image"] = photos[i] if i < len(photos) else ""
        services = {"title": text_of(st), "cards": cards}

    media = {}
    ms = first(doc, "section.media")
    if ms:
        media = {
            "title": t(ms, ".media_title"),
            "items": [
                {
                    "image": images(img_src(first(c, "img")), 1200) if first(c, "img") else "",
                    "label": t(c, ".gaclnews"),
                    "title": t(c, ".card-content1"),
                    "date": t(c, ".date"),
                    "href": rewrite_link(first(c, "a").attrib.get("href", "")) if first(c, "a") else "",
                    "cta": t(c, "a"),
                }
                for c in ms.css(".card1")
            ],
        }

    testimonials = {}
    ts = first(doc, "section.left_right_image_with_content_slider")
    if ts:
        testimonials = {
            "title": t(ts, ".right_heading"),
            "items": [
                {
                    "image": images(img_src(first(w, "img")), 800) if first(w, "img") else "",
                    "name": t(w, ".text_slider_text_top_title"),
                    "role": t(w, ".text_slider_text_top_text"),
                    "quote": t(w, ".text_slider_text_message"),
                }
                for w in ts.css(".text_slider_wrapper")
            ],
        }

    investor = {}
    inf = first(doc, "section.information")
    if inf:
        ps = inf.css(".infosection p")
        links = [{"text": text_of(a), "href": rewrite_link(a.attrib.get("href", ""))} for a in inf.css("a[href]")]
        investor = {
            "title": inline_html(ps[0]) if ps else "",
            "text": text_of(ps[1]) if len(ps) > 1 else "",
            "links": links,
        }

    quick = []
    for c in doc.css("section.lastSec .card4"):
        a = first(c, "a")
        quick.append({
            "icon": images(img_src(first(c, "img")), 200) if first(c, "img") else "",
            "title": t(c, "h2"),
            "text": t(c, "p"),
            "cta": text_of(a) if a else "",
            "href": rewrite_link(a.attrib.get("href", "")) if a else "",
        })

    notice = first(page, ".elementor-element-cff8344 a")
    return {
        "notice": {"text": t(page, ".elementor-element-cff8344"), "href": notice.attrib.get("href", "")} if notice else None,
        "slides": slides,
        "figures": {"title": figures_heading, "items": figures},
        "company": company,
        "products": products,
        "clients": clients,
        "green": green,
        "services": services,
        "media": media,
        "testimonials": testimonials,
        "investor": investor,
        "quick": quick,
    }


def nav() -> list[dict]:
    data = json.loads((ROOT / "scrape/output/navigation.json").read_text())
    def fix(items):
        return [{"label": i["label"], "href": rewrite_link(i["url"]), "children": fix(i.get("children", []))} for i in items]
    return fix(data)


def footer(images: Images) -> dict:
    page = Selector((PAGES / "home.html").read_text(encoding="utf-8"), url="https://gacl.com/")
    foot = first(page, '[data-elementor-type="footer"]')
    columns, sites = [], []
    for h in foot.css("h1, h2, h3, h4, h5, h6"):
        title = text_of(h)
        if not title:
            continue
        # Each heading is followed (in its widget column) by a menu or an address block.
        col = h.parent
        for _ in range(4):
            if col is None:
                break
            if col.css("ul li a") or len(text_of(col)) > len(title) + 20:
                break
            col = col.parent
        if col is None:
            continue
        links = [{"text": text_of(a), "href": rewrite_link(a.attrib.get("href", ""))}
                 for a in col.css("ul li a") if text_of(a)]
        if links:
            columns.append({"title": title, "links": links})
        elif title.isupper() and "COMPLEX" in title:
            body = clean(text_of(col).replace(title, "", 1))
            sites.append({"title": title, "text": body})
    legal = [text_of(p) for p in foot.css("p, .elementor-heading-title") if re.search(r"GSTIN|website belongs|©|\b20\d\d\b", text_of(p))]
    socials = [{"href": a.attrib.get("href", ""), "label": (a.attrib.get("aria-label") or text_of(a) or "").strip()}
               for a in foot.css(".elementor-social-icon, a[class*=social]") if a.attrib.get("href")]
    # Deduplicate columns rendered twice for mobile.
    uniq = {}
    for c in columns:
        uniq.setdefault(c["title"], c)
    # Address headings share one container; split its text at each heading.
    titles = list(dict.fromkeys(x["title"] for x in sites))
    blob = clean(text_of(foot))
    usites = {}
    for i, title in enumerate(titles):
        start = blob.find(title)
        if start < 0:
            continue
        start += len(title)
        end = min([blob.find(m, start) for m in titles[i + 1:] + ["GSTIN"] if blob.find(m, start) > 0] or [len(blob)])
        usites[title] = {"title": title, "text": blob[start:end].strip()}
    legal_seen, legal_out = set(), []
    for line in legal:
        key = re.sub(r"[^A-Z0-9]", "", line.upper())
        if key not in legal_seen:
            legal_seen.add(key)
            legal_out.append(line)
    legal = legal_out
    return {"columns": list(uniq.values()), "sites": list(usites.values()),
            "legal": legal, "social": socials}


def main():
    images = Images(ROOT / "site/public")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "home.json").write_text(json.dumps(home(images), indent=1, ensure_ascii=False))
    (OUT / "nav.json").write_text(json.dumps(nav(), indent=1, ensure_ascii=False))
    (OUT / "footer.json").write_text(json.dumps(footer(images), indent=1, ensure_ascii=False))
    print("home, nav, footer written")


if __name__ == "__main__":
    main()
