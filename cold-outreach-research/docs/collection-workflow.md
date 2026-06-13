# Collection workflow & commit plan

## Daily loop (30–45 min/day for ~5 days)
1. Pick 2 authors from the status table in README.md.
2. YouTube/podcast: find 2–3 recent, on-topic videos -> run
   `python scripts/fetch_youtube_transcripts.py <url> <url> --author <folder>`
3. LinkedIn: open the author's recent activity, pick 3–5 high-signal posts
   (frameworks, data, real examples — skip engagement bait), fill _TEMPLATE.md
   per post, save as `YYYY-MM-DD-short-slug.md`.
4. Update the README status table.
5. Commit.

## Commit plan (small, regular commits — not one dump)
- chore: scaffold repo structure and scripts
- docs: add annotated sources list (10 experts)
- feat: add YouTube transcript fetcher (yt-transcript-api + Supadata fallback)
- data: add Jason Bay transcripts (x3) and LinkedIn posts (x4)
- data: add Josh Braun LinkedIn posts (x5)
- ... one commit per author or per collection session ...
- docs: update README collection status table

## Quality bar per file
- Source URL + date present in front-matter
- "Why it matters" note filled in (this is what makes the repo playbook-ready)
- No paywalled/private content; public posts and videos only

## Compliance notes
- LinkedIn posts are collected manually; no scraping (LinkedIn ToS).
- Transcripts/posts are stored for private research with full attribution;
  the eventual playbook will paraphrase and cite, not republish.
