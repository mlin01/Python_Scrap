import scrapy
import json
from urllib.parse import urlparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from ..items import UniversalScraperItem


class SeleniumSpider(scrapy.Spider):
    name = "selenium_spider"

    def __init__(self, url=None, format='html', *args, **kwargs):
        super(SeleniumSpider, self).__init__(*args, **kwargs)
        if url:
            self.start_urls = [url]
        else:
            self.start_urls = ["https://example.com"]

        self.output_format = format.lower()
        self.url = url

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_with_selenium)

    def parse_with_selenium(self, response):
        # Set up Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        # Initialize the driver
        driver = None
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            # Navigate to the URL
            driver.get(self.url)

            # Wait for the page to load and JavaScript to execute
            # For Yahoo Finance, wait for specific elements that contain stock data
            if 'finance.yahoo.com' in self.url:
                try:
                    # Wait for the main quote container to load
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-symbol]"))
                    )
                    # Additional wait for dynamic content
                    time.sleep(3)
                except:
                    # If specific elements don't load, just wait a bit
                    time.sleep(5)

            # Get the fully rendered HTML
            html_content = driver.page_source

            # Handle different output formats
            if self.output_format == 'html':
                # For HTML output, yield only the HTML content
                yield {'html_content': html_content, 'url': self.url, 'title': driver.title if driver.title else f"Selenium scraped content from {urlparse(self.url).netloc}"}
            else:
                # For JSON output, yield the full item
                item = UniversalScraperItem()
                item['url'] = self.url
                item['status'] = 200  # Assume success if we got here
                item['response_headers'] = {'content-type': 'text/html'}
                item['title'] = driver.title if driver.title else f"Selenium scraped content from {urlparse(self.url).netloc}"
                item['text_content'] = html_content
                item['text_length'] = len(html_content)
                item['html_content'] = html_content
                item['links'] = []
                item['custom_data'] = {
                    'scraping_method': 'selenium',
                    'javascript_executed': True,
                    'timestamp': datetime.now().isoformat()
                }

                # Try to extract some basic info for Yahoo Finance
                if 'finance.yahoo.com' in self.url:
                    try:
                        # Extract stock symbol
                        symbol_element = driver.find_element(By.CSS_SELECTOR, "[data-symbol]")
                        if symbol_element:
                            item['custom_data']['symbol'] = symbol_element.get_attribute('data-symbol')

                        # Try to extract current price
                        price_selectors = [
                            "[data-testid='qsp-price']",
                            ".price",
                            "[data-field='regularMarketPrice']"
                        ]

                        for selector in price_selectors:
                            try:
                                price_element = driver.find_element(By.CSS_SELECTOR, selector)
                                if price_element and price_element.text.strip():
                                    item['custom_data']['current_price'] = price_element.text.strip()
                                    break
                            except:
                                continue

                    except Exception as e:
                        item['custom_data']['extraction_error'] = str(e)

                yield item

        except Exception as e:
            # Fallback: create item with error information
            if self.output_format == 'html':
                # For HTML output, yield error as HTML
                yield {'html_content': f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>", 'url': self.url, 'title': f"Error scraping {urlparse(self.url).netloc}"}
            else:
                # For JSON output, yield full error item
                item = UniversalScraperItem()
                item['url'] = self.url
                item['status'] = 500
                item['response_headers'] = {}
                item['title'] = f"Error scraping {urlparse(self.url).netloc}"
                item['text_content'] = f"Error: {str(e)}"
                item['text_length'] = len(item['text_content'])
                item['html_content'] = f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>"
                item['links'] = []
                item['custom_data'] = {
                    'scraping_method': 'selenium',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                yield item

        finally:
            if driver:
                driver.quit()
