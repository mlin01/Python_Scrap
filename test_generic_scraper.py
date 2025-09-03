#!/usr/bin/env python3
"""
Test the Generic Financial Scraper with common financial websites
"""

import sys
from easy_scraper import scrape_any_url, scrape_dividend_data
from website_configs import (
    build_morningstar_url,
    build_yahoo_finance_url,
    build_marketwatch_url
)

def test_morningstar_aapl():
    """Test Morningstar AAPL dividends page"""
    print("🍎 Testing Morningstar AAPL Dividends")
    print("=" * 40)
    
    url = build_morningstar_url('AAPL', 'dividends')
    print(f"URL: {url}")
    
    filename = scrape_any_url(url, 'summary')
    
    if filename:
        print("✅ Test completed successfully!")
        return True
    else:
        print("❌ Test failed!")
        return False

def test_yahoo_finance_aapl():
    """Test Yahoo Finance AAPL quote page"""
    print("\n🍎 Testing Yahoo Finance AAPL Quote")
    print("=" * 40)
    
    url = build_yahoo_finance_url('AAPL')
    print(f"URL: {url}")
    
    filename = scrape_any_url(url, 'summary')
    
    if filename:
        print("✅ Test completed successfully!")
        return True
    else:
        print("❌ Test failed!")
        return False

def test_marketwatch_aapl():
    """Test MarketWatch AAPL page"""
    print("\n🍎 Testing MarketWatch AAPL")
    print("=" * 40)
    
    url = build_marketwatch_url('AAPL')
    print(f"URL: {url}")
    
    filename = scrape_any_url(url, 'summary')
    
    if filename:
        print("✅ Test completed successfully!")
        return True
    else:
        print("❌ Test failed!")
        return False

def test_dividend_analysis():
    """Test comprehensive dividend analysis"""
    print("\n💰 Testing Comprehensive Dividend Analysis")
    print("=" * 50)
    
    try:
        results = scrape_dividend_data('AAPL')
        
        if results:
            print("✅ Dividend analysis completed!")
            print(f"📊 Summary:")
            summary = results.get('summary', {})
            print(f"   - Currency amounts found: {len(summary.get('total_dividend_amounts', []))}")
            print(f"   - Dates found: {len(summary.get('total_dividend_dates', []))}")
            print(f"   - Dividend keywords: {summary.get('dividend_keywords', [])}")
            print(f"   - Financial tables: {len(summary.get('financial_tables', []))}")
            return True
        else:
            print("❌ Dividend analysis failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error in dividend analysis: {e}")
        return False

def test_custom_url():
    """Test with the user's original URL"""
    print("\n🌐 Testing User's Original URL")
    print("=" * 40)
    
    url = "https://www.morningstar.com/stocks/xnas/aapl/dividends"
    print(f"URL: {url}")
    
    filename = scrape_any_url(url, 'summary')
    
    if filename:
        print("✅ Test completed successfully!")
        print("📄 Check the summary file for detailed results")
        return True
    else:
        print("❌ Test failed!")
        return False

def main():
    """Run all tests"""
    
    print("🚀 Generic Financial Scraper Test Suite")
    print("=" * 50)
    print("This will test the generic scraper with multiple financial websites")
    print("Each test uses automatic configuration based on the website")
    print()
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        
        if test_name == 'morningstar':
            test_morningstar_aapl()
        elif test_name == 'yahoo':
            test_yahoo_finance_aapl()
        elif test_name == 'marketwatch':
            test_marketwatch_aapl()
        elif test_name == 'dividend':
            test_dividend_analysis()
        elif test_name == 'custom':
            test_custom_url()
        else:
            print(f"❌ Unknown test: {test_name}")
            print("Available tests: morningstar, yahoo, marketwatch, dividend, custom")
    else:
        # Run all tests
        tests = [
            ("Morningstar Test", test_morningstar_aapl),
            ("Yahoo Finance Test", test_yahoo_finance_aapl),
            ("MarketWatch Test", test_marketwatch_aapl),
            ("Dividend Analysis Test", test_dividend_analysis),
            ("Custom URL Test", test_custom_url)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n▶️  Running {test_name}...")
            try:
                success = test_func()
                results.append((test_name, success))
            except Exception as e:
                print(f"❌ {test_name} failed with error: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} - {test_name}")
            if success:
                passed += 1
        
        print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! The generic scraper is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the individual results above.")

if __name__ == "__main__":
    main()
