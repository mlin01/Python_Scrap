#!/usr/bin/env python3
"""
Fast Financial Scraper using Firecrawl
This provides a much faster alternative to Selenium for financial data scraping
"""

import time
import json
from datetime import datetime
from typing import Dict, Any, Optional

def scrape_with_firecrawl(url: str, output_format: str = 'json') -> str:
    """
    Fast scraping using Firecrawl - much faster than Selenium
    
    Args:
        url: URL to scrape
        output_format: 'json', 'html', or 'summary'
    
    Returns:
        Filename of saved results
    """
    
    print(f"⚡ Fast scraping with Firecrawl: {url}")
    start_time = time.time()
    
    try:
        # Try to import firecrawl
        try:
            from firecrawl import FirecrawlApp
        except ImportError:
            print("❌ Firecrawl not installed. Install with: pip install firecrawl-py")
            return ""
        
        # Initialize Firecrawl (you'll need to set up API key)
        app = FirecrawlApp(api_key="your-api-key-here")  # You need to get this from firecrawl.dev
        
        scrape_start = time.time()
        
        # Scrape the page
        result = app.scrape_url(url, params={
            'formats': ['markdown', 'html'],
            'includeTags': ['table', 'div', 'span'],
            'onlyMainContent': False
        })
        
        scrape_time = time.time() - scrape_start
        total_time = time.time() - start_time
        
        if result.get('success', False):
            print(f"✅ Successfully scraped in {total_time:.2f} seconds!")
            print(f"   ⚡ Firecrawl time: {scrape_time:.2f}s")
            print(f"   📄 Content length: {len(result.get('content', ''))}")
            
            # Save results based on format
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            domain = url.split('/')[2].replace('.', '_')
            
            if output_format == 'html':
                filename = f"firecrawl_{domain}_{timestamp}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(result.get('html', ''))
                    
            elif output_format == 'summary':
                filename = f"firecrawl_summary_{domain}_{timestamp}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Firecrawl Results Summary\n")
                    f.write(f"=" * 50 + "\n\n")
                    f.write(f"URL: {url}\n")
                    f.write(f"Scraped: {datetime.now().isoformat()}\n")
                    f.write(f"Total time: {total_time:.2f} seconds\n")
                    f.write(f"Content length: {len(result.get('content', ''))}\n\n")
                    f.write(f"Content:\n{result.get('markdown', result.get('content', ''))}")
                    
            else:  # json
                filename = f"firecrawl_{domain}_{timestamp}.json"
                enhanced_result = {
                    'url': url,
                    'scraped_at': datetime.now().isoformat(),
                    'method': 'firecrawl',
                    'timing': {
                        'total_time_seconds': round(total_time, 2),
                        'scrape_time_seconds': round(scrape_time, 2)
                    },
                    'content': result.get('content', ''),
                    'markdown': result.get('markdown', ''),
                    'html': result.get('html', ''),
                    'metadata': result.get('metadata', {})
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(enhanced_result, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Results saved to: {filename}")
            return filename
            
        else:
            print(f"❌ Firecrawl failed: {result.get('error', 'Unknown error')}")
            return ""
            
    except Exception as e:
        print(f"❌ Error with Firecrawl: {e}")
        return ""

def compare_scraping_methods(url: str) -> Dict[str, Any]:
    """
    Compare Selenium vs Firecrawl scraping performance
    """
    
    print(f"🏁 Performance Comparison: {url}")
    print("=" * 60)
    
    results = {
        'url': url,
        'comparison_time': datetime.now().isoformat(),
        'methods': {}
    }
    
    # Test Firecrawl (if available)
    print("\n⚡ Testing Firecrawl...")
    firecrawl_start = time.time()
    firecrawl_file = scrape_with_firecrawl(url, 'json')
    firecrawl_time = time.time() - firecrawl_start
    
    results['methods']['firecrawl'] = {
        'time_seconds': round(firecrawl_time, 2),
        'success': bool(firecrawl_file),
        'output_file': firecrawl_file
    }
    
    # Test Selenium (using our existing scraper)
    print("\n🐌 Testing Selenium...")
    selenium_start = time.time()
    
    try:
        from easy_scraper import scrape_any_url
        selenium_file = scrape_any_url(url, 'json')
        selenium_time = time.time() - selenium_start
        
        results['methods']['selenium'] = {
            'time_seconds': round(selenium_time, 2),
            'success': bool(selenium_file),
            'output_file': selenium_file
        }
        
    except Exception as e:
        selenium_time = time.time() - selenium_start
        results['methods']['selenium'] = {
            'time_seconds': round(selenium_time, 2),
            'success': False,
            'error': str(e)
        }
    
    # Summary
    print(f"\n📊 Performance Summary:")
    print("=" * 30)
    
    for method, data in results['methods'].items():
        if data['success']:
            print(f"{method.capitalize()}: {data['time_seconds']:.2f}s ✅")
        else:
            print(f"{method.capitalize()}: {data['time_seconds']:.2f}s ❌")
    
    # Speed comparison
    if (results['methods'].get('firecrawl', {}).get('success') and 
        results['methods'].get('selenium', {}).get('success')):
        
        firecrawl_time = results['methods']['firecrawl']['time_seconds']
        selenium_time = results['methods']['selenium']['time_seconds']
        speedup = selenium_time / firecrawl_time
        
        print(f"\n🚀 Firecrawl is {speedup:.1f}x faster than Selenium!")
    
    # Save comparison results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    comparison_file = f"speed_comparison_{timestamp}.json"
    
    with open(comparison_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Comparison saved to: {comparison_file}")
    return results

def setup_firecrawl():
    """
    Helper function to set up Firecrawl
    """
    
    print("🔧 Firecrawl Setup Instructions")
    print("=" * 40)
    print("1. Sign up at https://firecrawl.dev")
    print("2. Get your API key from the dashboard")
    print("3. Install: pip install firecrawl-py")
    print("4. Set your API key in this script or as environment variable")
    print()
    print("Environment variable setup:")
    print("  export FIRECRAWL_API_KEY='your-key-here'")
    print("  # or on Windows:")
    print("  set FIRECRAWL_API_KEY=your-key-here")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("🚀 Fast Financial Scraper with Firecrawl")
        print("=" * 45)
        print("Usage:")
        print("  python fast_scraper.py <url> [format]")
        print("  python fast_scraper.py compare <url>")
        print("  python fast_scraper.py setup")
        print()
        print("Examples:")
        print("  python fast_scraper.py https://www.morningstar.com/stocks/xnas/aapl/dividends")
        print("  python fast_scraper.py https://finance.yahoo.com/quote/AAPL html")
        print("  python fast_scraper.py compare https://www.morningstar.com/stocks/xnas/aapl/dividends")
        print("  python fast_scraper.py setup")
    
    elif sys.argv[1] == 'setup':
        setup_firecrawl()
    
    elif sys.argv[1] == 'compare' and len(sys.argv) >= 3:
        url = sys.argv[2]
        compare_scraping_methods(url)
    
    else:
        url = sys.argv[1]
        output_format = sys.argv[2] if len(sys.argv) >= 3 else 'json'
        scrape_with_firecrawl(url, output_format)
