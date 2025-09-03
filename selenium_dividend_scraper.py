#!/usr/bin/env python3
"""
Specialized Selenium-based scraper for Morningstar dividend data
This script addresses the specific issue of JavaScript-rendered dividend tables
"""

import time
import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def scrape_morningstar_dividends_with_selenium():
    """
    Use Selenium directly to scrape Morningstar dividend data
    This bypasses the Scrapy framework to have more control over JavaScript rendering
    """
    
    url = "https://www.morningstar.com/stocks/xnas/aapl/dividends"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("🎯 Direct Selenium Scraping for Morningstar Dividend Data")
    print("=" * 60)
    print(f"Target URL: {url}")
    print("Strategy: Wait for JavaScript to fully render dividend table")
    print()
    
    driver = None
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # User agent to appear more like a real browser
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Create Chrome driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("🤖 Chrome WebDriver started successfully")
        
        # Set page load timeout
        driver.set_page_load_timeout(30)
        
        # Navigate to the page
        print("🌐 Loading Morningstar page...")
        driver.get(url)
        
        # Wait for initial page load
        print("⏱️  Waiting for initial page load...")
        time.sleep(5)
        
        # Wait for Nuxt.js to finish loading
        print("⏱️  Waiting for JavaScript framework to initialize...")
        try:
            # Wait for the main content area to be present
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
            print("✅ Main content area loaded")
        except:
            print("⚠️  Main content area not found, continuing anyway...")
        
        # Wait for dividend-specific elements to load
        print("⏱️  Waiting for dividend data to load...")
        
        # Try multiple selectors that might contain dividend data
        dividend_selectors = [
            '[data-testid*="dividend"]',
            '[class*="dividend"]',
            'table',
            '[class*="table"]',
            '[role="table"]',
            '[class*="history"]',
            '[class*="data-table"]'
        ]
        
        dividend_elements_found = False
        for selector in dividend_selectors:
            try:
                elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
                if elements:
                    print(f"✅ Found {len(elements)} elements matching '{selector}'")
                    dividend_elements_found = True
                    break
            except:
                continue
        
        if not dividend_elements_found:
            print("⚠️  No specific dividend elements found, capturing all content...")
        
        # Additional wait for dynamic content
        print("⏱️  Waiting for dynamic content to fully render...")
        time.sleep(10)
        
        # Get page source after JavaScript execution
        html_content = driver.page_source
        page_title = driver.title
        
        print(f"📄 Page title: {page_title}")
        print(f"📏 HTML content length: {len(html_content):,} characters")
        
        # Extract text content
        body_element = driver.find_element(By.TAG_NAME, "body")
        text_content = body_element.text
        
        print(f"📏 Text content length: {len(text_content):,} characters")
        
        # Look for specific dividend-related content
        dividend_keywords = [
            'dividend history',
            'ex-dividend',
            'payment date',
            'quarterly dividend',
            'dividend yield',
            'ex date',
            'pay date',
            'record date'
        ]
        
        found_keywords = []
        for keyword in dividend_keywords:
            if keyword.lower() in text_content.lower():
                found_keywords.append(keyword)
        
        print(f"💰 Dividend keywords found: {found_keywords}")
        
        # Look for table structures
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"📊 Tables found: {len(tables)}")
        
        # Look for specific dividend data patterns
        dividend_amounts = re.findall(r'\$[0-9]+\.?[0-9]*', text_content)
        dividend_dates = re.findall(r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}', text_content)
        
        print(f"💵 Dividend amounts found: {len(dividend_amounts)}")
        print(f"📅 Date patterns found: {len(dividend_dates)}")
        
        if dividend_amounts:
            print(f"   Sample amounts: {dividend_amounts[:10]}")
        if dividend_dates:
            print(f"   Sample dates: {dividend_dates[:10]}")
        
        # Try to find specific dividend table data
        table_data = extract_table_data(driver)
        
        # Save results
        results = {
            'url': url,
            'title': page_title,
            'scraped_at': datetime.now().isoformat(),
            'html_content': html_content,
            'text_content': text_content,
            'text_length': len(text_content),
            'html_length': len(html_content),
            'dividend_keywords_found': found_keywords,
            'dividend_amounts': dividend_amounts[:50],  # Limit to first 50
            'dividend_dates': dividend_dates[:50],  # Limit to first 50
            'tables_count': len(tables),
            'table_data': table_data,
            'extraction_method': 'selenium_direct'
        }
        
        # Save to file
        output_file = f"morningstar_selenium_dividend_data_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {output_file}")
        
        # Analyze the extracted data
        analyze_selenium_results(results, output_file)
        
        return results
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return None
        
    finally:
        if driver:
            driver.quit()
            print("🔒 WebDriver closed")

def extract_table_data(driver):
    """Extract structured data from any tables found on the page"""
    table_data = []
    
    try:
        tables = driver.find_elements(By.TAG_NAME, "table")
        
        for i, table in enumerate(tables):
            print(f"📊 Analyzing table {i+1}...")
            
            table_info = {
                'table_index': i,
                'headers': [],
                'rows': []
            }
            
            # Extract headers
            try:
                header_elements = table.find_elements(By.TAG_NAME, "th")
                if header_elements:
                    table_info['headers'] = [th.text.strip() for th in header_elements]
                    print(f"   Headers: {table_info['headers']}")
            except:
                pass
            
            # Extract rows
            try:
                row_elements = table.find_elements(By.TAG_NAME, "tr")
                for j, row in enumerate(row_elements[:20]):  # Limit to first 20 rows
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if cells:
                        row_data = [cell.text.strip() for cell in cells]
                        table_info['rows'].append(row_data)
                        if j < 3:  # Show first 3 rows
                            print(f"   Row {j+1}: {row_data}")
            except:
                pass
            
            table_data.append(table_info)
            
            # Check if this looks like a dividend table
            headers_text = ' '.join(table_info['headers']).lower()
            if any(keyword in headers_text for keyword in ['dividend', 'ex', 'date', 'payment', 'amount']):
                print(f"   🎯 Table {i+1} appears to be dividend-related!")
    
    except Exception as e:
        print(f"❌ Error extracting table data: {e}")
    
    return table_data

def analyze_selenium_results(results, output_file):
    """Analyze the results from Selenium scraping"""
    print()
    print("📈 Selenium Results Analysis")
    print("-" * 40)
    
    # Basic stats
    print(f"📏 Content captured:")
    print(f"   HTML: {results['html_length']:,} characters")
    print(f"   Text: {results['text_length']:,} characters")
    print(f"   Tables: {results['tables_count']}")
    
    # Dividend data analysis
    print(f"💰 Dividend data found:")
    print(f"   Keywords: {len(results['dividend_keywords_found'])}")
    print(f"   Amounts: {len(results['dividend_amounts'])}")
    print(f"   Dates: {len(results['dividend_dates'])}")
    
    if results['dividend_keywords_found']:
        print(f"   Keywords: {', '.join(results['dividend_keywords_found'])}")
    
    # Table analysis
    if results['table_data']:
        print(f"📊 Table analysis:")
        for i, table in enumerate(results['table_data']):
            print(f"   Table {i+1}: {len(table['headers'])} headers, {len(table['rows'])} rows")
            if table['headers']:
                print(f"     Headers: {', '.join(table['headers'][:5])}")
    
    # Success assessment
    success_score = 0
    if results['dividend_keywords_found']:
        success_score += 2
    if results['dividend_amounts']:
        success_score += 2
    if results['dividend_dates']:
        success_score += 2
    if results['table_data']:
        success_score += 1
    if results['text_length'] > 100000:  # Substantial content
        success_score += 1
    
    print()
    print(f"🎯 Success Assessment: {success_score}/8")
    
    if success_score >= 6:
        print("✅ Excellent - Likely captured dividend data successfully")
    elif success_score >= 4:
        print("⚠️  Good - Some dividend data captured, may need refinement")
    elif success_score >= 2:
        print("⚠️  Fair - Limited dividend data, more work needed")
    else:
        print("❌ Poor - No clear dividend data captured")
    
    # Recommendations
    print()
    print("💡 Recommendations:")
    
    if success_score < 4:
        print("   🔧 Try increasing wait times for JavaScript rendering")
        print("   🔧 Look for API endpoints that directly provide dividend data")
        print("   🔧 Check if page requires user interaction (clicks, scrolling)")
    
    if not results['table_data']:
        print("   🔧 No tables found - dividend data might be in other structures")
        print("   🔧 Try looking for div-based pseudo-tables")
    
    if results['text_length'] < 50000:
        print("   🔧 Low text content suggests incomplete page loading")
        print("   🔧 Consider longer wait times or different loading strategies")
    
    # Save analysis
    analysis_file = output_file.replace('.json', '_analysis.txt')
    with open(analysis_file, 'w', encoding='utf-8') as f:
        f.write(f"Morningstar Selenium Scraping Analysis\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Source: {output_file}\n\n")
        
        f.write(f"CONTENT STATISTICS:\n")
        f.write(f"- HTML Length: {results['html_length']:,} characters\n")
        f.write(f"- Text Length: {results['text_length']:,} characters\n")
        f.write(f"- Tables Found: {results['tables_count']}\n\n")
        
        f.write(f"DIVIDEND DATA:\n")
        f.write(f"- Keywords: {results['dividend_keywords_found']}\n")
        f.write(f"- Amounts: {results['dividend_amounts'][:20]}\n")
        f.write(f"- Dates: {results['dividend_dates'][:20]}\n\n")
        
        f.write(f"SUCCESS SCORE: {success_score}/8\n\n")
        
        f.write(f"TABLE ANALYSIS:\n")
        for i, table in enumerate(results['table_data']):
            f.write(f"Table {i+1}:\n")
            f.write(f"  Headers: {table['headers']}\n")
            f.write(f"  Rows: {len(table['rows'])}\n")
            f.write(f"  Sample rows: {table['rows'][:3]}\n\n")
    
    print(f"📝 Detailed analysis saved to: {analysis_file}")

def main():
    """Main function"""
    print("🚀 Starting Direct Selenium Morningstar Dividend Scraping")
    print()
    print("🎯 This approach:")
    print("   - Uses Selenium WebDriver directly (not through Scrapy)")
    print("   - Waits for JavaScript to fully render content")
    print("   - Specifically looks for dividend table structures")
    print("   - Provides detailed analysis of extraction success")
    print()
    
    results = scrape_morningstar_dividends_with_selenium()
    
    if results:
        print()
        print("🎯 Scraping completed successfully!")
        print("📋 Check the generated files for detailed dividend data analysis.")
    else:
        print()
        print("❌ Scraping failed. Check error messages above.")

if __name__ == "__main__":
    main()
