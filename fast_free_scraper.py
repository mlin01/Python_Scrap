#!/usr/bin/env python3
"""
Fast Free Financial Scraper
A lightweight alternative to Selenium that's much faster and doesn't cost money
Uses requests + BeautifulSoup for speed, with Selenium fallback when needed
"""

import time
import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List
import re

def scrape_with_requests(url: str, output_format: str = 'json') -> str:
    """
    Fast scraping using requests + BeautifulSoup - free and fast
    
    Args:
        url: URL to scrape
        output_format: 'json', 'html', or 'summary'
    
    Returns:
        Filename of saved results
    """
    
    print(f"⚡ Fast scraping with requests: {url}")
    start_time = time.time()
    
    try:
        # Try to import BeautifulSoup
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            print("❌ BeautifulSoup not installed. Install with: pip install beautifulsoup4")
            return ""
        
        # Headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }
        
        # Make the request
        request_start = time.time()
        print("📡 Making HTTP request...")
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        request_time = time.time() - request_start
        
        # Parse with BeautifulSoup
        parse_start = time.time()
        print("📄 Parsing HTML content...")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract data
        extracted_data = extract_financial_data_fast(soup, response.text)
        tables = extract_tables_fast(soup)
        
        parse_time = time.time() - parse_start
        total_time = time.time() - start_time
        
        print(f"✅ Successfully scraped in {total_time:.2f} seconds!")
        print(f"   📡 Request time: {request_time:.2f}s")
        print(f"   📄 Parse time: {parse_time:.2f}s")
        print(f"   📊 Tables found: {len(tables)}")
        print(f"   📝 Content length: {len(response.text):,} chars")
        
        # Create result object
        result = {
            'url': url,
            'title': soup.title.string if soup.title else '',
            'scraped_at': datetime.now().isoformat(),
            'success': True,
            'method': 'requests_beautifulsoup',
            'html_content': response.text,
            'text_content': soup.get_text(),
            'extracted_data': extracted_data,
            'tables': tables,
            'timing': {
                'total_time_seconds': round(total_time, 2),
                'request_time_seconds': round(request_time, 2),
                'parse_time_seconds': round(parse_time, 2)
            },
            'metadata': {
                'html_length': len(response.text),
                'text_length': len(soup.get_text()),
                'tables_count': len(tables),
                'status_code': response.status_code
            }
        }
        
        # Save results based on format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        domain = url.split('/')[2].replace('.', '_')
        
        if output_format == 'html':
            filename = f"fast_{domain}_{timestamp}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
                
        elif output_format == 'summary':
            filename = f"fast_summary_{domain}_{timestamp}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Fast Scraper Results Summary\n")
                f.write(f"=" * 50 + "\n\n")
                f.write(f"URL: {url}\n")
                f.write(f"Title: {result['title']}\n")
                f.write(f"Method: {result['method']}\n")
                f.write(f"Scraped: {result['scraped_at']}\n")
                f.write(f"Total time: {total_time:.2f} seconds\n")
                f.write(f"Status: {response.status_code}\n\n")
                
                f.write(f"Performance:\n")
                f.write(f"- Request: {request_time:.2f}s\n")
                f.write(f"- Parsing: {parse_time:.2f}s\n")
                f.write(f"- Content length: {len(response.text):,} chars\n")
                f.write(f"- Tables found: {len(tables)}\n\n")
                
                # Show financial data found
                if extracted_data['currency_amounts']:
                    f.write(f"Currency amounts found:\n")
                    for amount in extracted_data['currency_amounts'][:10]:
                        f.write(f"  - {amount}\n")
                    f.write("\n")
                
                if extracted_data['dates']:
                    f.write(f"Dates found:\n")
                    for date in extracted_data['dates'][:10]:
                        f.write(f"  - {date}\n")
                    f.write("\n")
                
                if extracted_data['financial_keywords']:
                    f.write(f"Financial keywords:\n")
                    for keyword in extracted_data['financial_keywords']:
                        f.write(f"  - {keyword}\n")
                    f.write("\n")
                
                # Show table summaries
                for i, table in enumerate(tables[:5]):
                    f.write(f"Table #{i+1}:\n")
                    f.write(f"  - Headers: {len(table['headers'])}\n")
                    f.write(f"  - Rows: {len(table['rows'])}\n")
                    if table['headers']:
                        f.write(f"  - Sample headers: {', '.join(table['headers'][:3])}\n")
                    f.write("\n")
                
        else:  # json
            filename = f"fast_{domain}_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {filename}")
        return filename
        
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return ""
    except Exception as e:
        print(f"❌ Error: {e}")
        return ""

def extract_financial_data_fast(soup, html_content: str) -> Dict[str, Any]:
    """Extract financial data using BeautifulSoup - much faster than Selenium"""
    
    text_content = soup.get_text()
    
    extracted_data = {
        'currency_amounts': [],
        'dates': [],
        'percentages': [],
        'financial_keywords': [],
        'financial_metrics': {}
    }
    
    # Currency patterns
    currency_patterns = [
        r'\$[0-9,]+\.?[0-9]*',
        r'[0-9,]+\.?[0-9]*\s*USD',
        r'[0-9,]+\.?[0-9]*\s*\$'
    ]
    
    # Date patterns
    date_patterns = [
        r'\d{1,2}/\d{1,2}/\d{4}',
        r'\d{4}-\d{2}-\d{2}',
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}',
        r'\d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) \d{4}'
    ]
    
    # Percentage patterns
    percentage_patterns = [
        r'[0-9,]+\.?[0-9]*\s*%',
        r'[0-9,]+\.?[0-9]*\s*percent'
    ]
    
    # Financial keywords
    financial_keywords = [
        'dividend', 'yield', 'earnings', 'revenue', 'profit',
        'ex-dividend', 'payment date', 'record date',
        'quarterly', 'annual', 'financial', 'income',
        'market cap', 'price', 'volume', 'change'
    ]
    
    # Extract currency amounts
    for pattern in currency_patterns:
        matches = re.findall(pattern, text_content, re.IGNORECASE)
        extracted_data['currency_amounts'].extend(matches)
    
    # Extract dates
    for pattern in date_patterns:
        matches = re.findall(pattern, text_content, re.IGNORECASE)
        extracted_data['dates'].extend(matches)
    
    # Extract percentages
    for pattern in percentage_patterns:
        matches = re.findall(pattern, text_content, re.IGNORECASE)
        extracted_data['percentages'].extend(matches)
    
    # Find financial keywords
    text_lower = text_content.lower()
    for keyword in financial_keywords:
        if keyword.lower() in text_lower:
            extracted_data['financial_keywords'].append(keyword)
    
    # Remove duplicates and limit results
    extracted_data['currency_amounts'] = list(set(extracted_data['currency_amounts']))[:50]
    extracted_data['dates'] = list(set(extracted_data['dates']))[:50]
    extracted_data['percentages'] = list(set(extracted_data['percentages']))[:30]
    extracted_data['financial_keywords'] = list(set(extracted_data['financial_keywords']))
    
    return extracted_data

def extract_tables_fast(soup) -> List[Dict[str, Any]]:
    """Extract tables using BeautifulSoup - much faster than Selenium"""
    
    tables_data = []
    
    # Find all tables
    tables = soup.find_all('table')
    
    for i, table in enumerate(tables):
        table_info = {
            'index': i,
            'headers': [],
            'rows': [],
            'metadata': {}
        }
        
        # Extract headers
        headers = table.find_all(['th', 'thead'])
        if headers:
            table_info['headers'] = [h.get_text().strip() for h in headers if h.get_text().strip()]
        
        # Extract rows
        rows = table.find_all('tr')
        for row in rows[:50]:  # Limit to first 50 rows
            cells = row.find_all(['td', 'th'])
            if cells:
                row_data = [cell.get_text().strip() for cell in cells]
                if any(cell for cell in row_data):  # Only add non-empty rows
                    table_info['rows'].append(row_data)
        
        # Add metadata
        table_info['metadata'] = {
            'total_rows': len(table_info['rows']),
            'total_columns': len(table_info['headers']) if table_info['headers'] else (len(table_info['rows'][0]) if table_info['rows'] else 0),
            'appears_financial': is_financial_table_fast(table_info)
        }
        
        if table_info['headers'] or table_info['rows']:
            tables_data.append(table_info)
    
    return tables_data

def is_financial_table_fast(table_info: Dict[str, Any]) -> bool:
    """Determine if a table contains financial data - fast version"""
    
    # Check headers for financial keywords
    headers_text = ' '.join(table_info['headers']).lower()
    financial_header_keywords = [
        'dividend', 'yield', 'price', 'date', 'amount', 'payment',
        'ex-date', 'record', 'earnings', 'revenue', 'profit'
    ]
    
    header_score = sum(1 for keyword in financial_header_keywords if keyword in headers_text)
    
    # Check first few rows for financial patterns
    row_score = 0
    for row in table_info['rows'][:5]:
        row_text = ' '.join(row).lower()
        if '$' in row_text or '%' in row_text:
            row_score += 1
    
    return header_score >= 1 or row_score >= 2

def compare_methods(url: str) -> Dict[str, Any]:
    """
    Compare fast requests method vs slow Selenium method
    """
    
    print(f"🏁 Performance Comparison: Fast vs Slow")
    print(f"URL: {url}")
    print("=" * 60)
    
    results = {
        'url': url,
        'comparison_time': datetime.now().isoformat(),
        'methods': {}
    }
    
    # Test fast method (requests + BeautifulSoup)
    print("\n⚡ Testing Fast Method (requests + BeautifulSoup)...")
    fast_start = time.time()
    fast_file = scrape_with_requests(url, 'json')
    fast_time = time.time() - fast_start
    
    results['methods']['fast_requests'] = {
        'time_seconds': round(fast_time, 2),
        'success': bool(fast_file),
        'output_file': fast_file,
        'method': 'requests + BeautifulSoup'
    }
    
    # Test slow method (Selenium) - optional
    test_selenium = input("\n🐌 Test slow Selenium method too? (y/n): ").lower().startswith('y')
    
    if test_selenium:
        print("\n🐌 Testing Slow Method (Selenium)...")
        selenium_start = time.time()
        
        try:
            from easy_scraper import scrape_any_url
            selenium_file = scrape_any_url(url, 'json')
            selenium_time = time.time() - selenium_start
            
            results['methods']['selenium'] = {
                'time_seconds': round(selenium_time, 2),
                'success': bool(selenium_file),
                'output_file': selenium_file,
                'method': 'Selenium WebDriver'
            }
            
        except Exception as e:
            selenium_time = time.time() - selenium_start
            results['methods']['selenium'] = {
                'time_seconds': round(selenium_time, 2),
                'success': False,
                'error': str(e),
                'method': 'Selenium WebDriver'
            }
    
    # Summary
    print(f"\n📊 Performance Summary:")
    print("=" * 30)
    
    for method, data in results['methods'].items():
        status = "✅" if data['success'] else "❌"
        print(f"{data['method']}: {data['time_seconds']:.2f}s {status}")
    
    # Speed comparison
    if len(results['methods']) > 1:
        fast_time = results['methods']['fast_requests']['time_seconds']
        if 'selenium' in results['methods']:
            selenium_time = results['methods']['selenium']['time_seconds']
            speedup = selenium_time / fast_time if fast_time > 0 else 0
            print(f"\n🚀 Fast method is {speedup:.1f}x faster than Selenium!")
    
    # Save comparison results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    comparison_file = f"speed_comparison_free_{timestamp}.json"
    
    with open(comparison_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Comparison saved to: {comparison_file}")
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("⚡ Fast Free Financial Scraper")
        print("=" * 35)
        print("Usage:")
        print("  python fast_free_scraper.py <url> [format]")
        print("  python fast_free_scraper.py compare <url>")
        print()
        print("Formats:")
        print("  json    - Complete data (default)")
        print("  html    - Raw HTML only")
        print("  summary - Human-readable summary")
        print()
        print("Examples:")
        print("  python fast_free_scraper.py https://www.morningstar.com/stocks/xnas/aapl/dividends")
        print("  python fast_free_scraper.py https://finance.yahoo.com/quote/AAPL html")
        print("  python fast_free_scraper.py compare https://www.morningstar.com/stocks/xnas/aapl/dividends")
    
    elif sys.argv[1] == 'compare' and len(sys.argv) >= 3:
        url = sys.argv[2]
        compare_methods(url)
    
    else:
        url = sys.argv[1]
        output_format = sys.argv[2] if len(sys.argv) >= 3 else 'json'
        scrape_with_requests(url, output_format)
