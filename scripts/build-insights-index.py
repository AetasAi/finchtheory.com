#!/usr/bin/env python3
"""
Finch Theory — Insights index auto-builder.

Scans insights/*.html, extracts metadata, and rebuilds the insights
section of index.html between markers:

    <!-- AUTO-INSIGHTS-START -->
    ...replaced automatically...
    <!-- AUTO-INSIGHTS-END -->

Articles with a datePublished in the FUTURE are excluded from the index.
This allows you to upload future-dated articles and have them appear
automatically on their scheduled date via the daily GitHub Action.

Run locally from repo root:
    py scripts\\build-insights-index.py

Per-article controls (optional, add to <head>):
    <meta name="ft-listed" content="false">    → hide from index
    <meta name="ft-service" content="Relationship Capital">
    <meta name="ft-type" content="Article">
"""

import json
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path


INSIGHTS_DIR = Path("insights")
INDEX_FILE = Path("index.html")

START_MARKER = "<!-- AUTO-INSIGHTS-START -->"
END_MARKER = "<!-- AUTO-INSIGHTS-END -->"


def extract_meta(html, name):
    m = re.search(rf'<meta\s+name="{re.escape(name)}"\s+content="([^"]*)"', html)
    return m.group(1).strip() if m else None

def extract_og(html, prop):
    m = re.search(rf'<meta\s+property="{re.escape(prop)}"\s+content="([^"]*)"', html)
    return m.group(1).strip() if m else None

def extract_json_ld_date(html):
    m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', html)
    if m:
        return m.group(1)[:10]
    return None

def extract_h1(html):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    return None

def extract_read_time(html):
    m = re.search(r'(\d+\s+min\s+read)', html)
    return m.group(1) if m else "5 min read"

def format_display_date(iso_str):
    d = date.fromisoformat(iso_str)
    return f"{d.day} {d.strftime('%B')} {d.year}"

def parse_articles(insights_dir):
    articles = []
    today = date.today()

    for path in sorted(insights_dir.glob("*.html")):
        if path.name == "index.html":
            continue
        html = path.read_text(encoding="utf-8")

        # Check if hidden
        listed = extract_meta(html, "ft-listed")
        if listed and listed.lower() == "false":
            continue

        # Date check — skip future articles
        pub_iso = extract_json_ld_date(html)
        if pub_iso:
            pub_date = date.fromisoformat(pub_iso)
            if pub_date > today:
                print(f"  Skipping (future): {path.name} — scheduled {pub_iso}")
                continue
        else:
            pub_iso = date.today().isoformat()
            pub_date = date.today()

        title = extract_h1(html) or extract_og(html, "og:title") or path.stem
        desc = extract_meta(html, "description") or extract_og(html, "og:description") or ""
        service = extract_meta(html, "ft-service") or "Insights"
        article_type = extract_meta(html, "ft-type") or "Article"
        read_time = extract_read_time(html)
        slug = path.name

        articles.append({
            "slug": slug,
            "title": title,
            "desc": desc,
            "service": service,
            "type": article_type,
            "read_time": read_time,
            "pub_date": pub_date,
            "pub_display": format_display_date(pub_iso),
        })

    # Newest first
    articles.sort(key=lambda a: a["pub_date"], reverse=True)
    return articles

def build_insight_rows(articles):
    if not articles:
        return '<p style="font-size:14px;color:var(--text-tertiary);padding:32px 0;">No articles published yet.</p>'

    rows = []
    for a in articles:
        row = f'''      <a href="/insights/{a["slug"]}" class="insight-row" style="text-decoration:none;display:grid;grid-template-columns:160px 1fr 180px;gap:40px;align-items:start;border-bottom:1px solid var(--mid-grey);padding:32px 0;transition:background 0.15s,padding 0.15s,margin 0.15s;" onmouseover="this.style.background='var(--warm-grey)';this.style.margin='0 -56px';this.style.padding='32px 56px';" onmouseout="this.style.background='';this.style.margin='';this.style.padding='32px 0';">
        <div><p class="insight-type">{a["type"]}</p><p class="insight-service">{a["service"]}</p></div>
        <div>
          <h3 class="insight-title">{a["title"]}</h3>
          <p class="insight-desc">{a["desc"]}</p>
        </div>
        <div class="insight-action"><span class="insight-time">{a["read_time"]}</span><span class="insight-read">Read article →</span></div>
      </a>'''
        rows.append(row)
    return "\n".join(rows)

def main():
    repo_root = Path(__file__).resolve().parent.parent
    insights_dir = repo_root / INSIGHTS_DIR
    index_path = repo_root / INDEX_FILE

    if not insights_dir.exists():
        sys.stderr.write(f"Insights directory not found: {insights_dir}\n")
        return 1
    if not index_path.exists():
        sys.stderr.write(f"index.html not found: {index_path}\n")
        return 1

    print("Finch Theory — Insights Index Builder")
    print(f"Scanning: {insights_dir}")
    print()

    articles = parse_articles(insights_dir)
    print(f"Found {len(articles)} published article(s)")
    for a in articles:
        print(f"  + {a['slug']} — {a['pub_display']}")

    rows_html = build_insight_rows(articles)

    index_html = index_path.read_text(encoding="utf-8")
    if START_MARKER not in index_html or END_MARKER not in index_html:
        sys.stderr.write(f"Markers not found in {INDEX_FILE}.\n")
        sys.stderr.write(f"Add these to the insights-list div:\n")
        sys.stderr.write(f"  {START_MARKER}\n  {END_MARKER}\n")
        return 1

    before = index_html[:index_html.index(START_MARKER) + len(START_MARKER)]
    after = index_html[index_html.index(END_MARKER):]
    new_index = before + "\n" + rows_html + "\n    " + after

    index_path.write_text(new_index, encoding="utf-8")
    print()
    print(f"✓ {INDEX_FILE} updated with {len(articles)} article(s).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
