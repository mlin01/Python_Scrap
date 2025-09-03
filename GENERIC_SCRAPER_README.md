# Generic Financial Data Scraper

A powerful, reusable web scraping solution that can extract financial data from any website that requires JavaScript rendering (Morningstar, Yahoo Finance, MarketWatch, etc.).

## 🚀 Key Features

- **Generic Design**: Works with any financial website, not just Morningstar
- **Auto-Configuration**: Automatically detects website type and applies optimal settings
- **JavaScript Support**: Handles dynamic content with Selenium WebDriver
- **Financial Data Recognition**: Automatically identifies financial tables, currency amounts, dates, and percentages
- **Multiple Output Formats**: JSON for data processing, summary for human reading
- **Easy to Extend**: Simple configuration system for new websites

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `generic_financial_scraper.py` | Core scraping engine with website-agnostic functions |
| `website_configs.py` | Pre-configured settings for popular financial websites |
| `easy_scraper.py` | Simple command-line interface for common tasks |
| `test_generic_scraper.py` | Test suite for validating functionality |

## 🎯 Quick Start

### 1. Simple URL Scraping
```python
from easy_scraper import scrape_any_url

# Scrape any financial website - auto-detects configuration
result_file = scrape_any_url("https://www.morningstar.com/stocks/xnas/aapl/dividends")
```

### 2. Comprehensive Symbol Analysis
```python
from easy_scraper import scrape_symbol_comprehensive

# Scrape multiple sites for a symbol
results = scrape_symbol_comprehensive("AAPL", include_sites=['morningstar', 'yahoo', 'marketwatch'])
```

### 3. Dividend-Specific Analysis
```python
from easy_scraper import scrape_dividend_data

# Focus on dividend data from multiple sources
dividend_data = scrape_dividend_data("AAPL")
```

### 4. Direct API Usage
```python
from generic_financial_scraper import scrape_financial_website

# Use the core scraper directly
result = scrape_financial_website("https://finance.yahoo.com/quote/TSLA")
```

## 🖥️ Command Line Usage

```bash
# Comprehensive symbol analysis
python easy_scraper.py symbol AAPL

# Dividend-focused analysis
python easy_scraper.py dividend TSLA

# Scrape any URL
python easy_scraper.py url "https://finance.yahoo.com/quote/MSFT"

# Website-specific scraping
python easy_scraper.py morningstar GOOGL
python easy_scraper.py yahoo NVDA
```

## 🔧 Configuration System

The scraper automatically selects optimal settings based on the website:

```python
from website_configs import get_config_for_url, build_morningstar_url

# Auto-detect configuration from URL
config = get_config_for_url("https://www.morningstar.com/...")

# Build URLs for specific websites
morningstar_url = build_morningstar_url("AAPL", "dividends")
yahoo_url = build_yahoo_finance_url("AAPL", "financials")
```

## 🌐 Supported Websites

| Website | Auto-Config | URL Builder | Features |
|---------|-------------|-------------|----------|
| Morningstar | ✅ | ✅ | Dividends, financials, analysis |
| Yahoo Finance | ✅ | ✅ | Quotes, financials, news |
| MarketWatch | ✅ | ✅ | Quotes, financials |
| Google Finance | ✅ | ✅ | Basic quotes |
| Any Other Site | ✅ | ➖ | Generic patterns |

## 📊 Data Extraction

The scraper automatically identifies and extracts:

- **Currency Amounts**: $123.45, 1,234 USD, etc.
- **Dates**: MM/DD/YYYY, YYYY-MM-DD, "Jan 15, 2024", etc.
- **Percentages**: 3.45%, 12.5 percent, etc.
- **Financial Tables**: Automatically detects tables with financial data
- **Keywords**: dividend, yield, earnings, revenue, etc.

## 🔄 Extending for New Websites

### 1. Add Website Configuration
```python
# In website_configs.py
WEBSITE_CONFIGS['new_site'] = {
    'scraping_config': ScrapingConfig(
        timeout=30,
        wait_time=10,
        download_delay=2
    ),
    'extraction_config': FinancialDataExtraction(
        table_selectors=['table', '.data-table'],
        financial_keywords=['price', 'volume', 'change']
    )
}
```

### 2. Add URL Pattern
```python
# In website_configs.py
URL_PATTERNS['newsite.com'] = 'new_site'
```

### 3. Add URL Builder (Optional)
```python
def build_newsite_url(symbol: str, page_type: str = 'quote') -> str:
    return f"https://newsite.com/stocks/{symbol}/{page_type}"
```

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Test all websites
python test_generic_scraper.py

# Test specific website
python test_generic_scraper.py morningstar
python test_generic_scraper.py yahoo
python test_generic_scraper.py dividend
```

## 📈 Example Output

### Summary Format
```
Financial Data Summary
==================================================

URL: https://www.morningstar.com/stocks/xnas/aapl/dividends
Title: Apple Inc AAPL Dividends | Morningstar
Success: True

Content Statistics:
- Content length: 2,524 characters
- Tables found: 19
- Financial tables: 19

Sample currency amounts:
  - $0.25
  - $3.29

Financial keywords found:
  - dividend
  - yield
  - quarterly
```

### JSON Format
Complete structured data including HTML content, extracted financial data, table structures, and metadata.

## 🚀 Advanced Usage

### Custom Scraping Configuration
```python
from generic_financial_scraper import GenericFinancialScraper, ScrapingConfig

# Custom configuration
config = ScrapingConfig(
    headless=False,  # Show browser
    timeout=60,      # Longer timeout
    wait_time=20     # Extra wait time
)

scraper = GenericFinancialScraper(config=config)
result = scraper.scrape_url("https://complex-financial-site.com")
```

### Multiple URLs with Custom Settings
```python
from generic_financial_scraper import scrape_multiple_urls

urls = [
    "https://finance.yahoo.com/quote/AAPL",
    "https://www.morningstar.com/stocks/xnas/aapl/dividends",
    "https://www.marketwatch.com/investing/stock/aapl"
]

results = scrape_multiple_urls(urls, config=custom_config)
```

## 🔒 Best Practices

1. **Respect robots.txt**: The scraper includes built-in delays and respects website policies
2. **Rate Limiting**: Automatic delays between requests prevent overwhelming servers
3. **Error Handling**: Comprehensive error catching and reporting
4. **Stealth Mode**: Browser fingerprinting protection to avoid detection
5. **Resource Cleanup**: Automatic browser cleanup to prevent memory leaks

## 🛠️ Requirements

```bash
pip install selenium webdriver-manager
```

The scraper automatically downloads and manages Chrome WebDriver.

## 🎯 Why This Approach?

- **Future-Proof**: Works with any new financial website without code changes
- **Maintainable**: Central configuration system instead of scattered site-specific code
- **Scalable**: Easy to add new websites and data extraction patterns
- **Reliable**: Handles JavaScript rendering that static scrapers miss
- **Flexible**: Multiple output formats and usage patterns

## 🔄 Migration from Site-Specific Scrapers

If you have existing scrapers for specific websites, migrating is simple:

```python
# Old approach (site-specific)
result = scrape_morningstar_dividends("AAPL")

# New approach (generic)
result = scrape_any_url("https://www.morningstar.com/stocks/xnas/aapl/dividends")

# Or use the convenience function
result = scrape_dividend_data("AAPL")  # Checks multiple sites
```

This generic approach gives you the same results with much more flexibility and future compatibility.
