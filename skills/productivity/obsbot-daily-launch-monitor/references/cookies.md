# Platform Cookies

## Cookie File Location

```
~/.hermes/cookies/platform_cookies.json
```

## Last Updated

2026-06-01

## Platforms Included

- Instagram
- X/Twitter
- TikTok
- YouTube

## Usage

Read cookies from file:

```python
import json
with open('/Users/zhoulong/.hermes/cookies/platform_cookies.json') as f:
    cookies = json.load(f)

# Use in curl
cookie_header = cookies['tiktok']
```

## Notes

- Cookies may expire; check `updated_at` field
- TikTok oembed API works with proxy (127.0.0.1:1082) without cookies
- Instagram/X cookies needed for direct API access
- YouTube cookies needed for accessing login-required content

## Known OBSBOT TikTok Accounts

For checking latest videos:

| Account | Handle | Followers |
|:--------|:-------|:----------|
| OBSBOT Official | @obsbot | 17.5K |
| obsbotmy | @obsbotmy1 | - |
| PSS Creative Media | @psscreativemedia | 1.8K |
| MrsMobster | @mrsmobster | - |
| MaccaGames | @maccagames | - |
| Brainiacvp | @brainiacvp | - |
| cestlabby | @cestlabby | - |
| stephskiii | @stephskiii | - |
