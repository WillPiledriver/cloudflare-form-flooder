# cloudflare-form-flooder
HTTPS post request flooding with anti-cloudflare

Very quick proxy scraper and https post request form flooding. Using the package called cloudscraper, you can bypass Cloudflare Under Attack mode.
Just plug in the url endpoint and the request data. I have been using this against some steam phishing websites to flood their database with bullshit logins pretty effectively using a proxy rotation method.
It uses threading, so the speed is dependent on the pool size and your bandwidth. (i maxed out at about 100 requests per second).
