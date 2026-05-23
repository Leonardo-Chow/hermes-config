# Amazon Review Scraping Workflow

Scraping Amazon product reviews using browser automation (curl is blocked by CAPTCHA).

## Why Not curl?

Amazon returns CAPTCHA page for automated requests from China:
```html
<h4>Click the button below to continue shopping</h4>
<!-- CAPTCHA form -->
```

## Solution: Browser + JavaScript Extraction

### Step 1: Navigate to Product Page

```bash
# Use browser tool (not curl)
browser_navigate url="https://www.amazon.com/dp/ASIN"
```

### Step 2: Click Reviews Section

```bash
# Find and click the "Reviews" link
browser_click ref="e15"  # (ref varies by page)
```

### Step 3: Scroll to Load Reviews

```bash
browser_scroll direction=down
browser_scroll direction=down
```

### Step 4: Extract Reviews via JavaScript

```javascript
// Method 1: Get review text directly
const pageContent = document.body.innerText;
const reviewStart = pageContent.indexOf('Top reviews from the United States');
// or: pageContent.indexOf('来自美国的热门评论');
pageContent.substring(reviewStart, reviewStart + 8000);

// Method 2: Get structured review data
const reviews = document.querySelectorAll('[data-hook="review"]');
reviews.forEach(review => {
    const title = review.querySelector('[data-hook="review-title"]')?.textContent;
    const body = review.querySelector('[data-hook="review-body"]')?.textContent;
    const rating = review.querySelector('[data-hook="review-star-rating"]')?.textContent;
    const author = review.querySelector('.a-profile-name')?.textContent;
    const date = review.querySelector('[data-hook="review-date"]')?.textContent;
});
```

### Step 5: Parse and Format

Reviews contain:
- Author name
- Star rating (e.g., "5 星（最高 5 星）" or "5 stars out of 5")
- Title
- Body text
- Date and location (e.g., "2025年10月1日在美国发布评论")
- Verified purchase badge
- Helpful votes count

## Pitfalls

- **CAPTCHA**: curl always gets CAPTCHA from China; must use browser
- **Language detection**: Amazon may show Chinese UI; review section label varies
- **Review loading**: Reviews load lazily; must scroll down 2-3 times
- **Variable references**: `browser_console` reuses JS context; use unique variable names to avoid "already declared" errors
- **Page structure**: Review content is in `document.body.innerText`, not in structured DOM elements on some pages
- **Stealth warning**: Browser runs without residential proxies; bot detection may be aggressive
