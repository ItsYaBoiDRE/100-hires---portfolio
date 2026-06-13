"""
Fetch YouTube transcripts for the research repo.

Two methods, in order of preference:
  1. youtube-transcript-api  (free, no API key)
  2. Supadata API            (free tier, needs SUPADATA_API_KEY env var)

Usage:
  pip install youtube-transcript-api requests
  python fetch_youtube_transcripts.py <video_id_or_url> --author jason-bay \
      --title "..." --published 2025-11-04 --why "why it matters for the playbook"

  Multiple ids are allowed for a quick bulk pull, but --title/--published/--why
  apply to the whole call, so fetch one video at a time when you want per-video
  metadata (the normal collection path).

  If --title / --published are omitted and SUPADATA_API_KEY is set, they are
  auto-filled from Supadata's YouTube video-metadata endpoint, so usually you
  only need to pass --why. Use --source supadata to skip the free library
  outright (e.g. when this machine's IP is being YouTube-rate-limited).

Output:
  ../research/youtube-transcripts/<author>/<video_id>.md
  Each file has front-matter (video id, title, URL, publish date, fetch date,
  method) plus a "Why it matters for the playbook" note and the transcript,
  matching the repo's per-file quality bar.
"""

import argparse
import datetime
import os
import re
import sys
import time

import requests

OUT_ROOT = os.path.join(os.path.dirname(__file__), "..", "research", "youtube-transcripts")


def extract_video_id(value: str) -> str:
    """Accept a raw ID or any common YouTube URL form."""
    patterns = [
        r"(?:v=|youtu\.be/|shorts/|embed/)([A-Za-z0-9_-]{11})",
        r"^([A-Za-z0-9_-]{11})$",
    ]
    for p in patterns:
        m = re.search(p, value)
        if m:
            return m.group(1)
    raise ValueError(f"Could not parse a video id from: {value}")


def fetch_via_library(video_id: str) -> str | None:
    """Method 1: youtube-transcript-api (no key needed)."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id, languages=["en", "en-US", "en-GB"])
        return "\n".join(snippet.text for snippet in fetched)
    except Exception as exc:  # noqa: BLE001 - report and fall through
        print(f"  [youtube-transcript-api failed: {exc}]")
        return None


def fetch_via_supadata(video_id: str) -> str | None:
    """Method 2: Supadata API fallback. Set SUPADATA_API_KEY.

    Uses Supadata's universal transcript endpoint. The older
    /v1/youtube/transcript route (with a `videoId` param) is deprecated;
    the universal /v1/transcript route takes a `url` param and works across
    platforms. Verified against https://docs.supadata.ai (June 2026): with
    text=true the plain-text transcript is returned in the JSON `content`
    field, alongside `lang` and `availableLangs`.
    """
    key = os.environ.get("SUPADATA_API_KEY")
    if not key:
        print("  [Supadata skipped: SUPADATA_API_KEY not set]")
        return None
    try:
        resp = requests.get(
            "https://api.supadata.ai/v1/transcript",
            params={
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "text": "true",
                "lang": "en",
            },
            headers={"x-api-key": key},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        # text=true -> {"content": <str>, "lang": ..., "availableLangs": [...]}
        # (.get("text") kept as a defensive fallback for older responses).
        text = _supadata_text(data)
        if not text and data.get("jobId"):
            # Long videos / mode=generate return an async jobId; poll for it.
            print(f"  [Supadata async jobId {data['jobId']}; polling...]")
            text = _poll_supadata_job(data["jobId"], key)
        return text
    except Exception as exc:  # noqa: BLE001
        print(f"  [Supadata failed: {exc}]")
        return None


def _supadata_text(data: dict) -> str | None:
    """Pull plain text from a Supadata transcript payload.

    With text=true `content` is a string; defensively handle the segment-array
    form (text=false) and the older `text` key too.
    """
    content = data.get("content")
    if isinstance(content, list):
        return "\n".join(
            seg.get("text", "") for seg in content if isinstance(seg, dict)
        ).strip() or None
    return content or data.get("text")


def _poll_supadata_job(job_id: str, key: str, attempts: int = 15, delay: int = 5) -> str | None:
    """Poll Supadata's async transcript job until it completes.

    GET /v1/transcript/{jobId} returns {"status": "queued|active|completed|failed",
    ..., "content": ...}. Returns the transcript text once status=completed and
    content is present, else None.
    """
    url = f"https://api.supadata.ai/v1/transcript/{job_id}"
    for _ in range(attempts):
        time.sleep(delay)
        try:
            resp = requests.get(url, headers={"x-api-key": key}, timeout=60)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:  # noqa: BLE001
            print(f"  [Supadata job poll failed: {exc}]")
            return None
        status = data.get("status")
        if status == "failed":
            print("  [Supadata job failed]")
            return None
        text = _supadata_text(data)
        if status == "completed" and text:
            return text
    print("  [Supadata job still processing after polling window]")
    return None


def fetch_metadata_via_supadata(video_id: str) -> dict:
    """Fetch title + upload date from Supadata's YouTube video-metadata endpoint.

    Returns {"title": str|None, "published": "YYYY-MM-DD"|None, "channel": str|None}.
    Server-side, so it works even when this machine's IP is YouTube-rate-limited.
    Empty dict if no key or on error.
    """
    key = os.environ.get("SUPADATA_API_KEY")
    if not key:
        return {}
    try:
        resp = requests.get(
            "https://api.supadata.ai/v1/youtube/video",
            params={"id": video_id},
            headers={"x-api-key": key},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        channel = (data.get("channel") or {}).get("name")
        return {
            "title": data.get("title"),
            "published": (data.get("uploadDate") or "")[:10] or None,
            "channel": channel,
        }
    except Exception as exc:  # noqa: BLE001
        print(f"  [Supadata metadata failed: {exc}]")
        return {}


def _yaml_str(value: str) -> str:
    """Return a YAML-safe double-quoted scalar.

    Titles often start with characters YAML treats specially ('[' starts a
    flow sequence, '*' is an alias reference), so always quote them.
    """
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def save_transcript(
    author: str,
    video_id: str,
    text: str,
    method: str,
    title: str | None = None,
    published: str | None = None,
    why: str | None = None,
) -> str:
    out_dir = os.path.join(OUT_ROOT, author)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{video_id}.md")
    title = title or "(title not set)"
    published = published or "unknown"
    why = why or "TODO: why this matters for the cold-outreach playbook."
    header = (
        f"---\n"
        f"video_id: {video_id}\n"
        f"title: {_yaml_str(title)}\n"
        f"url: https://www.youtube.com/watch?v={video_id}\n"
        f"published: {published}\n"
        f"fetched: {datetime.date.today().isoformat()}\n"
        f"method: {method}\n"
        f"---\n\n"
        f"# {title}\n\n"
        f"## Why it matters for the playbook\n{why}\n\n"
        f"## Transcript\n"
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(header + text.strip() + "\n")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("videos", nargs="+", help="Video IDs or URLs")
    parser.add_argument("--author", required=True, help="Folder name, e.g. jason-bay")
    parser.add_argument("--title", help="Video title (applies to this call)")
    parser.add_argument("--published", help="Publish date YYYY-MM-DD (applies to this call)")
    parser.add_argument("--why", help="Why it matters for the playbook (1-3 sentences)")
    parser.add_argument(
        "--source", choices=["auto", "library", "supadata"], default="auto",
        help="Transcript source: auto (library then Supadata), or force one.",
    )
    args = parser.parse_args()

    failures = []
    for raw in args.videos:
        vid = extract_video_id(raw)
        print(f"Fetching {vid} ...")
        text = method = None
        if args.source in ("auto", "library"):
            text = fetch_via_library(vid)
            method = "youtube-transcript-api"
        if not text and args.source in ("auto", "supadata"):
            text = fetch_via_supadata(vid)
            method = "supadata"
        if not text:
            failures.append(vid)
            continue

        # Auto-fill title/published from Supadata metadata when not supplied.
        title, published = args.title, args.published
        if not title or not published:
            meta = fetch_metadata_via_supadata(vid)
            title = title or meta.get("title")
            published = published or meta.get("published")

        path = save_transcript(
            args.author, vid, text, method,
            title=title, published=published, why=args.why,
        )
        print(f"  saved -> {os.path.relpath(path)} "
              f"(title={'set' if title else 'MISSING'}, published={published or 'MISSING'})")

    if failures:
        print(f"\nFailed: {', '.join(failures)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
