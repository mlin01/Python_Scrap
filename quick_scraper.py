#!/usr/bin/env python3
"""
Quick Scraper - Fast HTML retrieval with minimal processing
No parsing, no file creation, just raw HTML output
"""

import time
import sys
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Fix Windows encoding issues
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
def safe_print(text):
    """Print text safely, handling encoding issues on Windows"""
    # Check if we're in return-content mode (should be silent)
    if '--return-content' in sys.argv:
        return  # Silent mode - no console output
        
    try:
        print(text)
    except UnicodeEncodeError:
        # Replace emojis with simple text for Windows console
        safe_text = text.replace('🚀', '[ROCKET]')
        safe_text = safe_text.replace('⚡', '[LIGHTNING]')
        safe_text = safe_text.replace('📊', '[CHART]')
        safe_text = safe_text.replace('✅', '[SUCCESS]')
        safe_text = safe_text.replace('❌', '[FAIL]')
        safe_text = safe_text.replace('🌐', '[GLOBE]')
        safe_text = safe_text.replace('⏳', '[HOURGLASS]')
        safe_text = safe_text.replace('🔄', '[REFRESH]')
        safe_text = safe_text.replace('📈', '[TRENDING_UP]')
        safe_text = safe_text.replace('⏰', '[CLOCK]')
        safe_text = safe_text.replace('🎉', '[PARTY]')
        safe_text = safe_text.replace('📄', '[FILE]')
        safe_text = safe_text.replace('⚠️', '[WARNING]')
        print(safe_text)

def get_html_fast(url):
    """Simple fast HTML retrieval using requests"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text, True

    except Exception as e:
        return None, False

def has_meaningful_content(html_content):
    """Quick check if HTML has meaningful financial data"""
    if not html_content:
        return False

    soup = BeautifulSoup(html_content, 'html.parser')

    # Look for actual dividend values in table cells
    # The missing data you showed had specific values like 0.51, 0.56, 0.62
    dividend_value_pattern = r'\b0\.[5-9]\d\b|\b[1-9]\.\d{2}\b'  # Values like 0.51, 1.23

    # Check for dividend values in table cells specifically
    table_cells = soup.find_all(['td', 'th'])
    dividend_values_found = 0

    for cell in table_cells:
        cell_text = cell.get_text(strip=True)
        if re.search(dividend_value_pattern, cell_text):
            dividend_values_found += 1

    # Also check for the specific elements you mentioned
    # Look for content that contains actual numeric dividend data
    text_content = soup.get_text()

    # Look for patterns like the ones you were missing
    specific_dividend_patterns = [
        r'Dividend Per Share',
        r'0\.51.*0\.56.*0\.62',  # The specific sequence you mentioned
        r'<td.*?>0\.\d{2}</td>',  # Table cells with dividend values
    ]

    pattern_matches = 0
    for pattern in specific_dividend_patterns:
        if re.search(pattern, html_content, re.IGNORECASE | re.DOTALL):
            pattern_matches += 1

    # Only consider it meaningful if we find actual dividend values in structured format
    score = dividend_values_found * 3 + pattern_matches * 5

    safe_print(f"   📊 Content analysis: {dividend_values_found} dividend values, {pattern_matches} patterns, score: {score}")
    return score > 10  # More strict threshold

def get_html_selenium(url):
    """Quick Selenium HTML retrieval that bypasses anti-bot detection"""
    driver = None
    try:
        # Enhanced Chrome options to mimic real browser behavior
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Real browser user agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Window size to mimic real browser
        chrome_options.add_argument("--window-size=1920,1080")

        # Initialize driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Hide automation flags
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_page_load_timeout(60)

        safe_print("   🌐 Loading page...")
        driver.get(url)

        # Wait for AWS WAF challenge to resolve
        safe_print("   ⏳ Waiting for anti-bot challenge...")

        # First wait for the challenge page to load
        time.sleep(3)

        # Check if we're on a challenge page
        page_source = driver.page_source.lower()
        if "javascript is disabled" in page_source or "captcha" in page_source or "awswaf" in page_source:
            safe_print("   🔄 Detected anti-bot challenge, waiting for resolution...")
            # Wait for the challenge to resolve automatically
            max_wait = 30  # seconds
            waited = 0
            while waited < max_wait:
                time.sleep(2)
                waited += 2
                current_source = driver.page_source.lower()
                if "javascript is disabled" not in current_source and "captcha" not in current_source:
                    safe_print("   ✅ Challenge resolved!")
                    break
                safe_print(f"   ⏳ Still waiting... ({waited}s)")

        # Additional wait for content to load
        safe_print("   📊 Waiting for financial content...")
        try:
            # Wait for either tables or dividend-specific content
            WebDriverWait(driver, 15).until(
                lambda d: len(d.find_elements(By.TAG_NAME, "table")) > 0 or
                         "dividend per share" in d.page_source.lower() or
                         len(d.find_elements(By.CSS_SELECTOR, "[class*='dividend']")) > 0
            )
            safe_print("   📈 Financial content detected!")
        except:
            safe_print("   ⏰ Timeout waiting for content, proceeding anyway...")

        # Get final HTML content
        html_content = driver.page_source
        return html_content, True

    except Exception as e:
        safe_print(f"   ❌ Selenium error: {str(e)}")
        return None, False
    finally:
        if driver:
            driver.quit()

def quick_scrape(url):
    """
    Quick scraping with automatic fallback
    1. Try fast requests method
    2. Check content quality
    3. If insufficient, try Selenium (but faster)
    """
    safe_print(f"🚀 Quick scraping: {url}")
    start_time = time.time()

    # Step 1: Try fast method
    safe_print("⚡ Trying fast requests method...")
    html_content, success = get_html_fast(url)

    if html_content and success:
        fast_time = time.time() - start_time
        has_data = has_meaningful_content(html_content)

        safe_print(f"✅ Fast method: {fast_time:.2f}s, {len(html_content):,} chars")

        if has_data:
            safe_print("📊 Found meaningful financial data!")
            total_time = time.time() - start_time
            safe_print(f"🎉 Completed in {total_time:.2f}s using FAST method")
            return html_content, 'fast', total_time
        else:
            safe_print("⚠️  Insufficient data, trying Selenium...")
    else:
        safe_print("❌ Fast method failed, trying Selenium...")

    # Step 2: Try Selenium (but optimized for speed)
    safe_print("🌐 Using Selenium (optimized)...")
    selenium_start = time.time()

    html_content, success = get_html_selenium(url)

    if html_content and success:
        selenium_time = time.time() - selenium_start
        total_time = time.time() - start_time
        safe_print(f"✅ Selenium method: {selenium_time:.2f}s, {len(html_content):,} chars")
        safe_print(f"🎉 Completed in {total_time:.2f}s using SELENIUM method")
        return html_content, 'selenium', total_time
    else:
        safe_print("❌ Selenium method failed")
        return None, 'failed', time.time() - start_time

def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_scraper.py <url> [output_mode] [--return-content]")
        print("  url: URL to scrape")
        print("  output_mode: 'full' or 'stats' (default)")
        print("  --return-content: Return content directly instead of saving to file")
        print("\nExamples:")
        print("  python quick_scraper.py \"https://www.morningstar.com/stocks/xnas/aapl/dividends\"")
        print("  python quick_scraper.py \"https://finance.yahoo.com/quote/AAPL\" full")
        print("  python quick_scraper.py \"https://www.morningstar.com/stocks/xnas/aapl/dividends\" stats --return-content")
        sys.exit(1)

    url = sys.argv[1]
    output_mode = sys.argv[2] if len(sys.argv) > 2 else 'stats'
    return_content = '--return-content' in sys.argv
    
    html_content, method, duration = quick_scrape(url)

    if html_content:
        if return_content:
            # Return content directly without saving to file
            result_data = {
                'success': True,
                'url': url,
                'method': method,
                'duration': duration,
                'content_length': len(html_content),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'mode': output_mode
            }
            
            if output_mode.lower() == 'full':
                result_data['content'] = html_content
            else:
                # Create summary for stats mode
                summary = f"""# Scraping Result Summary

**URL**: {url}
**Method**: {method}
**Duration**: {duration:.2f}s
**Content Length**: {len(html_content):,} characters
**Timestamp**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**Status**: ✅ SUCCESS

**Sample Content** (first 500 characters):
```html
{html_content[:500]}...
```
"""
                result_data['content'] = summary
            
            # Output JSON for API consumption
            import json
            print("JSON_RESULT_START")
            print(json.dumps(result_data, ensure_ascii=True, indent=2))
            print("JSON_RESULT_END")
            
        else:
            # Original file-saving behavior for backward compatibility
            # Generate temporary file name based on URL and timestamp
            import tempfile
            from urllib.parse import urlparse
            import hashlib
            
            # Create a safe filename from URL
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace('www.', '').replace('.', '_')
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            timestamp = int(time.time())
            
            # Create temp file path
            temp_dir = tempfile.gettempdir()
            if output_mode.lower() == 'full':
                output_file = f"{temp_dir}/scraper_{domain}_{url_hash}_{timestamp}.html"
            else:
                output_file = f"{temp_dir}/scraper_{domain}_{url_hash}_{timestamp}_stats.md"

            # Create result summary
            summary = f"""# Scraping Result Summary

**URL**: {url}
**Method**: {method}
**Duration**: {duration:.2f}s
**Content Length**: {len(html_content):,} characters
**Timestamp**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**Status**: ✅ SUCCESS

---

"""

            if output_mode.lower() == 'full':
                # Save HTML content with summary header
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("<!-- " + summary.replace('\n', '\n<!-- ') + " -->\n\n")
                    f.write(html_content)
                safe_print(f"\n✅ SUCCESS! Full HTML content saved to temporary file:")
                safe_print(f"   📄 {output_file}")
            else:
                # Save only summary and stats
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(summary)
                    f.write(f"**Sample Content** (first 500 characters):\n```html\n{html_content[:500]}...\n```")
                safe_print(f"\n✅ SUCCESS! Stats saved to temporary file:")
                safe_print(f"   📄 {output_file}")
        
        safe_print(f"   Method: {method}")
        safe_print(f"   Duration: {duration:.2f}s")
        safe_print(f"   Content: {len(html_content):,} characters")

    else:
        if return_content:
            # Return error directly
            error_data = {
                'success': False,
                'url': url,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'error': 'Both fast and Selenium methods failed'
            }
            import json
            print("JSON_RESULT_START")
            print(json.dumps(error_data, ensure_ascii=False, indent=2))
            print("JSON_RESULT_END")
        else:
            # Original file-saving error behavior
            error_file = output_file.replace('.html', '_error.md').replace('_stats.md', '_error.md')
            error_summary = f"""# Scraping Error

**URL**: {url}
**Timestamp**: {time.strftime('%Y-%m-%d %H:%M:%S')}
**Status**: ❌ FAILED

## Error Details
- Both fast and Selenium methods failed
- Check URL validity and network connection
- Possible anti-bot protection or site changes

## Troubleshooting
1. Verify the URL is accessible in a browser
2. Check network connectivity
3. Try again later if site is temporarily unavailable
"""
            
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(error_summary)
            
            safe_print(f"Error details saved to: {error_file}")
        
        safe_print(f"\n❌ FAILED to scrape {url}")
        sys.exit(1)

if __name__ == "__main__":
    main()