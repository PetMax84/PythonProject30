# lighting_spider_divan

Scrapy project example to crawl lighting products from `divan.ru`.

**What it extracts**
- product name
- price (raw)
- product URL

**How to use**
1. Install dependencies: `pip install -r requirements.txt`
2. From project root run: `scrapy runspider spiders/divan_spider.py -o results.jsonl`
3. Or open the project in PyCharm as a Python project and run the command above in a Run Configuration.

**Notes**
- Selectors are intentionally conservative: the spider finds product links containing `/product/`.
- You may need to adjust selectors depending on site layout changes.
- Respect `robots.txt`, terms of service and add delays (`DOWNLOAD_DELAY`) in production.
