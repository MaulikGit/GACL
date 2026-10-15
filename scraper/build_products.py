"""Turn the crawled product-group pages into structured product data.

Reads scrape/output/pages/<group>.html and writes site/src/data/products.json:
one entry per product group, each with its products' specification tables,
caution notes, applications and leaflet/MSDS links.

Usage:
    python scraper/build_products.py [--pages scrape/output/pages] [--out site/src/data/products.json]
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scrapling.parser import Selector

GROUP_SLUGS = [
    "caustic-soda-group",
    "caustic-potash-group",
    "chlorotoluene-group",
    "hydrogen-peroxide-group",
    "special-chlorine-derivative-group",
    "chloromethane-group",
    "water-treatment-group",
    "sodium-chlorate-group",
    "phosphoric-group",
    "hydrazine-hydrate",
]
SECTION_WORDS = {"specifications", "specification", "applications", "application", "uses"}
STOP_HEADINGS = {"striving for change", "company", "materials & services", "quick links", "enquire now"}


def clean(text: str | None) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    # "Na 2 SO 4" -> "Na2SO4" style chemical formulae inside parentheses
    return re.sub(r"(?<=[A-Za-z]) (\d+)(?= |\)|$)", r"\1", text)


def text_of(el) -> str:
    return clean(el.get_all_text(separator=" ", strip=True))


def parse_group(path: Path, slug: str) -> dict:
    page = Selector(path.read_text(encoding="utf-8"), url=f"https://gacl.com/{slug}/")
    nodes = page.xpath(
        "//h1|//h2|//h3|//h4|//table|//li|//p"
        "|//div[contains(@class,'elementor-widget-text-editor')]"
        "|//a[contains(translate(@href,'PDF','pdf'),'.pdf')]"
    )
    title = ""
    products: list[dict] = []
    current: dict | None = None
    mode = None
    seen_text: set[str] = set()

    for node in nodes:
        tag = node.tag
        txt = text_of(node)
        low = txt.lower()
        if tag in ("h1", "h2", "h3", "h4"):
            if not txt or low.startswith(("gstin", "this website", "vadodara complex", "dahej complex")):
                continue
            if low in STOP_HEADINGS:
                if current:
                    break
                continue
            if not title and "group" in low or (not title and slug.split("-")[0] in low):
                title = txt
                continue
            if low in SECTION_WORDS:
                mode = "apps" if low.startswith(("appl", "uses")) else "spec"
                continue
            if txt == title:
                continue
            current = {"name": txt, "specs": [], "caution": "", "applications": [], "documents": []}
            products.append(current)
            mode = None
            seen_text = set()
            continue
        if current is None:
            continue
        if tag == "table":
            rows = [[text_of(c) for c in tr.css("th, td")] for tr in node.css("tr")]
            rows = [r for r in rows if any(r)]
            if rows:
                current["specs"].append(rows)
            continue
        if tag == "a":
            href = node.attrib.get("href", "")
            label = txt or Path(href).stem
            if href and all(d["url"] != href for d in current["documents"]):
                current["documents"].append({"label": label, "url": page.urljoin(href)})
            continue
        if not txt or txt in seen_text:
            continue
        if low.startswith("caution"):
            current["caution"] = re.sub(r"^caution\s*:?\s*", "", txt, flags=re.I)
            seen_text.add(txt)
            continue
        if mode == "apps" and tag in ("li", "p"):
            if low.startswith(("download", "leaflet", "msds", "enquiry", "major consuming")):
                continue
            if len(txt) < 120:
                current["applications"].append(txt)
                seen_text.add(txt)

    return {"slug": slug, "title": title, "products": products}


def tidy_formula(text: str) -> str:
    """'Na2 SO4 )' -> 'Na2SO4)', 'C6 H5 CH2 Cl' -> 'C6H5CH2Cl'."""
    text = re.sub(r"(?<=\d) (?=[A-Z.(])", "", text)
    text = re.sub(r"(?<=[A-Za-z0-9]) \)", ")", text)
    return re.sub(r" \.", ".", text)


def display_name(name: str) -> str:
    name = tidy_formula(name)
    head, sep, tail = name.partition("(")
    if head.isupper():
        head = " ".join(w if len(w) <= 3 and w.isalpha() and w in {"SBP", "HH", "CP", "BCL", "BOH"} else w.capitalize()
                        for w in head.split())
        head = head + (" " if sep else "")
    return (head.rstrip() + " " + sep + tail).strip() if sep else head.strip()


def finalize(groups: list[dict]) -> list[dict]:
    """Remove template blocks the site repeats on every product page."""
    # Hydrochloric acid and the caustic soda leaflet are a hidden block on every
    # group page; they belong to the caustic soda group only.
    stray_doc = "CAUSTIC-SODA-LYE.pdf"
    for group in groups:
        merged: dict[str, dict] = {}
        for product in group["products"]:
            name = display_name(product["name"])
            if name.lower().startswith("specifications") and group["slug"] == "water-treatment-group":
                name = "Poly Aluminium Chloride (PAC)"
                product["note"] = "Specifications as per IS 15573:2018"
            if name.startswith("Hydrochloric Acid") and group["slug"] != "caustic-soda-group":
                continue
            if group["slug"] != "caustic-soda-group":
                product["documents"] = [d for d in product["documents"] if not d["url"].endswith(stray_doc)]
            product["name"] = name
            product["specs"] = [[[tidy_formula(c) for c in row] for row in table] for table in product["specs"]]
            product["applications"] = list(dict.fromkeys(product["applications"]))
            if name in merged:
                # keep whichever duplicate actually carries content
                if not merged[name]["specs"] and product["specs"]:
                    merged[name] = product
                continue
            merged[name] = product
        group["products"] = [p for p in merged.values() if p["specs"] or p["applications"]]
    return groups


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", default="scrape/output/pages")
    parser.add_argument("--out", default="site/src/data/products.json")
    args = parser.parse_args()

    groups = []
    for slug in GROUP_SLUGS:
        path = Path(args.pages) / f"{slug}.html"
        if not path.exists():
            print(f"missing {path}")
            continue
        groups.append(parse_group(path, slug))
    groups = finalize(groups)
    for group in groups:
        print(f"{group['slug']}: {[p['name'] for p in group['products']]}")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(groups, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
