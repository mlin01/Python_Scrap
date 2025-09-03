#!/usr/bin/env python3
"""
Smart Financial Scraper - Hybrid approach
Fast requests first, falls back to Selenium if needed
"""

import time
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
from datetime import datetime
import re

# Import our existing scrapers
from generic_financial_scraper import GenericFinancialScraper
from website_configs import get_config_for_url

def get_html_fast(url):
    """
    Simple fast HTML retrieval using requests
    Returns: (html_content, success, duration)
    """
    import requests
    
    start_time = time.time()
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        print(f"📡 Making HTTP request to: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        duration = time.time() - start_time
        html_content = response.text
        
        print(f"✅ Successfully retrieved HTML in {duration:.2f}s")
        print(f"📄 Content length: {len(html_content):,} characters")
        
        return html_content, True, duration
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ Failed to retrieve HTML: {str(e)}")
        return None, False, duration

def detect_financial_data(soup):
    """
    Detect if the page contains actual financial data or just empty containers
    Returns (has_data, data_type, data_count)
    """
    indicators = {
        'dividend_data': 0,
        'financial_tables': 0,
        'price_data': 0,
        'total_elements': 0
    }
    
    # Check for dividend-specific data
    dividend_patterns = [
        r'\$?\d+\.\d{2,3}',  # Dollar amounts like $0.51, 0.51
        r'dividend',
        r'yield',
        r'payout',
        r'ex-date',
        r'quarterly',
        r'annual'
    ]
    
    text_content = soup.get_text().lower()
    
    # Count dividend indicators
    for pattern in dividend_patterns:
        matches = re.findall(pattern, text_content)
        if 'dividend' in pattern:
            indicators['dividend_data'] += len(matches) * 3  # Higher weight
        else:
            indicators['dividend_data'] += len(matches)
    
    # Check for financial tables
    tables = soup.find_all('table')
    indicators['financial_tables'] = len(tables)
    
    # Check for financial data rows
    financial_rows = soup.find_all(['tr', 'td'], class_=re.compile(r'(financial|dividend|price|data|value)'))
    indicators['total_elements'] = len(financial_rows)
    
    # Check for specific numeric patterns that indicate financial data
    price_patterns = [
        r'\$\d+\.\d{2}',  # $123.45
        r'\d+\.\d{2}%',   # 12.34%
        r'\d{1,3}(,\d{3})*\.\d{2}'  # 1,234.56
    ]
    
    for pattern in price_patterns:
        matches = re.findall(pattern, text_content)
        indicators['price_data'] += len(matches)
    
    # Calculate total score
    total_score = (
        indicators['dividend_data'] * 2 +  # Weight dividend data higher
        indicators['financial_tables'] * 5 +
        indicators['price_data'] * 3 +
        indicators['total_elements']
    )
    
    # Determine if we have meaningful data
    has_data = total_score > 20  # Threshold for meaningful financial data
    
    return has_data, indicators, total_score
    """
    Detect if the page contains actual financial data or just empty containers
    Returns (has_data, data_type, data_count)
    """
    indicators = {
        'dividend_data': 0,
        'financial_tables': 0,
        'price_data': 0,
        'total_elements': 0
    }
    
    # Check for dividend-specific data
    dividend_patterns = [
        r'\$?\d+\.\d{2,3}',  # Dollar amounts like $0.51, 0.51
        r'dividend',
        r'yield',
        r'payout',
        r'ex-date',
        r'quarterly',
        r'annual'
    ]
    
    text_content = soup.get_text().lower()
    
    # Count dividend indicators
    for pattern in dividend_patterns:
        matches = re.findall(pattern, text_content)
        if 'dividend' in pattern:
            indicators['dividend_data'] += len(matches) * 3  # Higher weight
        else:
            indicators['dividend_data'] += len(matches)
    
    # Check for financial tables
    tables = soup.find_all('table')
    indicators['financial_tables'] = len(tables)
    
    # Check for financial data rows
    financial_rows = soup.find_all(['tr', 'td'], class_=re.compile(r'(financial|dividend|price|data|value)'))
    indicators['total_elements'] = len(financial_rows)
    
    # Check for specific numeric patterns that indicate financial data
    price_patterns = [
        r'\$\d+\.\d{2}',  # $123.45
        r'\d+\.\d{2}%',   # 12.34%
        r'\d{1,3}(,\d{3})*\.\d{2}'  # 1,234.56
    ]
    
    for pattern in price_patterns:
        matches = re.findall(pattern, text_content)
        indicators['price_data'] += len(matches)
    
    # Calculate total score
    total_score = (
        indicators['dividend_data'] * 2 +  # Weight dividend data higher
        indicators['financial_tables'] * 5 +
        indicators['price_data'] * 3 +
        indicators['total_elements']
    )
    
    # Determine if we have meaningful data
    has_data = total_score > 20  # Threshold for meaningful financial data
    
    return has_data, indicators, total_score

def smart_scrape(url, output_format='html', max_wait_time=30):
    """
    Smart scraping approach:
    1. Try fast requests method first
    2. Check if we got meaningful financial data
    3. If not, fall back to Selenium method
    Returns: (html_content, method_used, duration, filename)
    """
    print(f"\n🚀 Smart Scraper Starting for: {url}")
    start_time = time.time()
    
    # Step 1: Try fast method
    print("\n📊 Step 1: Trying fast requests method...")
    fast_start = time.time()
    
    try:
        html_content, success, request_time = get_html_fast(url)
        fast_time = time.time() - fast_start
        
        if html_content and success:
            soup = BeautifulSoup(html_content, 'html.parser')
            has_data, indicators, score = detect_financial_data(soup)
            
            print(f"⚡ Fast method completed in {fast_time:.2f}s")
            print(f"📈 Data quality score: {score}")
            print(f"   - Dividend indicators: {indicators['dividend_data']}")
            print(f"   - Financial tables: {indicators['financial_tables']}")
            print(f"   - Price data points: {indicators['price_data']}")
            print(f"   - Total elements: {indicators['total_elements']}")
            
            if has_data:
                print("✅ Fast method found sufficient financial data!")
                
                # Save output
                domain = urlparse(url).netloc.replace('www.', '')
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"smart_fast_{domain}_{timestamp}.html"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"💾 Fast HTML saved to: {filename}")
                
                total_time = time.time() - start_time
                print(f"\n🎉 Smart scraper completed successfully in {total_time:.2f}s using FAST method")
                return html_content, 'fast', total_time, filename
            
            else:
                print("⚠️  Fast method found insufficient financial data (likely JavaScript-dependent)")
                print("🔄 Falling back to Selenium method...")
        
    except Exception as e:
        print(f"❌ Fast method failed: {str(e)}")
        print("🔄 Falling back to Selenium method...")
    
    # Step 2: Fall back to Selenium method
    print("\n🌐 Step 2: Using Selenium method for JavaScript-heavy content...")
    selenium_start = time.time()
    
    try:
        # Get site configuration
        config_dict = get_config_for_url(url)
        scraping_config = config_dict['scraping_config']
        extraction_config = config_dict['extraction_config']
        
        # Initialize Selenium scraper
        scraper = GenericFinancialScraper(scraping_config, extraction_config)
        
        # Perform scraping
        result = scraper.scrape_url(url)
        selenium_time = time.time() - selenium_start
        
        if result.success:
            print(f"✅ Selenium method completed in {selenium_time:.2f}s")
            
            # Save output
            domain = urlparse(url).netloc.replace('www.', '')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"smart_selenium_{domain}_{timestamp}.html"
            
            raw_html = result.html_content
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(raw_html)
            print(f"💾 Selenium HTML saved to: {filename}")
            
            total_time = time.time() - start_time
            print(f"\n🎉 Smart scraper completed successfully in {total_time:.2f}s using SELENIUM method")
            return raw_html, 'selenium', total_time, filename
        
        else:
            print(f"❌ Selenium method failed: {', '.join(result.errors) if result.errors else 'Unknown error'}")
            return None, 'failed', time.time() - start_time, None
    
    except Exception as e:
        print(f"❌ Selenium method failed: {str(e)}")
        return None, 'failed', time.time() - start_time, None
    
    finally:
        # Clean up
        try:
            scraper.cleanup()
        except:
            pass

def analyze_method_performance(url, iterations=1):
    """
    Analyze and compare both methods' performance
    """
    print(f"\n📊 Performance Analysis for: {url}")
    print("=" * 60)
    
    results = []
    
    for i in range(iterations):
        print(f"\n🔄 Iteration {i+1}/{iterations}")
        
        html_content, method, duration, filename = smart_scrape(url)
        
        results.append({
            'iteration': i+1,
            'method': method,
            'duration': duration,
            'success': html_content is not None,
            'filename': filename,
            'content_length': len(html_content) if html_content else 0
        })
        
        print(f"   Result: {method} method in {duration:.2f}s")
        if html_content:
            print(f"   Content: {len(html_content):,} characters")
    
    # Summary
    print(f"\n📈 Performance Summary:")
    print("-" * 40)
    
    fast_results = [r for r in results if r['method'] == 'fast']
    selenium_results = [r for r in results if r['method'] == 'selenium']
    
    if fast_results:
        avg_fast = sum(r['duration'] for r in fast_results) / len(fast_results)
        avg_content = sum(r['content_length'] for r in fast_results) / len(fast_results)
        print(f"🚀 Fast method: {len(fast_results)} runs, avg {avg_fast:.2f}s, avg {avg_content:,.0f} chars")
    
    if selenium_results:
        avg_selenium = sum(r['duration'] for r in selenium_results) / len(selenium_results)
        avg_content = sum(r['content_length'] for r in selenium_results) / len(selenium_results)
        print(f"🌐 Selenium method: {len(selenium_results)} runs, avg {avg_selenium:.2f}s, avg {avg_content:,.0f} chars")
    
    success_rate = sum(1 for r in results if r['success']) / len(results)
    print(f"✅ Overall success rate: {success_rate:.1%}")
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python smart_scraper.py <url> [analysis_mode]")
        print("  url: URL to scrape")
        print("  analysis_mode: 'analyze' for performance comparison (default: single run)")
        print("\nExamples:")
        print("  python smart_scraper.py \"https://www.morningstar.com/stocks/xnas/aapl/dividends\"")
        print("  python smart_scraper.py \"https://finance.yahoo.com/quote/AAPL\"")
        print("  python smart_scraper.py \"https://www.morningstar.com/stocks/xnas/aapl/dividends\" analyze")
        sys.exit(1)
    
    url = sys.argv[1]
    analysis_mode = sys.argv[2] if len(sys.argv) > 2 else 'single'
    
    if analysis_mode.lower() == 'analyze':
        analyze_method_performance(url, iterations=3)
    else:
        html_content, method, duration, filename = smart_scrape(url)
        
        if html_content:
            print(f"\n✅ Success! Method: {method}, Duration: {duration:.2f}s")
            print(f"📄 Content length: {len(html_content):,} characters")
            if filename:
                print(f"📁 Output saved to: {filename}")
            return html_content
        else:
            print(f"\n❌ Failed to scrape {url}")
            sys.exit(1)

if __name__ == "__main__":
    main()
