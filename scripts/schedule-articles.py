#!/usr/bin/env python3
"""
Finch Theory — Article scheduler.

Assign publication dates to articles in insights/.
Runs locally from the repo root:
    py scripts\\schedule-articles.py

CONFIGURATION:
    Edit START_FROM (date the first article publishes).
    Edit ARTICLE_ORDER (filenames in desired release order).
    Or use SCHEDULE for per-file specific dates.
"""

import re
import sys
from datetime import date, timedelta
from pathlib import Path


# ============================================================
# CONFIGURATION — edit these
# ============================================================

# Start date — will advance to next publish day if needed
START_FROM = date(2026, 6, 17)

# Order in which to publish (Tue/Thu cadence starting from START_FROM).
ARTICLE_ORDER = [
    "social-capital-and-the-shrinking-professional-network.html",
    "the-referral-gap.html",
    "generational-financial-pressure-at-work.html",
    "what-referral-data-tells-us-about-relationship-capital.html",
]

# Optional: override specific files to specific dates
SCHEDULE = {}  # e.g. {"article.html": "2026-08-05"}

# Publish days: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri
PUBLISH_DAYS = [1, 3]  # Tuesday and Thursday

POSTS_DIR = Path("insights")


# ============================================================
# Helpers
# ============================================================

def format_display(d):
    return f"{d.day} {d.strftime('%B')} {d.year}"

def next_publish_day(start, publish_days):
    d = start
    while d.weekday() not in publish_days:
        d += timedelta(days=1)
    return d

def generate_dates(start, count, publish_days):
    dates = []
    d = next_publish_day(start, publish_days)
    for _ in range(count):
        dates.append(d)
        d += timedelta(days=1)
        d = next_publish_day(d, publish_days)
    return dates

def update_dates_in_file(path, target_date):
    html = path.read_text(encoding="utf-8")
    original = html
    target_iso = target_date.isoformat()
    target_full = f"{target_iso}T08:00:00+00:00"
    target_display = format_display(target_date)
    messages = []

    # JSON-LD datePublished
    json_pat = re.compile(r'("datePublished"\s*:\s*")([^"]+)(")')
    m = json_pat.search(html)
    if m:
        old_iso = m.group(2)[:10]
        if old_iso != target_iso:
            html = json_pat.sub(f'\\g<1>{target_full}\\g<3>', html, count=1)
            messages.append(f"JSON-LD: {old_iso} → {target_iso}")

    # Byline "Published DD Month YYYY"
    byline_pat = re.compile(r'(Published\s+)(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})')
    m = byline_pat.search(html)
    if m:
        old_display = m.group(2)
        if old_display != target_display:
            html = byline_pat.sub(f'\\g<1>{target_display}', html, count=1)
            messages.append(f"Byline: {old_display} → {target_display}")

    if html != original:
        path.write_text(html, encoding="utf-8")
        return True, messages
    return False, []


# ============================================================
# Main
# ============================================================

def main():
    repo_root = Path(__file__).resolve().parent.parent
    posts_dir = repo_root / POSTS_DIR

    if not posts_dir.exists():
        sys.stderr.write(f"Insights directory not found: {posts_dir}\n")
        return 1

    print(f"Finch Theory — Article Scheduler")
    print(f"Starting from: {format_display(START_FROM)}")
    print(f"Publishing on: {[['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][d] for d in PUBLISH_DAYS]}")
    print()

    sequential_dates = generate_dates(START_FROM, len(ARTICLE_ORDER), PUBLISH_DAYS)
    final_schedule = {fn: d for fn, d in zip(ARTICLE_ORDER, sequential_dates)}
    for fn, iso_str in SCHEDULE.items():
        final_schedule[fn] = date.fromisoformat(iso_str)

    print(f"{'Filename':<60} {'Date':<20} {'Status'}")
    print("-" * 90)

    for filename, target_date in sorted(final_schedule.items(), key=lambda x: x[1]):
        path = posts_dir / filename
        if not path.exists():
            print(f"{filename:<60} {format_display(target_date):<20} FILE NOT FOUND")
            continue
        changed, messages = update_dates_in_file(path, target_date)
        if changed:
            status = "Updated: " + "; ".join(messages)
        else:
            status = "No change needed"
        print(f"{filename:<60} {format_display(target_date):<20} {status}")

    print()
    print("Done. Commit and push to deploy.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
