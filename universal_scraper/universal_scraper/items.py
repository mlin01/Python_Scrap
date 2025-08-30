# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UniversalScraperItem(scrapy.Item):
    # Basic page information
    url = scrapy.Field()
    title = scrapy.Field()
    status = scrapy.Field()
    response_headers = scrapy.Field()

    # Content information
    text_content = scrapy.Field()
    text_length = scrapy.Field()
    html_content = scrapy.Field()

    # Links and navigation
    links = scrapy.Field()
    internal_links = scrapy.Field()
    external_links = scrapy.Field()

    # Metadata
    scraped_at = scrapy.Field()
    scrape_duration = scrapy.Field()
    user_agent = scrapy.Field()

    # Custom data extraction
    custom_data = scrapy.Field()

    # Processing metadata
    processed_at = scrapy.Field()
    processing_duration = scrapy.Field()

    # Link analysis
    total_links = scrapy.Field()
    unique_links = scrapy.Field()
    http_links_count = scrapy.Field()
    https_links_count = scrapy.Field()
    relative_links_count = scrapy.Field()

    # Error handling
    error_message = scrapy.Field()
    retry_count = scrapy.Field()

    # URL components
    domain = scrapy.Field()
    scheme = scrapy.Field()
    path = scrapy.Field()
