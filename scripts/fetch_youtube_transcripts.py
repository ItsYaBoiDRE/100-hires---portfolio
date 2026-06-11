"""
Fetch YouTube transcripts for the research repo.

Two methods, in order of preference:
  1. youtube-transcript-api  (free, no API key)
  2. Supadata API            (free tier, needs SUPADATA_API_KEY env var)

Usage:
  pip install youtube-transcript-api requests
  python fetch_youtube_transcripts.py <video_id_or_url> [more ids...] --author "jason-bay"

Output:
  ../research/youtube-transcripts/<author>/<video_id>.md
  with a metadata header (video id, URL, fetch date, method).
"""

import argparse
import datetime
import os
import re
import sys

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
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        # text=true -> {"content": <str>, "lang": ..., "availableLangs": [...]}
        # (.get("text") kept as a defensive fallback for older responses).
        text = data.get("content") or data.get("text")
        if not text and data.get("jobId"):
            # Long videos / mode=generate return an async jobId to poll at
            # /v1/transcript/{jobId}; not handled here — re-run usually serves
            # the cached result synchronously.
            print(f"  [Supadata returned async jobId {data['jobId']}; "
                  "polling not implemented — re-run to fetch cached result]")
        return text
    except Exception as exc:  # noqa: BLE001
        print(f"  [Supadata failed: {exc}]")
        return None


def save_transcript(author: str, video_id: str, text: str, method: str) -> str:
    out_dir = os.path.join(OUT_ROOT, author)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{video_id}.md")
    header = (
        f"---\n"
        f"video_id: {video_id}\n"
        f"url: https://www.youtube.com/watch?v={video_id}\n"
        f"fetched: {datetime.date.today().isoformat()}\n"
        f"method: {method}\n"
        f"---\n\n"
    )
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(header + text.strip() + "\n")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("videos", nargs="+", help="Video IDs or URLs")
    parser.add_argument("--author", required=True, help="Folder name, e.g. jason-bay")
    args = parser.parse_args()

    failures = []
    for raw in args.videos:
        vid = extract_video_id(raw)
        print(f"Fetching {vid} ...")
        text = fetch_via_library(vid)
        method = "youtube-transcript-api"
        if not text:
            text = fetch_via_supadata(vid)
            method = "supadata"
        if not text:
            failures.append(vid)
            continue
        path = save_transcript(args.author, vid, text, method)
        print(f"  saved -> {os.path.relpath(path)}")

    if failures:
        print(f"\nFailed: {', '.join(failures)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
