#!/usr/bin/env python3
"""
Test script for scraping Morningstar AAPL dividends page
This script tests various scraping approaches and outputs results
"""

import sys
import os
import time
from pathlib import Path

def test_morningstar_scraping():
    """Test scraping Morningstar AAPL dividends page with different methods"""
    
    url = "https://www.morningstar.com/stocks/xnas/aapl/dividends"
    
    print("🧪 Testing Morningstar AAPL Dividends Page Scraping")
    print("=" * 60)
    print(f"Target URL: {url}")
    print()
    
    # Test 1: Simple scraper with universal spider
    print("📊 Test 1: Universal Spider (Basic HTML parsing)")
    print("-" * 50)
    
    try:
        from pathlib import Path
        script_dir = Path(__file__).parent.absolute()
        project_dir = script_dir / 'universal_scraper'
        
        # Change to the scrapy project directory
        original_cwd = os.getcwd()
        os.chdir(project_dir)
        
        # Add the project directory to Python path
        sys.path.insert(0, str(project_dir))
        
        # Import scrapy modules
        from scrapy.crawler import CrawlerProcess
        from scrapy.utils.project import get_project_settings
        
        # Get project settings with custom configuration for financial sites
        settings = get_project_settings()
        settings.set('ROBOTSTXT_OBEY', True)  # Respect robots.txt
        settings.set('DOWNLOAD_DELAY', 3)  # 3 seconds delay to be respectful
        settings.set('LOG_LEVEL', 'INFO')
        settings.set('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Create crawler process
        process = CrawlerProcess(settings)
        
        # Add spider with parameters
        process.crawl('universal', url=url, format='json')
        
        # Start the crawling process
        process.start(stop_after_crawl=True)
        
        print("✅ Universal spider test completed!")
        
    except Exception as e:
        print(f"❌ Universal spider test failed: {e}")
    
    finally:
        # Restore original working directory
        os.chdir(original_cwd)
        # Remove from Python path
        if str(project_dir) in sys.path:
            sys.path.remove(str(project_dir))
    
    print()
    
    # Wait a bit before next test to be respectful
    print("⏱️  Waiting 5 seconds before next test...")
    time.sleep(5)
    
    # Test 2: Selenium spider for JavaScript content
    print("🤖 Test 2: Selenium Spider (JavaScript rendering)")
    print("-" * 50)
    
    try:
        # Change to the scrapy project directory again
        os.chdir(project_dir)
        sys.path.insert(0, str(project_dir))
        
        # Import scrapy modules
        from scrapy.crawler import CrawlerProcess
        from scrapy.utils.project import get_project_settings
        
        # Get project settings optimized for JavaScript-heavy sites
        settings = get_project_settings()
        settings.set('ROBOTSTXT_OBEY', True)
        settings.set('DOWNLOAD_DELAY', 5)  # Longer delay for Selenium
        settings.set('LOG_LEVEL', 'INFO')
        settings.set('SELENIUM_HEADLESS', True)
        settings.set('SELENIUM_TIMEOUT', 30)
        
        # Create crawler process
        process = CrawlerProcess(settings)
        
        # Add selenium spider
        process.crawl('selenium_spider', url=url, format='json')
        
        # Start the crawling process
        process.start(stop_after_crawl=True)
        
        print("✅ Selenium spider test completed!")
        
    except Exception as e:
        print(f"❌ Selenium spider test failed: {e}")
        print("💡 Note: Selenium spider requires Chrome/Chromium and webdriver-manager")
    
    finally:
        # Restore original working directory
        os.chdir(original_cwd)
        if str(project_dir) in sys.path:
            sys.path.remove(str(project_dir))
    
    print()
    print("📋 Test Summary")
    print("-" * 20)
    print("• Both spiders tested with Morningstar AAPL dividends page")
    print("• Respectful scraping settings applied (delays, robots.txt)")
    print("• Check output above for scraped data")
    print("• Look for dividend-related content in the results")
    print()
    print("🔍 Expected data points:")
    print("  - Dividend yield")
    print("  - Dividend per share")
    print("  - Ex-dividend dates")
    print("  - Payment dates")
    print("  - Dividend history")
    print()
    print("⚠️  Important notes:")
    print("  - Morningstar may have anti-scraping measures")
    print("  - JavaScript rendering might be required for full content")
    print("  - Always respect the website's terms of service")
    print("  - Consider using official APIs when available")

def main():
    """Main function"""
    print("🚀 Starting Morningstar AAPL Dividends Test Suite")
    print()
    
    # Run the tests
    test_morningstar_scraping()
    
    print()
    print("🎯 Test completed! Check the output above for results.")

if __name__ == "__main__":
    main()
