#!/usr/bin/env python3
"""
Example: How to extend the Generic Financial Scraper for new websites
This shows how easy it is to add support for any new financial website
"""

from generic_financial_scraper import GenericFinancialScraper, ScrapingConfig, FinancialDataExtraction
from website_configs import WEBSITE_CONFIGS, URL_PATTERNS

def add_new_website_support():
    """Example: Adding support for a hypothetical new financial website"""
    
    print("🔧 Adding support for new financial website...")
    
    # 1. Define configuration for the new website
    new_site_config = {
        'scraping_config': ScrapingConfig(
            timeout=40,
            wait_time=12,
            implicit_wait=8,
            download_delay=3,
            headless=True  # Can be set to False for debugging
        ),
        'extraction_config': FinancialDataExtraction(
            table_selectors=[
                'table',
                '[class*="financial-table"]',
                '[data-testid*="financial"]',
                '.stock-data-table'
            ],
            financial_keywords=[
                'stock price', 'market value', 'trading volume',
                'earnings report', 'financial summary', 'investor data'
            ]
        )
    }
    
    # 2. Add to global configurations
    WEBSITE_CONFIGS['example_finance'] = new_site_config
    URL_PATTERNS['example-finance.com'] = 'example_finance'
    
    print("✅ New website configuration added!")
    return new_site_config

def demonstrate_flexibility():
    """Show different ways to use the generic scraper"""
    
    print("🚀 Demonstrating Generic Scraper Flexibility")
    print("=" * 50)
    
    # Method 1: Direct URL scraping (auto-detects configuration)
    print("\n1️⃣ Auto-detection method:")
    print("from easy_scraper import scrape_any_url")
    print("result = scrape_any_url('https://any-financial-site.com')")
    
    # Method 2: Manual configuration
    print("\n2️⃣ Manual configuration method:")
    print("from generic_financial_scraper import GenericFinancialScraper, ScrapingConfig")
    print("config = ScrapingConfig(timeout=60, headless=False)")
    print("scraper = GenericFinancialScraper(config=config)")
    print("result = scraper.scrape_url('https://any-site.com')")
    
    # Method 3: Multiple URLs
    print("\n3️⃣ Multiple URLs method:")
    print("from generic_financial_scraper import scrape_multiple_urls")
    print("urls = ['https://site1.com', 'https://site2.com']")
    print("results = scrape_multiple_urls(urls)")
    
    # Method 4: Symbol-based analysis
    print("\n4️⃣ Symbol-based analysis:")
    print("from easy_scraper import scrape_symbol_comprehensive")
    print("results = scrape_symbol_comprehensive('AAPL', ['morningstar', 'marketwatch'])")

def test_with_different_symbols():
    """Test the scraper with different stock symbols"""
    
    print("\n🧪 Testing with Different Symbols")
    print("=" * 40)
    
    symbols = ['TSLA', 'MSFT', 'GOOGL']
    
    for symbol in symbols:
        print(f"\n📊 Testing {symbol}...")
        
        # Build Morningstar URL for this symbol
        from website_configs import build_morningstar_url
        url = build_morningstar_url(symbol, 'dividends')
        
        print(f"URL: {url}")
        print("You could scrape this with:")
        print(f"  python easy_scraper.py url '{url}'")
        print(f"  python easy_scraper.py morningstar {symbol}")
        print(f"  python easy_scraper.py dividend {symbol}")

def show_real_world_usage():
    """Show real-world usage patterns"""
    
    print("\n🌍 Real-World Usage Scenarios")
    print("=" * 40)
    
    scenarios = [
        {
            'name': 'Daily Portfolio Monitoring',
            'description': 'Scrape multiple stocks from multiple sources daily',
            'code': '''
portfolio = ['AAPL', 'TSLA', 'MSFT', 'GOOGL']
for symbol in portfolio:
    results = scrape_symbol_comprehensive(symbol, ['morningstar', 'marketwatch'])
    # Process results...
'''
        },
        {
            'name': 'Dividend Research',
            'description': 'Focus on dividend data from all sources',
            'code': '''
dividend_stocks = ['KO', 'JNJ', 'PG', 'T']
for symbol in dividend_stocks:
    dividend_data = scrape_dividend_data(symbol)
    # Analyze dividend trends...
'''
        },
        {
            'name': 'Custom Financial Analysis',
            'description': 'Scrape specific pages with custom settings',
            'code': '''
# Custom configuration for specific needs
config = ScrapingConfig(timeout=60, wait_time=20)
scraper = GenericFinancialScraper(config=config)

custom_urls = [
    'https://finance.site.com/earnings',
    'https://another-site.com/analysis'
]
for url in custom_urls:
    result = scraper.scrape_url(url)
    # Custom processing...
'''
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📈 {scenario['name']}:")
        print(f"   {scenario['description']}")
        print(f"   Code example:{scenario['code']}")

def compare_approaches():
    """Compare the old specialized vs new generic approach"""
    
    print("\n⚖️ Old vs New Approach Comparison")
    print("=" * 45)
    
    print("\n❌ Old Approach (Specialized Functions):")
    print("   - morningstar_dividend_scraper.py")
    print("   - yahoo_finance_scraper.py") 
    print("   - marketwatch_scraper.py")
    print("   - Separate code for each website")
    print("   - Hard to maintain and extend")
    
    print("\n✅ New Approach (Generic System):")
    print("   - One generic_financial_scraper.py")
    print("   - Works with ANY financial website")
    print("   - Auto-detects configuration")
    print("   - Easy to add new websites")
    print("   - Consistent interface")
    
    print("\n🎯 Benefits of Generic Approach:")
    benefits = [
        "Future-proof: Works with new websites without code changes",
        "Maintainable: One codebase instead of many",
        "Consistent: Same interface for all websites",
        "Flexible: Multiple usage patterns",
        "Extensible: Easy to add new sites",
        "Reliable: Handles JavaScript rendering uniformly"
    ]
    
    for benefit in benefits:
        print(f"   ✓ {benefit}")

def main():
    """Main demonstration function"""
    
    print("🎯 Generic Financial Scraper - Advanced Examples")
    print("=" * 60)
    
    # Show how to add new website support
    add_new_website_support()
    
    # Demonstrate different usage methods
    demonstrate_flexibility()
    
    # Test with different symbols
    test_with_different_symbols()
    
    # Show real-world scenarios
    show_real_world_usage()
    
    # Compare approaches
    compare_approaches()
    
    print("\n🎉 Summary:")
    print("The generic scraper gives you a powerful, flexible toolkit that:")
    print("• Works with Morningstar (proven)")
    print("• Will work with Yahoo Finance when you need it")
    print("• Can handle any new financial website")
    print("• Provides consistent results across all sites")
    print("• Is easy to extend and maintain")

if __name__ == "__main__":
    main()
