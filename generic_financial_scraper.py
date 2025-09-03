#!/usr/bin/env python3
"""
Generic JavaScript-Enabled Financial Data Scraper
This module provides reusable functions for scraping financial data from any website
that requires JavaScript rendering (Morningstar, Yahoo Finance, etc.)
"""

import time
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging

# Import Selenium components
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

@dataclass
class ScrapingConfig:
    """Configuration for scraping operations"""
    headless: bool = True
    timeout: int = 30
    wait_time: int = 10
    implicit_wait: int = 10
    window_size: Tuple[int, int] = (1920, 1080)
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    respect_robots: bool = True
    download_delay: int = 3

@dataclass
class FinancialDataExtraction:
    """Configuration for financial data extraction patterns"""
    # Generic financial patterns
    currency_patterns: List[str] = None
    date_patterns: List[str] = None
    percentage_patterns: List[str] = None
    
    # Table detection selectors
    table_selectors: List[str] = None
    
    # Content detection keywords
    financial_keywords: List[str] = None
    
    def __post_init__(self):
        if self.currency_patterns is None:
            self.currency_patterns = [
                r'\$[0-9,]+\.?[0-9]*',
                r'[0-9,]+\.?[0-9]*\s*USD',
                r'[0-9,]+\.?[0-9]*\s*\$'
            ]
        
        if self.date_patterns is None:
            self.date_patterns = [
                r'\d{1,2}/\d{1,2}/\d{4}',
                r'\d{4}-\d{2}-\d{2}',
                r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}',
                r'\d{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) \d{4}'
            ]
        
        if self.percentage_patterns is None:
            self.percentage_patterns = [
                r'[0-9,]+\.?[0-9]*\s*%',
                r'[0-9,]+\.?[0-9]*\s*percent'
            ]
        
        if self.table_selectors is None:
            self.table_selectors = [
                'table',
                '[role="table"]',
                '[class*="table"]',
                '[class*="data-table"]',
                '[class*="grid"]',
                '[class*="financial"]',
                '[data-testid*="table"]'
            ]
        
        if self.financial_keywords is None:
            self.financial_keywords = [
                'dividend', 'yield', 'earnings', 'revenue', 'profit',
                'ex-dividend', 'payment date', 'record date',
                'quarterly', 'annual', 'financial', 'income',
                'balance sheet', 'cash flow', 'market cap',
                'price', 'volume', 'change', 'high', 'low'
            ]

@dataclass
class ScrapingResult:
    """Results from a scraping operation"""
    url: str
    title: str
    scraped_at: str
    success: bool
    html_content: str
    text_content: str
    extracted_data: Dict[str, Any]
    tables: List[Dict[str, Any]]
    errors: List[str]
    metadata: Dict[str, Any]

class GenericFinancialScraper:
    """Generic scraper for financial websites with JavaScript rendering"""
    
    def __init__(self, config: ScrapingConfig = None, extraction_config: FinancialDataExtraction = None):
        self.config = config or ScrapingConfig()
        self.extraction_config = extraction_config or FinancialDataExtraction()
        self.driver = None
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self) -> webdriver.Chrome:
        """Set up Chrome WebDriver with optimal settings"""
        chrome_options = Options()
        
        if self.config.headless:
            chrome_options.add_argument("--headless")
        
        # Performance and compatibility options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--window-size={self.config.window_size[0]},{self.config.window_size[1]}")
        chrome_options.add_argument(f"--user-agent={self.config.user_agent}")
        
        # Additional options for better compatibility
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Additional stealth measures
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            driver.set_page_load_timeout(self.config.timeout)
            driver.implicitly_wait(self.config.implicit_wait)
            
            self.logger.info("Chrome WebDriver setup successfully")
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to setup Chrome WebDriver: {e}")
            raise
    
    def wait_for_dynamic_content(self, driver: webdriver.Chrome, url: str) -> bool:
        """Wait for dynamic content to load based on URL patterns and common indicators"""
        
        # URL-specific waiting strategies
        if 'morningstar.com' in url:
            return self._wait_for_morningstar_content(driver)
        elif 'yahoo.com' in url or 'finance.yahoo.com' in url:
            return self._wait_for_yahoo_content(driver)
        elif 'marketwatch.com' in url:
            return self._wait_for_marketwatch_content(driver)
        else:
            return self._wait_for_generic_content(driver)
    
    def _wait_for_morningstar_content(self, driver: webdriver.Chrome) -> bool:
        """Wait for Morningstar-specific content to load"""
        try:
            # Wait for Nuxt.js to initialize
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
            
            # Wait for tables or data containers
            WebDriverWait(driver, 15).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, 'table, [class*="table"], [role="table"]')) > 0
            )
            
            self.logger.info("Morningstar content loaded")
            return True
            
        except TimeoutException:
            self.logger.warning("Timeout waiting for Morningstar content")
            return False
    
    def _wait_for_yahoo_content(self, driver: webdriver.Chrome) -> bool:
        """Wait for Yahoo Finance content to load"""
        try:
            # Wait for main content area
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test*="quote"], #Main, main'))
            )
            
            # Wait for financial data to appear
            WebDriverWait(driver, 10).until(
                lambda d: '$' in d.page_source or 'USD' in d.page_source
            )
            
            self.logger.info("Yahoo Finance content loaded")
            return True
            
        except TimeoutException:
            self.logger.warning("Timeout waiting for Yahoo Finance content")
            return False
    
    def _wait_for_marketwatch_content(self, driver: webdriver.Chrome) -> bool:
        """Wait for MarketWatch content to load"""
        try:
            # Wait for main content
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.region--primary, main, #maincontent'))
            )
            
            self.logger.info("MarketWatch content loaded")
            return True
            
        except TimeoutException:
            self.logger.warning("Timeout waiting for MarketWatch content")
            return False
    
    def _wait_for_generic_content(self, driver: webdriver.Chrome) -> bool:
        """Generic waiting strategy for unknown websites"""
        try:
            # Wait for basic page structure
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(self.config.wait_time)
            
            self.logger.info("Generic content loaded")
            return True
            
        except TimeoutException:
            self.logger.warning("Timeout waiting for generic content")
            return False
    
    def extract_financial_data(self, text_content: str, html_content: str) -> Dict[str, Any]:
        """Extract financial data using pattern matching"""
        
        extracted_data = {
            'currency_amounts': [],
            'dates': [],
            'percentages': [],
            'financial_keywords_found': [],
            'financial_metrics': {}
        }
        
        # Extract currency amounts
        for pattern in self.extraction_config.currency_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            extracted_data['currency_amounts'].extend(matches)
        
        # Extract dates
        for pattern in self.extraction_config.date_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            extracted_data['dates'].extend(matches)
        
        # Extract percentages
        for pattern in self.extraction_config.percentage_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            extracted_data['percentages'].extend(matches)
        
        # Find financial keywords
        text_lower = text_content.lower()
        for keyword in self.extraction_config.financial_keywords:
            if keyword.lower() in text_lower:
                extracted_data['financial_keywords_found'].append(keyword)
        
        # Extract specific financial metrics (can be extended)
        extracted_data['financial_metrics'] = self._extract_specific_metrics(text_content)
        
        # Remove duplicates and limit results
        extracted_data['currency_amounts'] = list(set(extracted_data['currency_amounts']))[:50]
        extracted_data['dates'] = list(set(extracted_data['dates']))[:50]
        extracted_data['percentages'] = list(set(extracted_data['percentages']))[:30]
        
        return extracted_data
    
    def _extract_specific_metrics(self, text_content: str) -> Dict[str, str]:
        """Extract specific financial metrics using pattern matching"""
        metrics = {}
        
        # Dividend yield pattern
        dividend_yield_match = re.search(r'dividend yield[:\s]*([0-9.]+%)', text_content, re.IGNORECASE)
        if dividend_yield_match:
            metrics['dividend_yield'] = dividend_yield_match.group(1)
        
        # Market cap pattern
        market_cap_match = re.search(r'market cap[:\s]*(\$[0-9.,]+[BMT]?)', text_content, re.IGNORECASE)
        if market_cap_match:
            metrics['market_cap'] = market_cap_match.group(1)
        
        # P/E ratio pattern
        pe_ratio_match = re.search(r'p/e ratio[:\s]*([0-9.]+)', text_content, re.IGNORECASE)
        if pe_ratio_match:
            metrics['pe_ratio'] = pe_ratio_match.group(1)
        
        return metrics
    
    def extract_tables(self, driver: webdriver.Chrome) -> List[Dict[str, Any]]:
        """Extract all table data from the page"""
        tables_data = []
        
        for selector in self.extraction_config.table_selectors:
            try:
                tables = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for i, table in enumerate(tables):
                    table_info = {
                        'selector': selector,
                        'index': i,
                        'headers': [],
                        'rows': [],
                        'metadata': {}
                    }
                    
                    # Extract headers
                    try:
                        headers = table.find_elements(By.CSS_SELECTOR, "th, thead td, [role='columnheader']")
                        if headers:
                            table_info['headers'] = [h.text.strip() for h in headers if h.text.strip()]
                    except:
                        pass
                    
                    # Extract rows
                    try:
                        rows = table.find_elements(By.CSS_SELECTOR, "tr, [role='row']")
                        for row in rows[:50]:  # Limit to first 50 rows
                            cells = row.find_elements(By.CSS_SELECTOR, "td, th, [role='cell'], [role='columnheader']")
                            if cells:
                                row_data = [cell.text.strip() for cell in cells]
                                if any(cell for cell in row_data):  # Only add non-empty rows
                                    table_info['rows'].append(row_data)
                    except:
                        pass
                    
                    # Add metadata
                    table_info['metadata'] = {
                        'total_rows': len(table_info['rows']),
                        'total_columns': len(table_info['headers']) if table_info['headers'] else (len(table_info['rows'][0]) if table_info['rows'] else 0),
                        'appears_financial': self._is_financial_table(table_info)
                    }
                    
                    if table_info['headers'] or table_info['rows']:
                        tables_data.append(table_info)
                        
            except Exception as e:
                self.logger.warning(f"Error extracting tables with selector '{selector}': {e}")
        
        return tables_data
    
    def _is_financial_table(self, table_info: Dict[str, Any]) -> bool:
        """Determine if a table contains financial data"""
        
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
    
    def scrape_url(self, url: str) -> ScrapingResult:
        """Main scraping function - works with any financial website"""
        
        import time
        start_time = time.time()
        
        self.logger.info(f"Starting to scrape: {url}")
        
        errors = []
        
        try:
            # Setup driver
            setup_start = time.time()
            self.driver = self.setup_driver()
            setup_time = time.time() - setup_start
            
            # Respect robots.txt delay
            if self.config.respect_robots:
                time.sleep(self.config.download_delay)
            
            # Navigate to URL
            nav_start = time.time()
            self.logger.info(f"Loading page: {url}")
            self.driver.get(url)
            nav_time = time.time() - nav_start
            
            # Wait for initial page load
            time.sleep(3)
            
            # Wait for dynamic content based on website
            wait_start = time.time()
            content_loaded = self.wait_for_dynamic_content(self.driver, url)
            if not content_loaded:
                errors.append("Dynamic content may not have loaded completely")
            wait_time = time.time() - wait_start
            
            # Additional wait for safety
            time.sleep(self.config.wait_time)
            
            # Extract content
            extract_start = time.time()
            html_content = self.driver.page_source
            title = self.driver.title
            
            # Extract text content
            try:
                body = self.driver.find_element(By.TAG_NAME, "body")
                text_content = body.text
            except:
                text_content = ""
                errors.append("Could not extract text content")
            
            # Extract financial data
            extracted_data = self.extract_financial_data(text_content, html_content)
            
            # Extract tables
            tables = self.extract_tables(self.driver)
            extract_time = time.time() - extract_start
            
            total_time = time.time() - start_time
            
            # Create result with timing information
            result = ScrapingResult(
                url=url,
                title=title,
                scraped_at=datetime.now().isoformat(),
                success=True,
                html_content=html_content,
                text_content=text_content,
                extracted_data=extracted_data,
                tables=tables,
                errors=errors,
                metadata={
                    'html_length': len(html_content),
                    'text_length': len(text_content),
                    'tables_count': len(tables),
                    'financial_tables_count': sum(1 for t in tables if t['metadata']['appears_financial']),
                    'extraction_method': 'selenium_generic',
                    'timing': {
                        'total_time_seconds': round(total_time, 2),
                        'setup_time_seconds': round(setup_time, 2),
                        'navigation_time_seconds': round(nav_time, 2),
                        'wait_time_seconds': round(wait_time, 2),
                        'extraction_time_seconds': round(extract_time, 2)
                    }
                }
            )
            
            self.logger.info(f"Successfully scraped {url} in {total_time:.2f} seconds")
            return result
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            
            # Return failed result
            return ScrapingResult(
                url=url,
                title="",
                scraped_at=datetime.now().isoformat(),
                success=False,
                html_content="",
                text_content="",
                extracted_data={},
                tables=[],
                errors=[str(e)],
                metadata={}
            )
            
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info("WebDriver closed")
    
    def save_result(self, result: ScrapingResult, filename: str = None) -> str:
        """Save scraping result to JSON file"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            domain = result.url.split('/')[2].replace('.', '_')
            filename = f"financial_scraping_{domain}_{timestamp}.json"
        
        # Convert result to dictionary
        result_dict = asdict(result)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results saved to: {filename}")
        return filename

# Convenience functions for common use cases

def scrape_financial_website(url: str, config: ScrapingConfig = None) -> ScrapingResult:
    """Convenient function to scrape any financial website"""
    scraper = GenericFinancialScraper(config)
    return scraper.scrape_url(url)

def scrape_multiple_urls(urls: List[str], config: ScrapingConfig = None) -> List[ScrapingResult]:
    """Scrape multiple URLs with the same configuration"""
    results = []
    
    for url in urls:
        print(f"🌐 Scraping: {url}")
        result = scrape_financial_website(url, config)
        results.append(result)
        
        # Delay between requests
        if config and config.download_delay:
            time.sleep(config.download_delay)
    
    return results

def create_custom_extraction_config(
    additional_keywords: List[str] = None,
    additional_selectors: List[str] = None
) -> FinancialDataExtraction:
    """Create a customized extraction configuration"""
    
    config = FinancialDataExtraction()
    
    if additional_keywords:
        config.financial_keywords.extend(additional_keywords)
    
    if additional_selectors:
        config.table_selectors.extend(additional_selectors)
    
    return config

# Example usage functions

def scrape_morningstar_dividends(symbol: str = "AAPL") -> ScrapingResult:
    """Scrape Morningstar dividend data for a specific symbol"""
    url = f"https://www.morningstar.com/stocks/xnas/{symbol.lower()}/dividends"
    
    # Custom config for dividend data
    extraction_config = create_custom_extraction_config(
        additional_keywords=['ex-dividend', 'payment date', 'record date', 'quarterly dividend'],
        additional_selectors=['[class*="dividend"]', '[data-testid*="dividend"]']
    )
    
    scraper = GenericFinancialScraper(extraction_config=extraction_config)
    return scraper.scrape_url(url)

def scrape_yahoo_finance(symbol: str = "AAPL", page: str = "quote") -> ScrapingResult:
    """Scrape Yahoo Finance data for a specific symbol"""
    url = f"https://finance.yahoo.com/quote/{symbol.upper()}"
    
    if page != "quote":
        url += f"/{page}"
    
    # Custom config for Yahoo Finance
    extraction_config = create_custom_extraction_config(
        additional_keywords=['market cap', 'volume', 'avg volume', 'beta', 'eps'],
        additional_selectors=['[data-test*="quote"]', '[data-symbol]']
    )
    
    scraper = GenericFinancialScraper(extraction_config=extraction_config)
    return scraper.scrape_url(url)

if __name__ == "__main__":
    # Example usage
    print("🚀 Generic Financial Data Scraper")
    print("This module provides reusable functions for any financial website")
    print()
    print("Example usage:")
    print("1. result = scrape_morningstar_dividends('AAPL')")
    print("2. result = scrape_yahoo_finance('AAPL', 'financials')")
    print("3. result = scrape_financial_website('https://any-financial-site.com')")
