# Robust Markdown Table Parsing from get_content

## Problem
`get_content` returns pipe-delimited Markdown tables, but fields like video titles contain `|`, `&`, HTML entities, and special characters that break naive `line.split('|')` parsing.

## Solution: Anchor-Based Reverse Parsing

Instead of relying on column positions from the left, anchor on **fixed-format fields from the right**:

1. **URL** — always matches `https://youtube.com/watch?v=XXXXXXXXXXX` (fixed length, no pipes)
2. **Date** — always `YYYY-MM-DD` format
3. **Numeric fields** — views, likes, comment count are pure digits (or digits with commas)

### Implementation

```python
def parse_sheet_row(line):
    """Parse a markdown table row with robust anchor-based approach."""
    # 1. Extract URL first (rightmost stable anchor)
    url_match = re.search(r'(https?://[^\s|]+)', line)
    if not url_match:
        return None
    url = url_match.group(1)
    
    # 2. Split and clean
    parts = [p.strip() for p in line.split('|')]
    parts = [p for p in parts if p]  # remove empty strings
    
    # 3. Find date anchor (YYYY-MM-DD)
    date_idx = None
    for i, p in enumerate(parts):
        if re.match(r'\d{4}-\d{2}-\d{2}', p):
            date_idx = i
            break
    
    if date_idx is None:
        return None
    
    # 4. Extract fields anchored on date position
    date = parts[date_idx]
    comment_count = parts[date_idx - 1] if date_idx >= 1 else '0'
    likes = parts[date_idx - 2] if date_idx >= 2 else '0'
    views = parts[date_idx - 3] if date_idx >= 3 else '0'
    
    # 5. Extract fields from the left
    seq = parts[0] if parts[0].isdigit() else '?'
    channel = parts[1] if len(parts) > 1 else '?'
    
    # 6. Title is everything between channel and views (may contain |)
    # Reconstruct from original line using positional anchoring
    title_start = line.find(parts[1]) + len(parts[1]) + 1  # after channel + |
    title_end = line.find(parts[date_idx - 3])  # before views
    title = line[title_start:title_end].strip().strip('|').strip()
    
    return {
        'seq': seq, 'channel': channel, 'title': title,
        'views': views, 'likes': likes, 'comment_count': comment_count,
        'date': date, 'url': url
    }
```

### Alternative: Simple Right-Anchored Split (when title reconstruction is hard)

```python
# If you just need video_id, channel, and comment_count:
for line in lines:
    url_match = re.search(r'(https?://youtube\.com/watch\?[^\s|]+)', line)
    if not url_match:
        continue
    parts = [p.strip() for p in line.split('|')]
    parts = [p for p in parts if p]
    
    # Find date, then count backwards
    for i, p in enumerate(parts):
        if re.match(r'\d{4}-\d{2}-\d{2}', p):
            video = {
                'channel': parts[1],
                'views': parts[i-3],
                'likes': parts[i-2], 
                'comment_count': parts[i-1],
                'date': p,
                'url': url_match.group(1)
            }
            break
```

## Pitfalls

- **Sequence number validation**: First field (`parts[0]`) should be a digit. If it's not, the row is likely a continuation or header — skip it.
- **Comment count contains commas**: `1,145` → need `re.sub(r'[^\d]', '', value)` before `int()` conversion
- **URL may be wrapped in markdown link syntax**: `[text](url)` — extract URL from inside parentheses
- **Chinese/Japanese/emoji in titles**: These don't break parsing but may shift byte positions — use character-level indexing, not byte-level
