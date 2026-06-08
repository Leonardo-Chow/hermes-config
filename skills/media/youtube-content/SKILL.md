---
name: youtube-content
description: "YouTube transcripts to summaries, threads, blogs."
platforms: [linux, macos, windows]
---

# YouTube Content Tool

## When to use

Use when the user shares a YouTube URL or video link, asks to summarize a video, requests a transcript, or wants to extract and reformat content from any YouTube video. Transforms transcripts into structured content (chapters, summaries, threads, blog posts).

Extract transcripts from YouTube videos and convert them into useful formats.

## Setup

```bash
pip install youtube-transcript-api PySocks
```

**PySocks is required** for SOCKS5 proxy support (Shadowrocket, v2rayN, etc.). Without it, `Missing dependencies for SOCKS support` error will occur when proxy is active.

## Helper Script

`SKILL_DIR` is the directory containing this SKILL.md file. The script accepts any standard YouTube URL format, short links (youtu.be), shorts, embeds, live links, or a raw 11-character video ID.

```bash
# JSON output with metadata
python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text (good for piping into further processing)
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback chain
python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

## Output Formats

After fetching the transcript, format it based on what the user asks for:

- **Chapters**: Group by topic shifts, output timestamped chapter list
- **Summary**: Concise 5-10 sentence overview of the entire video
- **Chapter summaries**: Chapters with a short paragraph summary for each
- **Thread**: Twitter/X thread format — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, and key takeaways
- **Quotes**: Notable quotes with timestamps

### Example — Chapters Output

```
00:00 Introduction — host opens with the problem statement
03:45 Background — prior work and why existing solutions fall short
12:20 Core method — walkthrough of the proposed approach
24:10 Results — benchmark comparisons and key takeaways
31:55 Q&A — audience questions on scalability and next steps
```

## Workflow

1. **Fetch** the transcript using the helper script with `--text-only --timestamps`.
2. **Validate**: confirm the output is non-empty and in the expected language. If empty, retry without `--language` to get any available transcript. If still empty, tell the user the video likely has transcripts disabled.
3. **Chunk if needed**: if the transcript exceeds ~50K characters, split into overlapping chunks (~40K with 2K overlap) and summarize each chunk before merging.
4. **Transform** into the requested output format. If the user did not specify a format, default to a summary.
5. **Verify**: re-read the transformed output to check for coherence, correct timestamps, and completeness before presenting.

## Direct Python API (when script fails)

If the helper script fails, use the API directly. **The API is instance-based** (not class methods):

```python
import os
os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1082'  # if behind GFW/proxy

from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
transcript = api.fetch(video_id, languages=['en', 'zh-Hans', 'zh-Hant', 'ja', 'ko'])

for entry in transcript:
    print(f"[{int(entry.start//60):02d}:{int(entry.start%60):02d}] {entry.text}")
```

## Pitfalls

- **API changed (v1.2+)**: No `YouTubeTranscriptApi.get_transcript()` or `YouTubeTranscriptApi.list_transcripts()`. Use `api = YouTubeTranscriptApi()` then `api.fetch(video_id, languages=[...])`.
- **PySocks required for proxy**: Without PySocks installed in the same Python environment, SOCKS5 proxy (`socks5h://`) will fail with `Missing dependencies for SOCKS support`. Install with `pip install PySocks`.
- **Proxy env vars**: Set `HTTPS_PROXY=socks5h://127.0.0.1:1082` (Shadowrocket default). Python `requests` (used internally) reads env vars, not `session.proxies`.
- **Python version mismatch**: `pip install` may install to system Python 3.9 while Hermes uses 3.12. Use `python3 -m pip install` to target the correct environment.

## Error Handling

- **Transcript disabled**: tell the user; suggest they check if subtitles are available on the video page.
- **Private/unavailable video**: relay the error and ask the user to verify the URL.
- **No matching language**: retry without `--language` to fetch any available transcript, then note the actual language to the user.
- **Dependency missing**: run `pip install youtube-transcript-api` and retry.
