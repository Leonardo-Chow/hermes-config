# Platform Cookies for OBSBOT Monitoring

> ⚠️ Cookies expire. Update when user provides new ones.

## Instagram Cookie
```
ps_n=1;datr=6PYYaksTidRhXCIPt-tJsJTx;ig_nrcb=1;ds_user_id=72830600731;csrftoken=IDu14B30o2ck21wlSYatxABDMGYcAds8;g_state={"i_l":0,"i_ll":1780366121471,"i_b":"5Ffkap3OyLu55ninjknSJxj23v3O3zLuoeHLxqjsn3A","i_e":{"enable_itp_optimization":0},"i_et":1780364297910};ig_did=980A8C7C-C606-4BC5-914B-63EF2255439A;ps_l=1;wd=1454x696;mid=ahj26wAEAAGU4WEdDcGmajkV6YyT;sessionid=72830600731%3AHXbaiT7WrGS5VK%3A25%3AAYg2qgBIKPtJ0H8mBLUNYJ89NLGubl3Vq1yXRDqJpw;rur="SNB\05472830600731\0541811902119:01ff5ee432d9dc062e2f9d2a3e4301609cbf5643de86a5784793eda307094658a54caf17"
```

## X/Twitter Cookie
```
auth_token=a250e62f0cc69a2b478be28e20c9e207546fdc2c;gt=2061623375127056618;__cuid=7152d613-6c41-4a32-a6d5-6444007dd262;guest_id=v1%3A178036428936232738;twid=u%3D1673994184464949248;ct0=ed13ca73271642e9f9d6a077f92b058d70436e81904a9223353dc61047b24e6a7df41f02ed3fa0e6bb400394271b6617fb4ef8c79a89c8b868fc16fb7a7e4c7225252cb8f691f6ae612249d8e3b97108;guest_id_ads=v1%3A178036428936232738;guest_id_marketing=v1%3A178036428936232738;personalization_id="v1_Sps1RGqZ1q+LQwsgT3vzjg=="
```

## TikTok Cookie
```
sid_guard=7418997a041b4d13d711975e8d0eaa13%7C1780031176%7C15552000%7CWed%2C+25-Nov-2026+05%3A06%3A16+GMT;ttwid=1%7Cazs44ncDCvbUsZ4zgwm6fGZnLkuJTovCjb_9C8HgEPU%7C1780366121%7C383143c3acf5ad317fdad5d77291fd3de95a8f5e0f4a1a97030a5632853e9b85;uid_tt=e569ea7ea5c9881c1072aba6eaa84f7d2d405cacb155e945e8a8acb56c3221c2;sessionid=7418997a041b4d13d711975e8d0eaa13;sid_tt=7418997a041b4d13d711975e8d0eaa13;store-country-code=cn;tt-target-idc=alisg
```

## YouTube Cookie
```
ST-xuwub9=session_logininfo=AFmmF2swRQIhANkiq_6sWGvjcyEoLraf4bqCpOTnmgXMsa8nzDL0XSyNAiBOnyYNZogCwFgVe0mDJHejeCCHloUrFqnBhJAt8dHVYQ%3AQUQ3MjNmeTg3ZWRWVkFKdnNOcDVNX1FQSV9CTXR3U1JtVXhyNlpsTHBBV3dObHMwbEI0OUdib2NEenFMNzFhRUtiUUJuY1pBZXdRek9EZ1lyLWNSSFdHYURKQldiZ2FYWUNLeHVXaFhfUDhyM2h0dkFaQjRhdDRxZlpEaFNsOU5XUTVyak1FS05GS2pOSlU4Q0Rhd2JVT2UzSHVNUzRvTjFB;__Secure-3PSID=g.a000-Qhtw7ichyFtc1cSXMaA9XmkXwO1kAUofFHaMfKZGw556jw2-d-sj1lQgkMRNDJLZ65m9wACgYKATkSARMSFQHGX2MijVJ519DoacJbAQVqZNVHjhoVAUF8yKoDor_l8xQ5RIpsLRfrlcz00076;LOGIN_INFO=AFmmF2swRQIhANkiq_6sWGvjcyEoLraf4bqCpOTnmgXMsa8nzDL0XSyNAiBOnyYNZogCwFgVe0mDJHejeCCHloUrFqnBhJAt8dHVYQ:QUQ3MjNmeTg3ZWRWVkFKdnNOcDVNX1FQSV9CTXR3U1JtVXhyNlpsTHBBV3dObHMwbEI0OUdib2NEenFMNzFhRUtiUUJuY1pBZXdRek9EZ1lyLWNSSFdHYURKQldiZ2FYWUNLeHVXaFhfUDhyM2h0dkFaQjRhdDRxZlpEaFNsOU5XUTVyak1FS05GS2pOSlU4Q0Rhd2JVT2UzSHVNUzRvTjFB;PREF=f4=4000000&tz=Asia.Shanghai&f5=30000
```

## 使用方法

### curl 带 Cookie
```bash
curl -s -b "COOKIE_STRING" "https://www.instagram.com/obsbot/"
```

### Scrapling 带 Cookie
```python
from scrapling.fetchers import StealthyFetcher
page = StealthyFetcher.fetch(
    'https://www.instagram.com/obsbot/',
    cookies={'sessionid': '...', 'csrftoken': '...'},
    proxy='http://127.0.0.1:1082',
    ...
)
```

### Playwright 带 Cookie
```python
context.add_cookies([{'name': 'sessionid', 'value': '...', 'domain': '.instagram.com', 'path': '/'}])
```
