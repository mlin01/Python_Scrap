#!/usr/bin/env python3
"""
Easy Financial Data Scraper
A simple interface to the Generic Financial Scraper for common use cases
"""

import sys
import json
from typing import List, Dict, Any
from generic_financial_scraper import (
    GenericFinancialScraper, 
    ScrapingConfig, 
    FinancialDataExtraction, 
    scrape_financial_website,
    scrape_multiple_urls
)
from website_configs import (
    get_config_for_url,
    get_config_by_name,
    build_morningstar_url,
    build_yahoo_finance_url,
    build_marketwatch_url,
    build_google_finance_url,
    TASK_CONFIGS
)

def scrape_symbol_comprehensive(symbol: str, include_sites: List[str] = None) -> Dict[str, Any]:
    """
    Scrape comprehensive financial data for a symbol from multiple sites
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        include_sites: List of sites to include ['morningstar', 'yahoo', 'marketwatch', 'google']
    
    Returns:
        Dictionary with results from each site
    """
    
    if include_sites is None:
        include_sites = ['morningstar', 'yahoo', 'marketwatch']
    
    results = {}
    
    print(f"🔍 Comprehensive scraping for {symbol.upper()}")
    print("=" * 50)
    
    for site in include_sites:
        try:
            print(f"📊 Scraping {site}...")
            
            if site == 'morningstar':
                # Get dividends from Morningstar
                url = build_morningstar_url(symbol, 'dividends')
                config = get_config_by_name('morningstar')
                
            elif site == 'yahoo':
                # Get quote from Yahoo Finance
                url = build_yahoo_finance_url(symbol)
                config = get_config_by_name('yahoo_finance')
                
            elif site == 'marketwatch':
                # Get quote from MarketWatch
                url = build_marketwatch_url(symbol)
                config = get_config_by_name('marketwatch')
                
            elif site == 'google':
                # Get quote from Google Finance
                url = build_google_finance_url(symbol)
                config = get_config_by_name('google_finance')
            
            else:
                print(f"  ⚠️  Unknown site: {site}")
                continue
            
            # Create scraper with site-specific config
            scraper = GenericFinancialScraper(
                config=config['scraping_config'],
                extraction_config=config['extraction_config']
            )
            
            # Scrape the site
            result = scraper.scrape_url(url)
            results[site] = result
            
            if result.success:
                print(f"  ✅ Success - Found {len(result.tables)} tables, {len(result.extracted_data.get('currency_amounts', []))} prices")
            else:
                print(f"  ❌ Failed - {'; '.join(result.errors)}")
            
        except Exception as e:
            print(f"  ⚠️  Error scraping {site}: {e}")
            results[site] = None
    
    print(f"\n✨ Completed scraping for {symbol.upper()}")
    return results

def scrape_dividend_data(symbol: str) -> Dict[str, Any]:
    """
    Scrape dividend-specific data from multiple sources
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
    
    Returns:
        Combined dividend data from multiple sources
    """
    
    print(f"💰 Dividend Analysis for {symbol.upper()}")
    print("=" * 40)
    
    # URLs to check for dividend data
    urls = [
        build_morningstar_url(symbol, 'dividends'),
        build_yahoo_finance_url(symbol)  # Yahoo quote page has dividend info
    ]
    
    all_results = []
    
    for url in urls:
        print(f"📈 Checking: {url}")
        
        # Get appropriate config for URL
        config = get_config_for_url(url)
        
        # Create scraper
        scraper = GenericFinancialScraper(
            config=config['scraping_config'],
            extraction_config=config['extraction_config']
        )
        
        # Scrape
        result = scraper.scrape_url(url)
        all_results.append(result)
        
        if result.success:
            dividend_keywords = [kw for kw in result.extracted_data.get('financial_keywords_found', []) 
                               if 'dividend' in kw.lower()]
            print(f"  ✅ Found dividend keywords: {dividend_keywords}")
        else:
            print(f"  ❌ Failed to scrape")
    
    # Combine results
    combined_data = {
        'symbol': symbol.upper(),
        'scraped_urls': urls,
        'results': all_results,
        'summary': _summarize_dividend_data(all_results)
    }
    
    return combined_data

def _summarize_dividend_data(results: List[Any]) -> Dict[str, Any]:
    """Summarize dividend data from multiple results"""
    
    summary = {
        'total_dividend_amounts': [],
        'total_dividend_dates': [],
        'dividend_keywords': [],
        'financial_tables': []
    }
    
    for result in results:
        if result and result.success:
            # Collect dividend amounts
            amounts = result.extracted_data.get('currency_amounts', [])
            summary['total_dividend_amounts'].extend(amounts)
            
            # Collect dates
            dates = result.extracted_data.get('dates', [])
            summary['total_dividend_dates'].extend(dates)
            
            # Collect dividend-related keywords
            keywords = result.extracted_data.get('financial_keywords_found', [])
            dividend_keywords = [kw for kw in keywords if 'dividend' in kw.lower()]
            summary['dividend_keywords'].extend(dividend_keywords)
            
            # Collect financial tables
            financial_tables = [t for t in result.tables if t['metadata']['appears_financial']]
            summary['financial_tables'].extend(financial_tables)
    
    # Remove duplicates and limit
    summary['total_dividend_amounts'] = list(set(summary['total_dividend_amounts']))[:20]
    summary['total_dividend_dates'] = list(set(summary['total_dividend_dates']))[:20]
    summary['dividend_keywords'] = list(set(summary['dividend_keywords']))
    
    return summary

def scrape_any_url(url: str, output_format: str = 'json') -> str:
    """
    Scrape any financial website URL with automatic configuration
    
    Args:
        url: URL to scrape
        output_format: 'json', 'html', or 'summary'
    
    Returns:
        Filename of saved results
    """
    
    print(f"🌐 Scraping: {url}")
    
    # Get automatic configuration
    config = get_config_for_url(url)
    
    # Create scraper
    scraper = GenericFinancialScraper(
        config=config['scraping_config'],
        extraction_config=config['extraction_config']
    )
    
    # Scrape
    result = scraper.scrape_url(url)
    
    if result.success:
        timing = result.metadata.get('timing', {})
        total_time = timing.get('total_time_seconds', 0)
        
        print(f"✅ Successfully scraped in {total_time:.2f} seconds!")
        print(f"   📄 Content length: {result.metadata.get('text_length', 0):,} chars")
        print(f"   📊 Tables found: {result.metadata.get('tables_count', 0)}")
        print(f"   💰 Financial tables: {result.metadata.get('financial_tables_count', 0)}")
        print(f"   🔢 Currency amounts: {len(result.extracted_data.get('currency_amounts', []))}")
        
        # Show detailed timing breakdown
        if timing:
            print(f"   ⏱️  Timing breakdown:")
            print(f"      • Setup: {timing.get('setup_time_seconds', 0):.2f}s")
            print(f"      • Navigation: {timing.get('navigation_time_seconds', 0):.2f}s") 
            print(f"      • Wait for content: {timing.get('wait_time_seconds', 0):.2f}s")
            print(f"      • Data extraction: {timing.get('extraction_time_seconds', 0):.2f}s")
        
        # Save results based on format
        if output_format == 'summary':
            filename = _save_summary(result)
        elif output_format == 'html':
            filename = _save_html(result)
        else:
            filename = scraper.save_result(result)
        
        print(f"💾 Results saved to: {filename}")
        return filename
        
    else:
        print(f"❌ Failed to scrape: {'; '.join(result.errors)}")
        return ""

def _save_html(result) -> str:
    """Save HTML content to a clean HTML file"""
    
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain = result.url.split('/')[2].replace('.', '_')
    filename = f"scraped_{domain}_{timestamp}.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        # Write the raw HTML content
        f.write(result.html_content)
    
    return filename

def _save_summary(result) -> str:
    """Save a human-readable summary instead of full JSON"""
    
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain = result.url.split('/')[2].replace('.', '_')
    filename = f"summary_{domain}_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Financial Data Summary\n")
        f.write(f"=" * 50 + "\n\n")
        f.write(f"URL: {result.url}\n")
        f.write(f"Title: {result.title}\n")
        f.write(f"Scraped: {result.scraped_at}\n")
        f.write(f"Success: {result.success}\n\n")
        
        if result.success:
            f.write(f"Content Statistics:\n")
            f.write(f"- Content length: {result.metadata.get('text_length', 0):,} characters\n")
            f.write(f"- Tables found: {result.metadata.get('tables_count', 0)}\n")
            f.write(f"- Financial tables: {result.metadata.get('financial_tables_count', 0)}\n\n")
            
            f.write(f"Financial Data Extracted:\n")
            f.write(f"- Currency amounts: {len(result.extracted_data.get('currency_amounts', []))}\n")
            f.write(f"- Dates: {len(result.extracted_data.get('dates', []))}\n")
            f.write(f"- Percentages: {len(result.extracted_data.get('percentages', []))}\n")
            f.write(f"- Financial keywords: {len(result.extracted_data.get('financial_keywords_found', []))}\n\n")
            
            # Show some examples
            amounts = result.extracted_data.get('currency_amounts', [])[:10]
            if amounts:
                f.write(f"Sample currency amounts:\n")
                for amount in amounts:
                    f.write(f"  - {amount}\n")
                f.write("\n")
            
            dates = result.extracted_data.get('dates', [])[:10]
            if dates:
                f.write(f"Sample dates:\n")
                for date in dates:
                    f.write(f"  - {date}\n")
                f.write("\n")
            
            keywords = result.extracted_data.get('financial_keywords_found', [])
            if keywords:
                f.write(f"Financial keywords found:\n")
                for keyword in keywords:
                    f.write(f"  - {keyword}\n")
                f.write("\n")
            
            # Show table summaries
            for i, table in enumerate(result.tables):
                if table['metadata']['appears_financial']:
                    f.write(f"Financial Table #{i+1}:\n")
                    f.write(f"  - Headers: {', '.join(table['headers'][:5])}\n")
                    f.write(f"  - Rows: {table['metadata']['total_rows']}\n")
                    f.write(f"  - Columns: {table['metadata']['total_columns']}\n\n")
        
        if result.errors:
            f.write(f"Errors:\n")
            for error in result.errors:
                f.write(f"  - {error}\n")
    
    return filename

def main():
    """Command line interface"""
    
    if len(sys.argv) < 2:
        print("📊 Easy Financial Data Scraper")
        print("=" * 40)
        print("Usage:")
        print("  python easy_scraper.py <command> [options]")
        print()
        print("Commands:")
        print("  symbol <SYMBOL>           - Comprehensive scraping for a stock symbol")
        print("  dividend <SYMBOL>         - Dividend analysis for a stock symbol")
        print("  url <URL> [format]        - Scrape any financial website URL")
        print("  morningstar <SYMBOL>      - Scrape Morningstar dividends")
        print("  yahoo <SYMBOL>            - Scrape Yahoo Finance")
        print()
        print("Output formats (for url command):")
        print("  json     - Complete data in JSON format (default)")
        print("  html     - Raw HTML content only")
        print("  summary  - Human-readable summary")
        print()
        print("Examples:")
        print("  python easy_scraper.py symbol AAPL")
        print("  python easy_scraper.py dividend TSLA")
        print("  python easy_scraper.py url https://finance.yahoo.com/quote/MSFT")
        print("  python easy_scraper.py url https://morningstar.com/stocks/xnas/aapl/dividends html")
        print("  python easy_scraper.py morningstar GOOGL")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'symbol' and len(sys.argv) >= 3:
        symbol = sys.argv[2].upper()
        results = scrape_symbol_comprehensive(symbol)
        
        # Save combined results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_{symbol}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({site: result.__dict__ if result else None for site, result in results.items()}, 
                     f, indent=2, default=str)
        
        print(f"\n💾 All results saved to: {filename}")
    
    elif command == 'dividend' and len(sys.argv) >= 3:
        symbol = sys.argv[2].upper()
        results = scrape_dividend_data(symbol)
        
        # Save dividend results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dividend_{symbol}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Dividend analysis saved to: {filename}")
    
    elif command == 'url' and len(sys.argv) >= 3:
        url = sys.argv[2]
        output_format = sys.argv[3] if len(sys.argv) >= 4 else 'json'
        scrape_any_url(url, output_format)
    
    elif command == 'morningstar' and len(sys.argv) >= 3:
        symbol = sys.argv[2].upper()
        url = build_morningstar_url(symbol, 'dividends')
        scrape_any_url(url)
    
    elif command == 'yahoo' and len(sys.argv) >= 3:
        symbol = sys.argv[2].upper()
        page = sys.argv[3] if len(sys.argv) >= 4 else 'quote'
        url = build_yahoo_finance_url(symbol, page)
        scrape_any_url(url)
    
    else:
        print("❌ Invalid command or missing arguments")
        print("Use 'python easy_scraper.py' for help")

if __name__ == "__main__":
    from datetime import datetime
    main()
