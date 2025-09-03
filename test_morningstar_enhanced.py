#!/usr/bin/env python3
"""
Enhanced test script for scraping Morningstar AAPL dividends page
This script tests scraping and saves results to files for analysis
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime

def test_morningstar_with_output():
    """Test scraping Morningstar AAPL dividends page and save output"""
    
    url = "https://www.morningstar.com/stocks/xnas/aapl/dividends"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"morningstar_aapl_dividends_{timestamp}.json"
    
    print("🧪 Testing Morningstar AAPL Dividends Page Scraping with File Output")
    print("=" * 70)
    print(f"Target URL: {url}")
    print(f"Output file: {output_file}")
    print()
    
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
        
        # Get project settings with file output
        settings = get_project_settings()
        settings.set('ROBOTSTXT_OBEY', True)
        settings.set('DOWNLOAD_DELAY', 3)
        settings.set('LOG_LEVEL', 'INFO')
        settings.set('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Set feed exports to save to file
        settings.set('FEEDS', {
            output_file: {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'indent': 2
            }
        })
        
        # Create crawler process
        process = CrawlerProcess(settings)
        
        # Add spider with parameters
        process.crawl('universal', url=url)
        
        # Start the crawling process
        process.start(stop_after_crawl=True)
        
        print("✅ Scraping completed successfully!")
        
        # Move output file to parent directory for easier access
        if os.path.exists(output_file):
            import shutil
            dest_path = original_cwd + "\\" + output_file
            shutil.move(output_file, dest_path)
            print(f"📁 Output file moved to: {dest_path}")
            
            # Analyze the scraped data
            analyze_scraped_data(dest_path)
        else:
            print("⚠️  Output file not found")
        
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Restore original working directory
        os.chdir(original_cwd)
        # Remove from Python path
        if str(project_dir) in sys.path:
            sys.path.remove(str(project_dir))

def analyze_scraped_data(file_path):
    """Analyze the scraped data for financial information"""
    print()
    print("📊 Analyzing Scraped Data for Financial Information")
    print("-" * 50)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list) and len(data) > 0:
            item = data[0]
        else:
            item = data
        
        print(f"🔍 URL: {item.get('url', 'N/A')}")
        print(f"📄 Title: {item.get('title', 'N/A')}")
        print(f"📏 Content Length: {item.get('text_length', 0):,} characters")
        print(f"🔗 Total Links: {item.get('total_links', 0)}")
        print(f"⏰ Scraped At: {item.get('scraped_at', 'N/A')}")
        print()
        
        # Analyze text content for dividend-related keywords
        text_content = item.get('text_content', '').lower()
        
        dividend_keywords = [
            'dividend', 'yield', 'ex-dividend', 'payment date', 
            'quarterly', 'annual', 'per share', '$', 'cents',
            'payout', 'distribution', 'record date'
        ]
        
        found_keywords = []
        for keyword in dividend_keywords:
            if keyword in text_content:
                found_keywords.append(keyword)
        
        print(f"💰 Dividend-related keywords found: {len(found_keywords)}/{len(dividend_keywords)}")
        print(f"   Keywords: {', '.join(found_keywords) if found_keywords else 'None'}")
        print()
        
        # Look for specific dividend information patterns
        import re
        
        # Look for dollar amounts
        dollar_patterns = re.findall(r'\$\d+\.?\d*', text_content)
        if dollar_patterns:
            print(f"💵 Dollar amounts found: {dollar_patterns[:10]}...")  # Show first 10
        
        # Look for percentage patterns (for yield)
        percent_patterns = re.findall(r'\d+\.?\d*%', text_content)
        if percent_patterns:
            print(f"📈 Percentage values found: {percent_patterns[:10]}...")  # Show first 10
        
        # Look for dates
        date_patterns = re.findall(r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}', text_content)
        if date_patterns:
            print(f"📅 Dates found: {date_patterns[:10]}...")  # Show first 10
        
        print()
        
        # Check if the content suggests JavaScript is needed
        js_indicators = ['loading', 'javascript', 'enable javascript', 'noscript']
        needs_js = any(indicator in text_content for indicator in js_indicators)
        
        if needs_js:
            print("⚠️  JavaScript may be required for full content")
        else:
            print("✅ Static HTML scraping appears sufficient")
        
        # Save analysis summary
        summary_file = file_path.replace('.json', '_analysis.txt')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Morningstar AAPL Dividends Analysis\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Source: {item.get('url', 'N/A')}\n\n")
            f.write(f"Content Statistics:\n")
            f.write(f"- Title: {item.get('title', 'N/A')}\n")
            f.write(f"- Text Length: {item.get('text_length', 0):,} characters\n")
            f.write(f"- Total Links: {item.get('total_links', 0)}\n\n")
            f.write(f"Dividend Keywords Found: {', '.join(found_keywords) if found_keywords else 'None'}\n\n")
            if dollar_patterns:
                f.write(f"Dollar Amounts: {', '.join(dollar_patterns[:20])}\n\n")
            if percent_patterns:
                f.write(f"Percentages: {', '.join(percent_patterns[:20])}\n\n")
            if date_patterns:
                f.write(f"Dates: {', '.join(date_patterns[:20])}\n\n")
        
        print(f"📝 Analysis summary saved to: {summary_file}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

def main():
    """Main function"""
    print("🚀 Starting Enhanced Morningstar AAPL Dividends Test")
    print()
    
    # Run the test
    test_morningstar_with_output()
    
    print()
    print("🎯 Test completed! Check the generated files for detailed results.")

if __name__ == "__main__":
    main()
