#!/usr/bin/env python3
"""
Improved scraper for Morningstar AAPL dividends page
This version is specifically designed to extract dividend table data that requires JavaScript rendering
"""

import sys
import os
import time
import json
import re
from pathlib import Path
from datetime import datetime

def test_morningstar_dividend_data_extraction():
    """
    Test specific extraction of dividend data from Morningstar
    This function addresses the issue where our initial scraper wasn't capturing the actual dividend table
    """
    
    url = "https://www.morningstar.com/stocks/xnas/aapl/dividends"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"morningstar_dividend_data_{timestamp}.json"
    
    print("🎯 Improved Morningstar AAPL Dividend Data Extraction")
    print("=" * 70)
    print(f"Target URL: {url}")
    print(f"Issue: Previous scraping captured navigation/structure, not dividend table")
    print(f"Solution: Using Selenium spider with extended wait times and specific selectors")
    print()
    
    try:
        from pathlib import Path
        script_dir = Path(__file__).parent.absolute()
        project_dir = script_dir / 'universal_scraper'
        
        # Change to the scrapy project directory
        original_cwd = os.getcwd()
        os.chdir(project_dir)
        
        # Add the project directory to Python path
        sys.path.insert(0, str(project_dir))
        
        # Import scrapy modules
        from scrapy.crawler import CrawlerProcess
        from scrapy.utils.project import get_project_settings
        
        # Configure settings specifically for dynamic content
        settings = get_project_settings()
        settings.set('ROBOTSTXT_OBEY', True)
        settings.set('DOWNLOAD_DELAY', 5)  # Longer delay for JS rendering
        settings.set('LOG_LEVEL', 'INFO')
        settings.set('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Selenium-specific settings for dynamic content
        settings.set('SELENIUM_HEADLESS', True)
        settings.set('SELENIUM_TIMEOUT', 45)  # Extended timeout for page load
        settings.set('SELENIUM_IMPLICIT_WAIT', 10)  # Wait for elements
        
        # Set feed exports to save to file
        settings.set('FEEDS', {
            output_file: {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'indent': 2
            }
        })
        
        # Create crawler process
        process = CrawlerProcess(settings)
        
        # Use selenium spider for JavaScript content
        print("🤖 Using Selenium spider for JavaScript-rendered dividend table...")
        process.crawl('selenium_spider', url=url)
        
        # Start the crawling process
        process.start(stop_after_crawl=True)
        
        print("✅ Selenium scraping completed!")
        
        # Move output file to parent directory for easier access
        if os.path.exists(output_file):
            import shutil
            dest_path = original_cwd + "\\" + output_file
            shutil.move(output_file, dest_path)
            print(f"📁 Output file moved to: {dest_path}")
            
            # Analyze the scraped data for dividend-specific content
            analyze_dividend_specific_data(dest_path)
        else:
            print("⚠️  Output file not found")
        
    except Exception as e:
        print(f"❌ Selenium scraping failed: {e}")
        print("💡 This likely means Selenium/ChromeDriver needs to be installed")
        print("💡 Falling back to enhanced universal spider with longer waits...")
        
        # Fallback to enhanced universal spider
        try:
            # Enhanced universal spider with more aggressive extraction
            settings = get_project_settings()
            settings.set('ROBOTSTXT_OBEY', True)
            settings.set('DOWNLOAD_DELAY', 5)
            settings.set('LOG_LEVEL', 'INFO')
            settings.set('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Set feed exports
            settings.set('FEEDS', {
                output_file: {
                    'format': 'json',
                    'encoding': 'utf8',
                    'store_empty': False,
                    'indent': 2
                }
            })
            
            process = CrawlerProcess(settings)
            process.crawl('universal', url=url)
            process.start(stop_after_crawl=True)
            
            if os.path.exists(output_file):
                import shutil
                dest_path = original_cwd + "\\" + output_file
                shutil.move(output_file, dest_path)
                print(f"📁 Fallback output file moved to: {dest_path}")
                analyze_dividend_specific_data(dest_path)
        
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")
    
    finally:
        # Restore original working directory
        os.chdir(original_cwd)
        if str(project_dir) in sys.path:
            sys.path.remove(str(project_dir))

def analyze_dividend_specific_data(file_path):
    """Analyze scraped data specifically for dividend table information"""
    print()
    print("📈 Analyzing for Dividend-Specific Data")
    print("-" * 50)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list) and len(data) > 0:
            item = data[0]
        else:
            item = data
        
        text_content = item.get('text_content', '').lower()
        html_content = item.get('html_content', '')
        
        print(f"🔍 Content Analysis:")
        print(f"   Total characters: {len(html_content):,}")
        print(f"   Text characters: {len(text_content):,}")
        print()
        
        # Look for specific dividend table indicators
        dividend_indicators = [
            'dividend history',
            'ex-dividend date',
            'ex date',
            'payment date',
            'pay date',
            'record date',
            'quarterly dividend',
            'dividend per share',
            'dividend yield',
            'table',
            'thead',
            'tbody',
            'tr',
            'td'
        ]
        
        found_indicators = []
        for indicator in dividend_indicators:
            if indicator in text_content:
                found_indicators.append(indicator)
        
        print(f"📊 Dividend Table Indicators Found: {len(found_indicators)}/{len(dividend_indicators)}")
        print(f"   Found: {', '.join(found_indicators) if found_indicators else 'None'}")
        print()
        
        # Look for specific dividend amounts and dates
        dividend_amounts = re.findall(r'\$[0-9]+\.?[0-9]*', text_content)
        dividend_dates = re.findall(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{1,2},? \d{4}', text_content)
        standard_dates = re.findall(r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}', text_content)
        
        print(f"💰 Financial Data Extraction:")
        if dividend_amounts:
            print(f"   Dividend amounts: {dividend_amounts[:15]}...")  # Show first 15
        if dividend_dates:
            print(f"   Dividend dates (named): {dividend_dates[:10]}...")  # Show first 10
        if standard_dates:
            print(f"   Standard dates: {standard_dates[:10]}...")  # Show first 10
        
        # Check for JavaScript/dynamic content indicators
        js_indicators = [
            '__nuxt',
            'data-server-rendered',
            'vue',
            'react',
            'angular',
            'loading',
            'please wait',
            'javascript required'
        ]
        
        js_found = []
        for indicator in js_indicators:
            if indicator in html_content.lower():
                js_found.append(indicator)
        
        print()
        print(f"🔧 JavaScript Framework Detection:")
        print(f"   JS indicators found: {', '.join(js_found) if js_found else 'None'}")
        
        if '__nuxt' in js_found:
            print("   ⚡ Detected: Nuxt.js (Vue.js framework)")
            print("   📝 Note: This explains why dividend data requires JavaScript rendering")
        
        # Specific analysis for Morningstar's structure
        if 'morningstar' in text_content:
            print()
            print("🏢 Morningstar-Specific Analysis:")
            
            # Look for common Morningstar dividend table patterns
            morningstar_patterns = [
                'dividend.*history',
                'quarterly.*dividend',
                'annual.*dividend',
                'dividend.*yield',
                'ex.*dividend.*date',
                'payment.*date'
            ]
            
            for pattern in morningstar_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    print(f"   Found pattern '{pattern}': {len(matches)} matches")
        
        # Generate recommendations
        print()
        print("💡 Recommendations:")
        
        if len(found_indicators) < 5:
            print("   ❌ Low dividend table indicators suggest JavaScript rendering is required")
            print("   🔧 Solution: Use Selenium spider with extended wait times")
            print("   🔧 Alternative: Look for API endpoints or direct data feeds")
        
        if '__nuxt' in js_found:
            print("   ⚡ Nuxt.js detected - page uses server-side rendering + client hydration")
            print("   🔧 Solution: Wait for client-side JavaScript to complete data loading")
            print("   🔧 Alternative: Check for XHR/API calls that load dividend data")
        
        if dividend_amounts and dividend_dates:
            print("   ✅ Some financial data detected - partial success")
            print("   🔧 Optimization: Focus extraction on detected patterns")
        
        # Save detailed analysis
        analysis_file = file_path.replace('.json', '_detailed_analysis.txt')
        with open(analysis_file, 'w', encoding='utf-8') as f:
            f.write(f"Morningstar AAPL Dividend Data Analysis\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Source file: {file_path}\n\n")
            
            f.write(f"ISSUE IDENTIFIED:\n")
            f.write(f"Previous scraping captured page structure/navigation but not actual dividend table data.\n")
            f.write(f"This is because Morningstar uses Nuxt.js for dynamic content loading.\n\n")
            
            f.write(f"CONTENT ANALYSIS:\n")
            f.write(f"- Total HTML: {len(html_content):,} characters\n")
            f.write(f"- Text content: {len(text_content):,} characters\n")
            f.write(f"- Dividend indicators: {len(found_indicators)}/{len(dividend_indicators)}\n")
            f.write(f"- JavaScript framework: {', '.join(js_found) if js_found else 'None detected'}\n\n")
            
            f.write(f"EXTRACTED DATA:\n")
            f.write(f"- Dividend amounts: {dividend_amounts[:20] if dividend_amounts else 'None'}\n")
            f.write(f"- Dividend dates: {dividend_dates[:15] if dividend_dates else 'None'}\n")
            f.write(f"- Standard dates: {standard_dates[:15] if standard_dates else 'None'}\n\n")
            
            f.write(f"TECHNICAL SOLUTION:\n")
            f.write(f"1. Use Selenium WebDriver with Chrome/Chromium\n")
            f.write(f"2. Wait for JavaScript to fully load dividend table\n")
            f.write(f"3. Extract table data using CSS selectors or XPath\n")
            f.write(f"4. Alternative: Intercept XHR/API calls for direct data access\n")
        
        print(f"📝 Detailed analysis saved to: {analysis_file}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

def main():
    """Main function"""
    print("🚀 Starting Improved Morningstar Dividend Data Extraction")
    print()
    print("📋 Background:")
    print("   The previous test showed our scraper captured page structure")
    print("   but not the actual dividend table data. This is because")
    print("   Morningstar uses JavaScript (Nuxt.js) to render dividend content.")
    print()
    print("🎯 This test will:")
    print("   1. Use Selenium for JavaScript rendering")
    print("   2. Wait for dynamic content to load")
    print("   3. Extract specific dividend table data")
    print("   4. Provide recommendations for optimal scraping")
    print()
    
    # Run the improved test
    test_morningstar_dividend_data_extraction()
    
    print()
    print("🎯 Test completed! Check the output for dividend-specific analysis.")

if __name__ == "__main__":
    main()
