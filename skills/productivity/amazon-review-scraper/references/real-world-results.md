# Real-World Test Results (2026-05-13)

## Products Tested

| ASIN | Product | Reviews | 5★ | 4★ | 3★ | 2★ | 1★ | Verified | Images | Video |
|------|---------|---------|-----|-----|-----|-----|-----|----------|--------|-------|
| B0G636CXQM | OBSBOT Tiny 3 | 29 | 23 | 2 | 1 | 2 | 1 | 26 | 6 | 2 |
| B0G63LXK6R | OBSBOT Tiny 3 Lite | 32 | 21 | 5 | 0 | 1 | 5 | 26 | 8 | 2 |
| B0C3B6ZR1V | OBSBOT Tiny 2 | 185 | 113 | 24 | 14 | 9 | 25 | 169 | 25 | 5 |
| B0DDTH3HX8 | Insta360 Link 2 | 206 | 129 | 22 | 7 | 12 | 36 | 195 | 17 | 5 |

## Key Findings

### Ratings vs Reviews (Critical Distinction)
- Amazon shows "138 ratings" for B0G636CXQM — only **29** are written reviews
- Typically **10-20%** of ratings have text content
- Always clarify this to users: "138 ratings, 29 written reviews"

### Woot vs Browser Comparison (B0G636CXQM)
- Browser + Cookie (logged in): 13 reviews (Amazon's page limit)
- Woot endpoint (no login): 29 reviews (+123% more)
- The browser approach hits Amazon's "Top Reviews" page limit

### Max Mode Efficiency
- For products with <50 written reviews, different sort orders return identical results
- For products with >100 reviews, sort orders surface different reviews
- Max mode adds ~0-30% more reviews over full mode depending on product size

### Multi-Product Batch Pattern
When scraping multiple ASINs, use `delegate_task` for parallel execution:
```
delegate_task with 3 parallel tasks:
  1. Scrape ASIN_A → create Tencent Doc → move to folder
  2. Scrape ASIN_B → create Tencent Doc → move to folder
  3. Scrape ASIN_C → create Tencent Doc → move to folder
```
Each task takes ~2-3 minutes. Parallel execution = same time as single product.

### Tencent Docs Integration
Amazon review docs go to: obsbot → Amazon folder (DKQjkLCCkwLR)
Create as smartcanvas_by_mdx, then move_file to target folder.
Title limit: 36 chars max.
