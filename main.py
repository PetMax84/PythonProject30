# -*- coding: utf-8 -*-
import re
from urllib.parse import urljoin
import scrapy
from w3lib.url import url_query_cleaner

class DivanLightingSpider(scrapy.Spider):
    name = "divan_lighting"
    allowed_domains = ["divan.ru"]
    start_urls = [
        "https://www.divan.ru/category/svet",
    ]

    custom_settings = {
        # polite defaults for running locally; tune as needed
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 0.5,
        "AUTOTHROTTLE_MAX_DELAY": 10,
        # export encoding
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    # generic product-link matcher: links that contain '/product/' are product pages on divan.ru
    product_link_pattern = re.compile(r'/product/')
    pagination_pattern = re.compile(r'(/category/.+page-\d+)|([?&]page=\d+)')

    price_rx = re.compile(r'(\d[\d\s\u00A0]*\d)\s*(руб|₽)', flags=re.IGNORECASE)

    def parse(self, response):
        # 1) find product links
        for href in response.css('a::attr(href)').getall():
            if not href:
                continue
            if self.product_link_pattern.search(href):
                absolute = urljoin(response.url, href)
                absolute = url_query_cleaner(absolute, remove_query=True)
                yield scrapy.Request(absolute, callback=self.parse_product)

        # 2) follow pagination links (pattern-based)
        for href in response.css('a::attr(href)').getall():
            if href and self.pagination_pattern.search(href):
                absolute = urljoin(response.url, href)
                yield scrapy.Request(absolute, callback=self.parse)

    def parse_product(self, response):
        # name: try common places
        name = response.css('h1::text').get() or response.css('[itemprop=name]::text').get() or response.xpath('//meta[@property="og:title"]/@content').get()
        if name:
            name = name.strip()

        # price: try common selectors, fallback to regex search in page text
        price = None
        # common classes/attrs that might contain price
        for sel in [
            '[itemprop=price]::attr(content)',
            '.price::text',
            '.product-price::text',
            '.product__price::text',
            '.price-new::text',
            '.price-value::text',
            '.catalog-price__value::text',
        ]:
            text = response.css(sel).get()
            if text:
                text = text.strip()
                # extract digits with руб or numeric
                m = self.price_rx.search(text)
                if m:
                    price = m.group(1).replace('\xa0', ' ').strip()
                    break
                # if numeric only
                digits = re.sub(r'[^0-9]', '', text)
                if digits:
                    price = digits
                    break

        if not price:
            # fallback: search page text
            m = self.price_rx.search(response.text)
            if m:
                price = m.group(1).replace('\xa0', ' ').strip()

        yield {
            "name": name,
            "price": price,
            "url": response.url,
        }
