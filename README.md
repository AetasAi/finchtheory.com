# Finch Theory

Commercial growth consultancy website for [finchtheory.com](https://finchtheory.com).

Built as a single self-contained HTML file. No framework, no build step, no dependencies.

## Deployment

Hosted on GitHub Pages with a custom domain. DNS configured at 123-reg.

## Structure

```
index.html   — full site, all assets embedded (mobile optimised)
CNAME        — custom domain for GitHub Pages
.nojekyll    — prevents Jekyll processing
robots.txt   — search and AI crawler directives
sitemap.xml  — sitemap submitted to Google Search Console
llms.txt     — AI discoverability (ChatGPT, Claude, Perplexity)
```

## Updating content

Edit `index.html` directly. Commit and push — the site updates within ~60 seconds.
