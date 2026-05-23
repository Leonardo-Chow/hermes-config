# YouTube Comment Extraction Reference

## Browser-based Extraction Pattern

When TranscriptAPI doesn't provide comments, use browser tools to extract them directly from YouTube pages.

### JavaScript Selectors

| Element | Selector | Notes |
|:--------|:---------|:------|
| Comment container | `ytd-comment-thread-renderer` | Each comment is wrapped in this element |
| Author name | `#author-text` | Contains @username |
| Comment text | `#content-text` | Main comment body |
| Like count | `#vote-count-middle` | May be empty for low-engagement comments |
| Comment count | `h2 yt-formatted-string` | Shows "N 条评论" or "N comments" |

### Extraction Script

```javascript
const comments = [];
const commentElements = document.querySelectorAll('ytd-comment-thread-renderer');
commentElements.forEach((el, i) => {
    if (i < 10) {
        const author = el.querySelector('#author-text')?.textContent?.trim() || '';
        const text = el.querySelector('#content-text')?.textContent?.trim() || '';
        const likes = el.querySelector('#vote-count-middle')?.textContent?.trim() || '';
        if (text) {
            comments.push({ author, text, likes });
        }
    }
});
JSON.stringify(comments, null, 2);
```

### Workflow

1. `browser_navigate` to video URL
2. `browser_scroll` down 2-3 times (comments lazy-load below video)
3. `browser_console` with extraction script
4. Parse JSON result

### Limitations

- Only extracts visible comments (top/recent)
- YouTube bot detection may block without residential proxies
- Requires VPN in GFW regions
- Comment replies are not extracted (only top-level comments)

## TranscriptAPI Metadata

For video title/tags without full transcript:

```bash
curl -s "https://transcriptapi.com/api/v2/youtube/transcript?video_url=VIDEO_ID&format=json&send_metadata=true" \
  -H "Authorization: Bearer $TRANSCRIPT_API_KEY" \
  -H "User-Agent: HermesAgent/0.11.0"
```

Returns: `metadata.title`, `metadata.author_name`, `metadata.author_url`
