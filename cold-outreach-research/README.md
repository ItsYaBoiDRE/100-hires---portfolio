# Cold Outreach Pipeline for B2B SaaS — Research Repository

Research base for a future cold-outreach playbook, built from 10 high-signal practitioners (not aggregators).

## Why this topic

Cold outreach is the one B2B SaaS growth channel where the gap between average and expert execution is measurable in a single metric (positive reply rate), where practitioners publish their actual systems in public (Clay tables, sequences, real emails with results), and where my analytics background applies directly — a pipeline is a funnel with conversion rates at every stage, and that's a data problem.

## Why these 10 experts

A cold outreach pipeline has four layers, and most "follow these gurus" lists only cover the first one. This repo deliberately covers all four:

| Layer | Experts |
|---|---|
| Messaging & copy | Josh Braun, Will Allred, Florin Tatulea, Kyle Coleman |
| Cold calling & conversations | 30 Minutes to President's Club, Becc Holland |
| Systems & infrastructure (lists, deliverability, Clay, sequencing) | Eric Nowoslawski, Sam Nelson |
| Multichannel & training systems | Morgan J Ingram, Jason Bay |

Selection bar: every source actively practices outbound (rep, leader, or agency operator) and publishes first-hand, tactical material. Full annotations in [`research/sources.md`](research/sources.md).

## Repository structure

```
research/
  sources.md              # 10 experts, links, annotations, verification notes
  linkedin-posts/         # one folder per author; posts as dated .md files
  youtube-transcripts/    # one folder per author; one .md per video (metadata header)
  other/                  # newsletters, podcast notes, datasets, PDFs
scripts/
  fetch_youtube_transcripts.py   # youtube-transcript-api with Supadata fallback
  requirements.txt
docs/
  collection-workflow.md  # how content was collected + commit plan
```

## How content was collected

- **YouTube transcripts:** fetched with `scripts/fetch_youtube_transcripts.py` — tries the free `youtube-transcript-api` first, falls back to Supadata's API (free tier). Each file carries a metadata header: video ID, URL, fetch date, method.
- **LinkedIn posts:** collected manually (copy from the public post + record URL and date) using the template in `research/linkedin-posts/_TEMPLATE.md`. Automated LinkedIn scraping violates LinkedIn's Terms of Service, so this repo intentionally uses manual collection.
- **Attribution:** all collected material remains the intellectual property of its authors and is stored here for private research/analysis only. Every file links its original source.

## Collection status

| Author | LinkedIn posts | YT/podcast transcripts | Status |
|---|---|---|---|
| Jason Bay | 0 | 3 | transcripts ✓ (cold email 85M study, cold-calling hot take, Rippling outbound); LinkedIn pending |
| Josh Braun | 0 | 2 | transcripts ✓ (cold-call script + 7 objections, techniques that get responses); LinkedIn-primary, posts pending |
| 30MPC | — | 3 | transcripts ✓ (cold-call opener, cold-call objection handling, cold-email sequence) |
| Will Allred | 0 | 2 | transcripts ✓ (real 2025 campaign lessons, smarter outbound w/ Lavender data) |
| Florin Tatulea | 0 | 2 | transcripts ✓ (2026 cold-email showdown; pclub cold-email secrets, 2023) |
| Kyle Coleman | 0 | 1 | transcript ✓ (AI for prospecting executives); 2nd (GTM/AI) pending Supadata async |
| Becc Holland | 0 | 2 | transcripts ✓ (2025 outbound playbook; signature "math of personalization", 2024) |
| Morgan J Ingram | 0 | 3 | transcripts ✓ (next-level pipeline, AI-assisted selling, LinkedIn prospecting workshop 2024) |
| Eric Nowoslawski | 0 | 3 | transcripts ✓ (Clay+Smartlead tech stack, personalization at 1.5M scale, cold-email restart) |
| Sam Nelson | 0 | 2 | transcripts ✓ (crush SD in 2025; winning outbound sequence strategy, 2024) |

