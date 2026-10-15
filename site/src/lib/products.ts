// Product specifications imported from gacl.com by scraper/build_products.py.
import raw from "../data/products.json";
import { home } from "./content";

export type Product = {
  name: string;
  specs: string[][][];
  caution: string;
  applications: string[];
  documents: { label: string; url: string }[];
  note?: string;
};
export type Group = { slug: string; title: string; image: string; products: Product[] };

const cards: { title: string; href: string; image: string }[] = home.products?.items ?? [];
const imageFor = (slug: string) => cards.find((c) => c.href.replace(/\//g, "") === slug)?.image ?? "";

export const groups: Group[] = (raw as { slug: string; title: string; products: Product[] }[]).map((g) => ({
  slug: g.slug,
  title: g.title,
  image: imageFor(g.slug),
  products: g.products,
}));

export const productSlug = (name: string) =>
  name.toLowerCase().replace(/\(.*?\)/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

export function splitName(name: string) {
  const m = name.match(/^(.*?)\s*\((.+)\)\s*(.*)$/);
  if (!m) return { base: name, formula: "" };
  return { base: (m[1] + (m[3] ? " " + m[3] : "")).trim(), formula: m[2].replace(/\)\s*\(/g, " · ") };
}
