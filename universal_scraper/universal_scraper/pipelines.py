# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import csv
import os
from datetime import datetime
from urllib.parse import urlparse
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class DataValidationPipeline:
    """Pipeline for validating and cleaning scraped data"""

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Validate required fields
        if not adapter.get('url'):
            raise DropItem("Missing URL in item")

        if adapter.get('status') not in [200, 301, 302, 404, 500]:
            spider.logger.warning(f"Unexpected status code: {adapter.get('status')} for URL: {adapter.get('url')}")

        # Clean and normalize data
        if adapter.get('title'):
            adapter['title'] = adapter['title'].strip()

        # Ensure links are properly formatted
        if adapter.get('links'):
            adapter['links'] = [link.strip() for link in adapter['links'] if link.strip()]

        return item


class DuplicateFilterPipeline:
    """Pipeline for filtering duplicate items"""

    def __init__(self):
        self.seen_urls = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        url = adapter.get('url')

        if url in self.seen_urls:
            raise DropItem(f"Duplicate item found: {url}")
        else:
            self.seen_urls.add(url)
            return item


class DataProcessingPipeline:
    """Pipeline for processing and enhancing scraped data"""

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Add processing timestamp
        adapter['processed_at'] = datetime.now().isoformat()

        # Calculate scrape duration if available
        if adapter.get('scraped_at'):
            scraped_time = datetime.fromisoformat(adapter['scraped_at'])
            processed_time = datetime.now()
            adapter['processing_duration'] = (processed_time - scraped_time).total_seconds()

        # Enhance link analysis
        if adapter.get('links'):
            adapter['total_links'] = len(adapter['links'])
            adapter['unique_links'] = len(set(adapter['links']))

            # Count different link types
            http_links = [link for link in adapter['links'] if link.startswith('http')]
            https_links = [link for link in adapter['links'] if link.startswith('https')]
            relative_links = [link for link in adapter['links'] if not link.startswith(('http', '//'))]

            adapter['http_links_count'] = len(http_links)
            adapter['https_links_count'] = len(https_links)
            adapter['relative_links_count'] = len(relative_links)

        # Add domain information
        if adapter.get('url'):
            parsed = urlparse(adapter['url'])
            adapter['domain'] = parsed.netloc
            adapter['scheme'] = parsed.scheme
            adapter['path'] = parsed.path

        return item


class StatisticsPipeline:
    """Pipeline for collecting scraping statistics"""

    def __init__(self):
        self.stats = {
            'total_items': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0,
            'domains_scraped': set(),
            'status_codes': {},
            'avg_text_length': 0,
            'total_links_found': 0
        }

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        self.stats['total_items'] += 1

        # Track successful vs failed scrapes
        status = adapter.get('status', 0)
        if 200 <= status < 300:
            self.stats['successful_scrapes'] += 1
        else:
            self.stats['failed_scrapes'] += 1

        # Track status codes
        if status not in self.stats['status_codes']:
            self.stats['status_codes'][status] = 0
        self.stats['status_codes'][status] += 1

        # Track domains
        if adapter.get('domain'):
            self.stats['domains_scraped'].add(adapter['domain'])

        # Update averages
        text_length = adapter.get('text_length', 0)
        self.stats['avg_text_length'] = (
            (self.stats['avg_text_length'] * (self.stats['total_items'] - 1)) + text_length
        ) / self.stats['total_items']

        # Count links
        self.stats['total_links_found'] += adapter.get('total_links', 0)

        return item

    def close_spider(self, spider):
        """Save statistics when spider closes"""
        stats_file = f"stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, 'w') as f:
            # Convert set to list for JSON serialization
            stats_copy = self.stats.copy()
            stats_copy['domains_scraped'] = list(stats_copy['domains_scraped'])
            json.dump(stats_copy, f, indent=2)

        spider.logger.info(f"Scraping statistics saved to {stats_file}")


class DataExportPipeline:
    """Pipeline for exporting data in various formats"""

    def __init__(self):
        self.items = []
        # Set output directory to project root (outside universal_scraper)
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'output')
        os.makedirs(self.output_dir, exist_ok=True)

    def process_item(self, item, spider):
        self.items.append(dict(item))
        return item

    def close_spider(self, spider):
        """Export data when spider closes"""
        if not self.items:
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Check if this is HTML format (items will have html_content field)
        is_html_format = (len(self.items) > 0 and 
                         'html_content' in self.items[0])
        
        # Debug logging
        spider.logger.info(f"Items count: {len(self.items)}")
        if self.items:
            spider.logger.info(f"First item keys: {list(self.items[0].keys())}")
            spider.logger.info(f"First item length: {len(self.items[0])}")
            spider.logger.info(f"Has html_content: {'html_content' in self.items[0]}")
            spider.logger.info(f"Has text_content: {'text_content' in self.items[0]}")
            spider.logger.info(f"Has links: {'links' in self.items[0]}")
            spider.logger.info(f"Is HTML format: {is_html_format}")

        if is_html_format:
            # Export HTML content
            self._export_html(timestamp)
        else:
            # Export full JSON data
            self._export_json(timestamp)

    def _export_json(self, timestamp):
        """Display JSON data in terminal instead of exporting to file"""
        print("\n" + "="*80)
        print("SCRAPED DATA (JSON FORMAT)")
        print("="*80)
        
        for i, item in enumerate(self.items, 1):
            print(f"\n--- Item {i} ---")
            print(json.dumps(item, indent=2, ensure_ascii=False))
            print("-" * 40)

    def _export_html(self, timestamp):
        """Display HTML content summary in terminal instead of exporting to file"""
        if not self.items:
            return

        item = self.items[0]  # Should only be one item for HTML format
        title = item.get('title', 'No title')
        url = item.get('url', 'No URL')
        html_content = item.get('html_content', '')

        print("\n" + "="*80)
        print("SCRAPED HTML CONTENT")
        print("="*80)
        print(f"Title: {title}")
        print(f"URL: {url}")
        print(f"Content Length: {len(html_content)} characters")
        print("-" * 40)
        
        # Show first 1000 characters of HTML content
        preview_length = 1000
        if len(html_content) > preview_length:
            print("HTML Preview (first 1000 characters):")
            print(html_content[:preview_length])
            print("...")
            print(f"(Content truncated. Full length: {len(html_content)} characters)")
        else:
            print("Full HTML Content:")
            print(html_content)
