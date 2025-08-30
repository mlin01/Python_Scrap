import scrapy
import json
from urllib.parse import urlparse
from datetime import datetime
from ..items import UniversalScraperItem


class UniversalSpider(scrapy.Spider):
    name = "universal"

    def __init__(self, url=None, format='json', *args, **kwargs):
        super(UniversalSpider, self).__init__(*args, **kwargs)
        if url:
            parsed = urlparse(url)
            self.allowed_domains = [parsed.netloc]
            self.start_urls = [url]
        else:
            self.allowed_domains = ["example.com"]
            self.start_urls = ["https://example.com"]

        self.output_format = format.lower()

    def parse(self, response):
        # Create item using the defined model
        item = UniversalScraperItem()

        # Basic page information
        item['url'] = response.url
        item['status'] = response.status

        # Convert headers from bytes/lists to strings for JSON serialization
        item['response_headers'] = {}
        for key, value in response.headers.items():
            key_str = key.decode('utf-8', errors='ignore') if isinstance(key, bytes) else str(key)
            if isinstance(value, list):
                value_str = [v.decode('utf-8', errors='ignore') if isinstance(v, bytes) else str(v) for v in value]
            else:
                value_str = value.decode('utf-8', errors='ignore') if isinstance(value, bytes) else str(value)
            item['response_headers'][key_str] = value_str

        # Check if response is JSON
        content_type = response.headers.get('Content-Type', b'').decode('utf-8', errors='ignore').lower()
        is_json = 'application/json' in content_type or response.url.endswith('.json')

        if is_json:
            # Handle JSON response
            try:
                json_data = response.json()
                item['title'] = f"JSON API Response from {urlparse(response.url).netloc}"
                item['text_content'] = json.dumps(json_data, indent=2)
                item['text_length'] = len(item['text_content'])
                item['html_content'] = item['text_content']  # Store JSON as HTML content for consistency

                # Extract links from JSON if it's an array of objects with URLs
                all_links = []
                if isinstance(json_data, list):
                    for obj in json_data:
                        if isinstance(obj, dict):
                            # Look for common URL fields
                            for key in ['url', 'link', 'href', 'website', 'permalink']:
                                if key in obj and obj[key]:
                                    all_links.append(str(obj[key]))
                elif isinstance(json_data, dict):
                    # Look for arrays in the JSON that might contain links
                    for key, value in json_data.items():
                        if isinstance(value, list) and len(value) > 0:
                            for obj in value[:10]:  # Limit to first 10 items
                                if isinstance(obj, dict):
                                    for link_key in ['url', 'link', 'href', 'website', 'permalink']:
                                        if link_key in obj and obj[link_key]:
                                            all_links.append(str(obj[link_key]))

                item['links'] = all_links
                item['custom_data'] = json_data

            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                item['title'] = f"API Response from {urlparse(response.url).netloc}"
                item['text_content'] = response.text
                item['text_length'] = len(response.text)
                item['html_content'] = response.body.decode('utf-8', errors='ignore')
                item['links'] = []
                item['custom_data'] = {'error': 'Failed to parse JSON'}
        else:
            # Handle HTML response (original logic)
            item['title'] = response.css('title::text').get()
            item['text_content'] = response.text
            item['text_length'] = len(response.text)
            item['html_content'] = response.body.decode('utf-8', errors='ignore')

            # Special handling for Yahoo Finance URLs - extract HTML with CSS selector
            if 'finance.yahoo.com' in response.url:
                # Use 'html' CSS selector to extract the complete HTML content
                html_selector_content = response.css('html').get()
                if html_selector_content:
                    item['html_content'] = html_selector_content
                    # Initialize custom_data if not exists
                    if 'custom_data' not in item:
                        item['custom_data'] = {}
                    item['custom_data']['css_selector_used'] = 'html'
                    item['custom_data']['yahoo_finance_html'] = html_selector_content

            # Links extraction
            all_links = response.css('a::attr(href)').getall()
            item['links'] = all_links

        # Separate internal and external links (only for HTML responses with actual links)
        if not is_json or (is_json and item['links']):
            parsed_url = urlparse(response.url)
            base_domain = parsed_url.netloc
            internal_links = []
            external_links = []

            for link in item['links']:
                if link.startswith(('http://', 'https://')):
                    link_domain = urlparse(link).netloc
                    if link_domain == base_domain:
                        internal_links.append(link)
                    else:
                        external_links.append(link)
                else:
                    internal_links.append(link)

            item['internal_links'] = internal_links
            item['external_links'] = external_links
        else:
            item['internal_links'] = []
            item['external_links'] = []

        # Metadata
        item['scraped_at'] = datetime.now().isoformat()
        item['user_agent'] = response.request.headers.get('User-Agent', b'').decode('utf-8')

        # Initialize optional fields if not set
        if 'custom_data' not in item:
            item['custom_data'] = {}
        item['error_message'] = None
        item['retry_count'] = 0

        # Handle different output formats
        if self.output_format == 'html':
            # For HTML output, yield only the HTML content
            yield {'html_content': item['html_content'], 'url': item['url'], 'title': item['title']}
        else:
            # For JSON output, yield the full item
            yield item
