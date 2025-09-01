#!/usr/bin/env python3
"""
Simple command-line scraper using direct Python module calls
This script provides an alternative to the main scraper.py that doesn't require PATH setup
"""

import sys
import os
from pathlib import Path

def run_scraper(url, output_format='json', spider_name='universal'):
    """Run the scraper with specified parameters"""
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent.absolute()
    project_dir = script_dir / 'universal_scraper'
    
    # Change to the scrapy project directory
    original_cwd = os.getcwd()
    os.chdir(project_dir)
    
    # Add the project directory to Python path
    sys.path.insert(0, str(project_dir))
    
    try:
        # Import scrapy modules
        from scrapy.crawler import CrawlerProcess
        from scrapy.utils.project import get_project_settings
        
        # Get project settings
        settings = get_project_settings()
        settings.set('ROBOTSTXT_OBEY', False)
        settings.set('LOG_LEVEL', 'INFO')
        
        # Create crawler process
        process = CrawlerProcess(settings)
        
        # Add spider with parameters
        process.crawl(spider_name, url=url, format=output_format)
        
        # Start the crawling process
        process.start(stop_after_crawl=True)
        
        print(f"\n✅ Scraping completed successfully!")
        print(f"URL: {url}")
        print(f"Format: {output_format}")
        print(f"Spider: {spider_name}")
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return False
    
    finally:
        # Restore original working directory
        os.chdir(original_cwd)
        # Remove from Python path
        if str(project_dir) in sys.path:
            sys.path.remove(str(project_dir))
    
    return True

def main():
    """Main function with command-line argument parsing"""
    
    if len(sys.argv) < 2:
        print("📚 Universal Web Scraper - Python Module Version")
        print("="*50)
        print("Usage:")
        print("  python simple_scraper.py <url> [format] [spider]")
        print()
        print("Arguments:")
        print("  url      - URL to scrape (required)")
        print("  format   - Output format: 'json' or 'html' (default: json)")
        print("  spider   - Spider to use: 'universal' or 'selenium_spider' (default: universal)")
        print()
        print("Examples:")
        print("  python simple_scraper.py https://example.com")
        print("  python simple_scraper.py https://example.com json")
        print("  python simple_scraper.py https://example.com html universal")
        print("  python simple_scraper.py https://dynamic-site.com json selenium_spider")
        print()
        sys.exit(1)
    
    # Parse command-line arguments
    url = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else 'json'
    spider_name = sys.argv[3] if len(sys.argv) > 3 else 'universal'
    
    # Validate arguments
    if output_format not in ['json', 'html']:
        print("❌ Error: Format must be 'json' or 'html'")
        sys.exit(1)
    
    if spider_name not in ['universal', 'selenium_spider']:
        print("❌ Error: Spider must be 'universal' or 'selenium_spider'")
        sys.exit(1)
    
    # Auto-detect if JavaScript spider is needed
    javascript_sites = [
        'finance.yahoo.com', 'twitter.com', 'facebook.com',
        'instagram.com', 'linkedin.com', 'reddit.com'
    ]
    
    if spider_name == 'universal' and any(site in url for site in javascript_sites):
        print(f"🤖 Auto-detected JavaScript-heavy site, switching to selenium_spider")
        spider_name = 'selenium_spider'
    
    print(f"🚀 Starting scraper...")
    print(f"URL: {url}")
    print(f"Format: {output_format}")
    print(f"Spider: {spider_name}")
    print("-" * 50)
    
    # Run the scraper
    success = run_scraper(url, output_format, spider_name)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
