#!/usr/bin/env python3
"""
Universal Web Scraper
Supports two output methods: JSON and HTML
"""

import sys
import os
from pathlib import Path

def scrape_json(url):
    """Scrape URL and return JSON data"""
    print(f"Scraping {url} for JSON output...")

    # Change to the scrapy project directory
    project_dir = os.path.join(os.path.dirname(__file__), 'universal_scraper')
    
    # Add the project directory to Python path
    sys.path.insert(0, project_dir)
    
    try:
        # Import scrapy modules
        from scrapy.crawler import CrawlerProcess
        from scrapy.utils.project import get_project_settings
        
        # Get project settings
        os.chdir(project_dir)
        settings = get_project_settings()
        settings.set('ROBOTSTXT_OBEY', False)
        settings.set('LOG_LEVEL', 'ERROR')  # Reduce log noise
        
        # Create crawler process
        process = CrawlerProcess(settings)
        
        # Add spider
        process.crawl('universal', url=url, format='json')
        
        # Start the crawling process
        process.start(stop_after_crawl=True)
        
        print("Scraping completed.")
        return "Scraping completed successfully", None
        
    except Exception as e:
        return None, str(e)

def scrape_html(url):
    """Scrape URL and return HTML content"""
    print(f"Scraping {url} for HTML output...")

    # Change to the scrapy project directory
    project_dir = os.path.join(os.path.dirname(__file__), 'universal_scraper')
    
    # Add the project directory to Python path
    sys.path.insert(0, project_dir)

    # Check if we need JavaScript execution for dynamic content
    needs_javascript = any(domain in url for domain in [
        'finance.yahoo.com',
        'twitter.com',
        'facebook.com',
        'instagram.com',
        'linkedin.com',
        'reddit.com'
    ])

    if needs_javascript:
        print("Detected site that requires JavaScript execution. Using Selenium spider...")
        spider_name = "selenium_spider"
    else:
        spider_name = "universal"

    try:
        # Import scrapy modules
        from scrapy.crawler import CrawlerProcess
        from scrapy.utils.project import get_project_settings
        
        # Get project settings
        os.chdir(project_dir)
        settings = get_project_settings()
        settings.set('ROBOTSTXT_OBEY', False)
        settings.set('LOG_LEVEL', 'ERROR')  # Reduce log noise
        
        # Create crawler process
        process = CrawlerProcess(settings)
        
        # Add spider
        process.crawl(spider_name, url=url, format='html')
        
        # Start the crawling process
        process.start(stop_after_crawl=True)
        
        print("Scraping completed.")
        return "Scraping completed successfully", None
        
    except Exception as e:
        return None, str(e)

def main():
    if len(sys.argv) < 3:
        print("Usage: python scraper.py <format> <url>")
        print("Formats: json, html")
        print("Example: python scraper.py json https://example.com")
        sys.exit(1)

    format_type = sys.argv[1].lower()
    url = sys.argv[2]

    if format_type not in ['json', 'html']:
        print("Error: Format must be 'json' or 'html'")
        sys.exit(1)

    if format_type == 'json':
        stdout, stderr = scrape_json(url)
    else:
        stdout, stderr = scrape_html(url)

    if stderr:
        print(f"Errors: {stderr}")

    if stdout:
        print(stdout)

if __name__ == "__main__":
    main()
