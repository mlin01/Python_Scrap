#!/usr/bin/env python3
"""
Batch Test Runner for Quick Scraper
Runs multiple test cases and saves results to files
"""

import subprocess
import sys
import time
import os
import json

# Test cases configuration
TEST_CASES = [
    {
        "name": "Apple Dividends - Stats",
        "url": "https://www.morningstar.com/stocks/xnas/aapl/dividends",
        "mode": "stats"
    },
    {
        "name": "Apple Dividends - Full",
        "url": "https://www.morningstar.com/stocks/xnas/aapl/dividends", 
        "mode": "full"
    },
    {
        "name": "Microsoft Dividends - Stats",
        "url": "https://www.morningstar.com/stocks/xnas/msft/dividends",
        "mode": "stats"
    },
    {
        "name": "Yahoo Finance - Full",
        "url": "https://finance.yahoo.com/quote/AAPL",
        "mode": "full"
    },
    {
        "name": "MacroTrends Balance Sheet - Stats",
        "url": "https://www.macrotrends.net/stocks/charts/AAPL/apple/balance-sheet",
        "mode": "stats"
    }
]

def run_test_case(test_case):
    """Run a single test case"""
    print(f"\n🧪 Running Test: {test_case['name']}")
    print(f"   URL: {test_case['url']}")
    print(f"   Mode: {test_case['mode']}")
    
    start_time = time.time()
    
    try:
        # Run the scraper (no output file specified - will use temp files)
        result = subprocess.run([
            sys.executable, 'quick_scraper.py', 
            test_case['url'], 
            test_case['mode']
        ], capture_output=True, text=True, timeout=120)
        
        duration = time.time() - start_time
        
        # Check results
        success = result.returncode == 0
        
        # Extract temp file path from stdout
        temp_file_path = None
        if success and "📄" in result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if "📄" in line and ("/tmp/" in line or "\\temp\\" in line.lower() or "\\tmp\\" in line):
                    # Extract file path from the line
                    temp_file_path = line.split("📄")[-1].strip()
                    break
        
        # Check if temp file exists
        output_exists = False
        file_size = 0
        
        if temp_file_path and os.path.exists(temp_file_path):
            output_exists = True
            file_size = os.path.getsize(temp_file_path)
        
        # Print results
        status = "✅ PASS" if success and output_exists else "❌ FAIL"
        print(f"   {status} - {duration:.2f}s")
        
        if output_exists:
            print(f"   📄 Temp File: {temp_file_path} ({file_size:,} bytes)")
        else:
            print(f"   ❌ No temporary file created")
        
        if result.stdout:
            print(f"   📝 Output: {result.stdout.strip()}")
        
        if result.stderr:
            print(f"   ⚠️  Error: {result.stderr.strip()}")
        
        return {
            "name": test_case['name'],
            "url": test_case['url'],
            "mode": test_case['mode'],
            "temp_file": temp_file_path,
            "success": success,
            "output_exists": output_exists,
            "file_size": file_size,
            "duration": round(duration, 2),
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip() if result.stderr else None
        }
        
    except subprocess.TimeoutExpired:
        print(f"   ⏰ TIMEOUT - Test exceeded 120 seconds")
        return {
            "name": test_case['name'],
            "success": False,
            "error": "Timeout after 120 seconds",
            "duration": 120
        }
    except Exception as e:
        print(f"   ❌ ERROR - {str(e)}")
        return {
            "name": test_case['name'],
            "success": False,
            "error": str(e),
            "duration": time.time() - start_time
        }

def main():
    print("🚀 Quick Scraper Batch Test Runner")
    print("=" * 50)
    
    # Run all test cases
    results = []
    total_start = time.time()
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}]", end="")
        result = run_test_case(test_case)
        results.append(result)
        
        # Small delay between tests
        time.sleep(1)
    
    total_duration = time.time() - total_start
    
    # Generate summary report
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results if r.get('success', False))
    failed = len(results) - passed
    
    print(f"Total Tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Total Duration: {total_duration:.2f}s")
    
    # Detailed results
    print(f"\n📋 DETAILED RESULTS:")
    for result in results:
        status = "✅" if result.get('success', False) else "❌"
        duration = result.get('duration', 0)
        print(f"{status} {result['name']} ({duration:.2f}s)")
        
        if result.get('temp_file') and os.path.exists(result['temp_file']):
            size = result.get('file_size', 0)
            print(f"   📄 Temp File: {result['temp_file']} ({size:,} bytes)")
        
        if result.get('error'):
            print(f"   ❌ Error: {result['error']}")
    
    # Save detailed results to JSON (in temp directory)
    import tempfile
    temp_dir = tempfile.gettempdir()
    report_file = f"{temp_dir}/scraper_test_report_{int(time.time())}.json"
    with open(report_file, 'w') as f:
        json.dump({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': len(results),
            'passed': passed,
            'failed': failed,
            'total_duration': round(total_duration, 2),
            'results': results
        }, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # List all temp files created
    print(f"\n📁 Generated Temporary Files:")
    temp_files = []
    for result in results:
        if result.get('temp_file') and os.path.exists(result['temp_file']):
            temp_files.append(result['temp_file'])
    
    if temp_files:
        for temp_file in temp_files:
            size = os.path.getsize(temp_file)
            print(f"   📄 {os.path.basename(temp_file)} ({size:,} bytes)")
            print(f"      Path: {temp_file}")
    else:
        print("   No temporary files found")
    
    print(f"\n💡 Note: Temporary files will be automatically cleaned up by the system")

if __name__ == "__main__":
    main()
