#!/usr/bin/env python3
"""
Finch Theory — Sitemap generator.

Scans the repo for all .html files and writes a fresh sitemap.xml.
Future-dated articles (datePublished > today) are excluded.

Run from repo root:
    py generate-sitemap.py

Or with an explicit path:
    py generate-sitemap.py C:\\Repos\\Finch Theory
"""

from __future__ import annotations
import re
import sys
from datetime import date, datetime
from pathlib import Path

BASE_URL = "https://finchtheory.com"

EXCLUDE_NAMES = {
    "404.html",
    "privacy.html",
}

EXCLUDE_DIRS = {
    ".git",
    ".github",
    "node_modules",
    "scripts",
    "docs",
}

def get_date_from_html(path: Path) -> date | None:
    """Extract datePublished from JSON-LD if present."""
    try:
        html = path.read_text(encoding="utf-8")
        m = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})', html)
        if m:
            return date.fromisoformat(m.group(1))
    except Exception:
        pass
    return None

def classify(rel: Path):
    """Return (priority, changefreq) for a given relative path."""
    name = rel.name
    parts = rel.parts

    if rel == Path("index.html"):
        return 1.0, "weekly"
    if len(parts) == 1:
        # Top-level pages
        return 0.7, "monthly"
    if parts[0] == "insights":
        return 0.8, "monthly"
    return 0.5, "monthly"

def scan(repo_root: Path) -> list[dict]:
    today = date.today()
    urls = []

    for path in sorted(repo_root.rglob("*.html")):
        rel = path.relative_to(repo_root)

        # Skip excluded dirs
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue

        # Skip excluded files
        if rel.name in EXCLUDE_NAMES:
            continue

        # Skip future-dated articles
        pub_date = get_date_from_html(path)
        if pub_date and pub_date > today:
            print(f"  Skipping (future): {rel}")
            continue

        # Build URL
        if rel.name == "index.html" and len(rel.parts) == 1:
            url = f"{BASE_URL}/"
        else:
            url = f"{BASE_URL}/{rel.as_posix()}"

        lastmod = pub_date.isoformat() if pub_date else today.isoformat()
        priority, changefreq = classify(rel)

        urls.append({
            "url": url,
            "lastmod": lastmod,
            "changefreq": changefreq,
            "priority": priority,
        })

    return urls

def build_xml(urls: list[dict]) -> str:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in sorted(urls, key=lambda x: (-x["priority"], x["url"])):
        lines.append("  <url>")
        lines.append(f"    <loc>{u['url']}</loc>")
        lines.append(f"    <lastmod>{u['lastmod']}</lastmod>")
        lines.append(f"    <changefreq>{u['changefreq']}</changefreq>")
        lines.append(f"    <priority>{u['priority']:.1f}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"

def main():
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1])
    else:
        repo_root = Path(__file__).resolve().parent

    print(f"Finch Theory — Sitemap Generator")
    print(f"Root: {repo_root}")
    print()

    urls = scan(repo_root)
    xml = build_xml(urls)

    out = repo_root / "sitemap.xml"
    out.write_text(xml, encoding="utf-8")

    print(f"\n✓ Written {len(urls)} URLs to sitemap.xml")
    for u in sorted(urls, key=lambda x: (-x["priority"], x["url"])):
        print(f"  {u['priority']:.1f}  {u['url']}")

if __name__ == "__main__":
    main()
