# Website-specific configurations for the Generic Financial Scraper
# This file contains pre-configured settings for popular financial websites

from generic_financial_scraper import ScrapingConfig, FinancialDataExtraction
from typing import Dict, Any

# Website configurations
WEBSITE_CONFIGS = {
    'morningstar': {
        'scraping_config': ScrapingConfig(
            timeout=45,
            wait_time=15,
            implicit_wait=10,
            download_delay=3
        ),
        'extraction_config': FinancialDataExtraction(
            table_selectors=[
                'table',
                '[class*="table"]',
                '[class*="dividend"]',
                '[class*="data-table"]',
                '[role="table"]',
                '[data-testid*="table"]',
                '[data-testid*="dividend"]'
            ],
            financial_keywords=[
                'dividend', 'yield', 'ex-dividend', 'payment date', 'record date',
                'quarterly', 'annual', 'dividend per share', 'payout ratio',
                'dividend growth', 'trailing yield', 'forward yield'
            ]
        )
    },
    
    'yahoo_finance': {
        'scraping_config': ScrapingConfig(
            timeout=30,
            wait_time=10,
            implicit_wait=8,
            download_delay=2
        ),
        'extraction_config': FinancialDataExtraction(
            table_selectors=[
                'table',
                '[data-test*="quote"]',
                '[data-test*="financials"]',
                '[class*="table"]',
                '[class*="data-table"]',
                '[data-symbol]',
                'section[data-testid]'
            ],
            financial_keywords=[
                'market cap', 'volume', 'avg volume', 'beta', 'eps',
                'revenue', 'profit margin', 'operating margin', 'return on equity',
                'price/earnings', 'price/book', 'debt/equity', 'current ratio'
            ]
        )
    },
    
    'marketwatch': {
        'scraping_config': ScrapingConfig(
            timeout=25,
            wait_time=8,
            implicit_wait=6,
            download_delay=2
        ),
        'extraction_config': FinancialDataExtraction(
            table_selectors=[
                'table',
                '[class*="table"]',
                '[class*="data-table"]',
                '.region--primary table',
                '[data-module*="financials"]'
            ],
            financial_keywords=[
                'last price', 'change', 'volume', 'market cap',
                'dividend yield', 'p/e ratio', 'earnings'
            ]
        )
    },
    
    'google_finance': {
        'scraping_config': ScrapingConfig(
            timeout=20,
            wait_time=6,
            implicit_wait=5,
            download_delay=1
        ),
        'extraction_config': FinancialDataExtraction(
            table_selectors=[
                'table',
                '[class*="table"]',
                '[jsname]',
                '[data-aid]'
            ],
            financial_keywords=[
                'price', 'change', 'volume', 'market cap',
                'p/e ratio', 'dividend yield'
            ]
        )
    },
    
    'generic': {
        'scraping_config': ScrapingConfig(
            timeout=30,
            wait_time=10,
            implicit_wait=8,
            download_delay=3
        ),
        'extraction_config': FinancialDataExtraction()  # Uses default patterns
    }
}

# URL patterns for automatic website detection
URL_PATTERNS = {
    'morningstar.com': 'morningstar',
    'finance.yahoo.com': 'yahoo_finance',
    'yahoo.com/quote': 'yahoo_finance',
    'marketwatch.com': 'marketwatch',
    'google.com/finance': 'google_finance'
}

def get_config_for_url(url: str) -> Dict[str, Any]:
    """Automatically detect the best configuration for a URL"""
    
    for pattern, config_name in URL_PATTERNS.items():
        if pattern in url.lower():
            return WEBSITE_CONFIGS[config_name]
    
    # Return generic config if no match found
    return WEBSITE_CONFIGS['generic']

def get_config_by_name(website_name: str) -> Dict[str, Any]:
    """Get configuration by website name"""
    
    website_name = website_name.lower()
    
    if website_name in WEBSITE_CONFIGS:
        return WEBSITE_CONFIGS[website_name]
    
    # Return generic config if not found
    return WEBSITE_CONFIGS['generic']

# Common URL builders
def build_morningstar_url(symbol: str, page_type: str = 'dividends') -> str:
    """Build Morningstar URL for a symbol"""
    symbol = symbol.upper()
    
    # Map common page types
    page_map = {
        'dividends': 'dividends',
        'financials': 'financials',
        'quote': 'quote',
        'analysis': 'analysis',
        'chart': 'chart'
    }
    
    page = page_map.get(page_type, page_type)
    return f"https://www.morningstar.com/stocks/xnas/{symbol.lower()}/{page}"

def build_yahoo_finance_url(symbol: str, page_type: str = 'quote') -> str:
    """Build Yahoo Finance URL for a symbol"""
    symbol = symbol.upper()
    
    base_url = f"https://finance.yahoo.com/quote/{symbol}"
    
    if page_type == 'quote':
        return base_url
    else:
        return f"{base_url}/{page_type}"

def build_marketwatch_url(symbol: str, page_type: str = 'quote') -> str:
    """Build MarketWatch URL for a symbol"""
    symbol = symbol.lower()
    
    if page_type == 'quote':
        return f"https://www.marketwatch.com/investing/stock/{symbol}"
    elif page_type == 'financials':
        return f"https://www.marketwatch.com/investing/stock/{symbol}/financials"
    else:
        return f"https://www.marketwatch.com/investing/stock/{symbol}/{page_type}"

def build_google_finance_url(symbol: str, exchange: str = 'NASDAQ') -> str:
    """Build Google Finance URL for a symbol"""
    symbol = symbol.upper()
    exchange = exchange.upper()
    
    return f"https://www.google.com/finance/quote/{symbol}:{exchange}"

# Example configurations for common tasks
TASK_CONFIGS = {
    'dividend_analysis': {
        'urls': [
            lambda symbol: build_morningstar_url(symbol, 'dividends'),
            lambda symbol: build_yahoo_finance_url(symbol, 'quote')
        ],
        'keywords': ['dividend', 'yield', 'ex-dividend', 'payment', 'quarterly']
    },
    
    'financial_overview': {
        'urls': [
            lambda symbol: build_yahoo_finance_url(symbol, 'financials'),
            lambda symbol: build_marketwatch_url(symbol, 'financials'),
            lambda symbol: build_morningstar_url(symbol, 'financials')
        ],
        'keywords': ['revenue', 'earnings', 'profit', 'margin', 'cash flow']
    },
    
    'stock_quote': {
        'urls': [
            lambda symbol: build_yahoo_finance_url(symbol),
            lambda symbol: build_google_finance_url(symbol),
            lambda symbol: build_marketwatch_url(symbol)
        ],
        'keywords': ['price', 'volume', 'change', 'high', 'low', 'market cap']
    }
}

if __name__ == "__main__":
    print("📋 Website Configuration Helper")
    print("Available configurations:")
    for name in WEBSITE_CONFIGS.keys():
        print(f"  - {name}")
    
    print("\nURL Builders available:")
    print("  - build_morningstar_url('AAPL', 'dividends')")
    print("  - build_yahoo_finance_url('AAPL', 'financials')")
    print("  - build_marketwatch_url('AAPL')")
    print("  - build_google_finance_url('AAPL')")
