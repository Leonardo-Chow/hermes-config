# Daily Digest (摸鱼日报) — IMA Publishing Pattern

Proven workflow for generating and publishing a structured daily briefing to IMA notes + knowledge base.

## Overview

```
Data Sources (parallel async) → Markdown Assembly → import_doc (create note) → add_knowledge (associate to KB)
```

## IMA API Sequence

### Step 1: Get cover image fresh signed URL

Cover images in IMA have time-limited signed URLs. Always refresh before publishing:

```bash
node "$SKILL_DIR/ima_api.cjs" "openapi/wiki/v1/get_media_info" \
  '{"media_id":"img_<ID>_<HASH>"}' "$OPTS"
# → data.url_info.url contains the current signed URL
```

### Step 2: Create the note

```bash
node "$SKILL_DIR/ima_api.cjs" "openapi/note/v1/import_doc" \
  '{"title":"2026年X月X日 · 摸鱼日报","content":"# Markdown content here...","content_format":1}' "$OPTS"
# → data.note_id is the new note's ID
```

- `content_format` MUST be `1` (Markdown)
- title and content MUST be valid UTF-8 (see main SKILL.md UTF-8 rules)
- The response returns `note_id`

### Step 3: Associate to knowledge base

```bash
node "$SKILL_DIR/ima_api.cjs" "openapi/wiki/v1/add_knowledge" \
  '{"knowledge_base_id":"<kb_id>","media_type":11,"note_info":{"content_id":"<note_id>"}}' "$OPTS"
# → data.media_id is the KB entry ID
```

- `media_type=11` means "note type" media
- The note is now browseable in the knowledge base

## Traps

- **Cover image URL expires**: always call `get_media_info` before publishing to get a fresh signed URL
- **import_doc creates a new note each time**: does NOT update an existing note. Use `append_doc` to append to existing notes
- **Permission model**: the API only operates on YOUR own notes and addable KBs. `add_knowledge` requires you to have write permission on the target KB
- **Content size limit**: single notes have a max size limit. Very long daily digests (>50KB) may hit `CONTENT_SIZE_OVERLOAD` (error 210009)
