"""Extract the dealer network and open tenders from the crawled pages.

Writes site/src/data/dealers.json and site/src/data/tenders.json.

Usage:
    python scraper/build_directory.py [--pages scrape/output/pages] [--out site/src/data]
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from scrapling.parser import Selector


def clean(text: str | None) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def text_of(el) -> str:
    return clean(el.get_all_text(separator=" ", strip=True))


def dealers(pages: Path) -> list[dict]:
    page = Selector((pages / "dealer-network.html").read_text(encoding="utf-8"))
    regions: list[dict] = []
    region = "Direct Sales & Other States"
    for node in page.xpath("//h1|//h2|//h3|//h4|//h5|//h6|//p|//table"):
        txt = text_of(node)
        if node.tag != "table":
            m = re.match(r"^(REGION|STATE|COUNTRY)\s*:?\s*(.+)$", txt, re.I)
            if m:
                region = m.group(2).title().replace(" / ", " / ")
            elif node.tag.startswith("h") and re.search(r"export|international", txt, re.I):
                region = "Export & Direct Sales"
            continue
        rows = [[text_of(c) for c in tr.css("td, th")] for tr in node.css("tr")]
        head, body = rows[0], [r for r in rows[1:] if any(r)]
        phone_col = next((i for i, h in enumerate(head) if "phone" in h.lower()), None)
        mail_col = next((i for i, h in enumerate(head) if "mail" in h.lower() or "url" in h.lower()), len(head) - 1)
        entries = []
        for r in body:
            address = r[0]
            m = re.search(r"\b(M/s\.?|Mr\.|Ms\.|Mrs\.|Shri)\s", address)
            contact = address[m.start():].strip() if m else ""
            address = address[: m.start()].strip() if m else address
            raw = r[mail_col] if mail_col < len(r) else ""
            emails = re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", raw)
            urls = [u for u in re.findall(r"(?:https?://)?www\.[\w.-]+", raw)]
            entries.append({
                "details": address.rstrip(", "),
                "contact": contact,
                "phone": r[phone_col] if phone_col is not None and phone_col < len(r) else "",
                "emails": emails,
                "website": urls[0] if urls else "",
            })
        if regions and regions[-1]["region"] == region:
            regions[-1]["dealers"].extend(entries)
        else:
            regions.append({"region": region, "dealers": entries})
    return regions


SMALL = {"of", "for", "the", "and", "in", "on", "at", "to", "under", "by", "a", "an", "or"}
KEEP = {"MW", "KW", "SPV", "EOI", "RE", "GACL", "GNAL", "HVAC", "IT", "PAC", "RFQ", "RFP"}


def title_case(text: str) -> str:
    words = text.rstrip(".").split()
    out = []
    for i, w in enumerate(words):
        if w.upper() in KEEP:
            out.append(w.upper())
        elif i and w.lower() in SMALL:
            out.append(w.lower())
        else:
            out.append(w.capitalize())
    return " ".join(out)


def tenders(pages: Path) -> list[dict]:
    page = Selector((pages / "tenders.html").read_text(encoding="utf-8"), url="https://gacl.com/tenders/")
    out = []
    for table in page.css("table"):
        for tr in table.css("tr")[1:]:
            cells = tr.css("td")
            if len(cells) < 4:
                continue
            out.append({
                "title": title_case(text_of(cells[1])),
                "open": text_of(cells[2]),
                "close": text_of(cells[3]),
                "documents": [
                    {"label": clean(a.get_all_text()) or "Document", "url": page.urljoin(a.attrib.get("href", ""))}
                    for a in (cells[4].css("a[href]") if len(cells) > 4 else [])
                ],
            })
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", default="scrape/output/pages")
    parser.add_argument("--out", default="site/src/data")
    args = parser.parse_args()
    pages, out = Path(args.pages), Path(args.out)
    d = dealers(pages)
    t = tenders(pages)
    (out / "dealers.json").write_text(json.dumps(d, indent=2, ensure_ascii=False))
    (out / "tenders.json").write_text(json.dumps(t, indent=2, ensure_ascii=False))
    print(f"{sum(len(r['dealers']) for r in d)} dealers in {len(d)} regions: {[r['region'] for r in d]}")
    print(f"{len(t)} tenders")


if __name__ == "__main__":
    main()
