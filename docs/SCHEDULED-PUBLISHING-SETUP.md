# Finch Theory — Scheduled Publishing System

Articles can be uploaded with **future dates** and will appear on the Insights section of the homepage automatically when their date arrives — Tuesday and Thursday cadence built in.

---

## What's in the system

| File | Location | Purpose |
|---|---|---|
| `build-insights-index.py` | `scripts/` | Rebuilds insights section — hides future-dated articles |
| `scheduled-publish.yml` | `.github/workflows/` | Daily 07:00 UK action — releases articles on schedule |
| `update-insights-index.yml` | `.github/workflows/` | Fires on push to `insights/*.html` — immediate rebuild |
| `schedule-articles.py` | `scripts/` | Helper — sets Tue/Thu dates on a batch of articles |

---

## How it works

**Two GitHub Actions, two jobs:**

**`update-insights-index.yml`** — fires when you push any file to `insights/`. Runs the indexer immediately. Use for articles you want live now.

**`scheduled-publish.yml`** — fires every day at 07:00 UK time. Articles whose `datePublished` is today or in the past get added to the index. Use for scheduled batches.

**The future-date filter:**

```
insights/
├── your-network-is-an-asset.html         (2026-06-06) ← live
├── the-referral-gap.html                 (2026-06-24) ← FUTURE, hidden until 24 Jun
└── generational-financial-pressure.html  (2026-07-01) ← FUTURE, hidden until 1 Jul
```

Article URLs still work directly when pushed — they just don't appear in the index until their date arrives.

---

## Day-to-day: scheduling a batch

1. Drop articles into `insights/`
2. Open `scripts/schedule-articles.py`, edit:
   ```python
   START_FROM = date(2026, 7, 1)   # First publish date
   ARTICLE_ORDER = [
       "first-article.html",
       "second-article.html",
   ]
   ```
3. Run from repo root:
   ```
   py scripts\schedule-articles.py
   ```
4. Commit and push

Articles will appear on the homepage automatically on their scheduled dates. **Remember to purge Cloudflare cache** on each publish day.

---

## Day-to-day: publish immediately

Set `datePublished` to today's date and push. The `update-insights-index.yml` action fires and adds it to the index within 60 seconds.

---

## Updating the sitemap

After adding articles, regenerate the sitemap:
```
py generate-sitemap.py
```
Commit and push `sitemap.xml`.

---

## Cloudflare cache reminder

**Always purge after pushing.** Cloudflare → finchtheory.com → Caching → Purge Everything.

For scheduled publish days, either purge manually in the morning or set a Cache Rule to reduce TTL on the homepage.

---

*Last updated: June 2026*
