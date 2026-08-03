#!/bin/bash
# Fetch Instagram follower count for one username
COOKIE_STR="$1"
USERNAME="$2"
curl -s --max-time 10 \
  -H "Cookie: ${COOKIE_STR}" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36" \
  "https://www.instagram.com/${USERNAME}/"
