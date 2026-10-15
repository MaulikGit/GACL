// Content imported from the crawl of gacl.com by scraper/extract_pages.py and
// scraper/extract_home.py. Text is kept exactly as published on the live site.
import navData from "../content/nav.json";
import footerData from "../content/footer.json";
import homeData from "../content/home.json";

export type Block =
  | { type: "heading"; level: number; text: string }
  | { type: "eyebrow"; text: string }
  | { type: "text"; html: string }
  | { type: "list"; ordered: boolean; items: string[] }
  | { type: "image"; src: string; alt: string; caption?: string; href?: string }
  | { type: "gallery"; images: { src: string; alt: string }[] }
  | { type: "cards"; items: Card[] }
  | { type: "table"; rows: string[][] }
  | { type: "accordion"; items: { title: string; blocks: Block[] }[] }
  | { type: "button"; text: string; href: string }
  | { type: "video"; url: string }
  | { type: "embed"; src: string }
  | { type: "stat"; value: string; suffix: string; label: string };

export type Card = { image: string; title: string; html: string; href: string; cta: string };
export type Section = { bg: string; blocks: Block[] };
export type Page = { slug: string; path: string; title: string; description: string; hero: string; sections: Section[] };
export type NavItem = { label: string; href: string; children: NavItem[] };

const modules = import.meta.glob<{ default: Page }>("../content/pages/*.json", { eager: true });
export const pages: Page[] = Object.values(modules).map((m) => m.default);
export const pageByPath = new Map(pages.map((p) => [p.path, p]));

export const nav = navData as NavItem[];
export const footer = footerData as {
  columns: { title: string; links: { text: string; href: string }[] }[];
  sites: { title: string; text: string }[];
  legal: string[];
  social: { href: string; label: string }[];
};
export const home = homeData as any;

/** Links to pages that exist in the new site stay local; anything else opens on gacl.com. */
export function href(link: string): string {
  if (!link) return "#";
  if (/^(https?:|mailto:|tel:|#)/.test(link)) return link;
  const path = link.split("?")[0].split("#")[0];
  if (path === "/" || pageByPath.has(path) || path === "/products/") return link;
  return `https://gacl.com${link}`;
}

export const isExternal = (link: string) => /^https?:/.test(href(link)) && !href(link).includes("://gacl.com/wp-content") ? true : /^https?:/.test(href(link));

export function plain(html: string): string {
  return html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
}

export function youtubeId(url: string): string | null {
  const m = url.match(/(?:youtu\.be\/|v=|embed\/)([\w-]{11})/);
  return m ? m[1] : null;
}
