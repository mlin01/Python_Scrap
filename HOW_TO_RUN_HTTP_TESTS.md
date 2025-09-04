# How to Run test_scraper.http

## 🚀 Quick Start Guide

### Step 1: Install VS Code REST Client Extension
1. Open VS Code
2. Press `Ctrl+Shift+X` (Extensions)
3. Search for "REST Client" by Huachao Mao
4. Click "Install"

### Step 2: Start the HTTP Server
Open a terminal in your project directory and run:
```powershell
python scraper_server.py
```

You should see:
```
🌐 Starting Quick Scraper HTTP Server on port 8000
📡 API Documentation: http://localhost:8000/
🧪 Test endpoint: http://localhost:8000/scrape
📄 Use test_scraper.http file for testing
⏹️  Press Ctrl+C to stop
```

### Step 3: Use the .http File
1. Open `test_scraper.http` in VS Code
2. You'll see "Send Request" links above each test section
3. Click any "Send Request" link to execute that test
4. Results will appear in a new VS Code tab

## 📋 Available Tests

### 🧪 Test Cases:
1. **Apple Dividends - Stats**: Quick stats from Morningstar
2. **Apple Dividends - Full**: Complete HTML content
3. **Microsoft Dividends - Stats**: Microsoft dividend data summary
4. **Yahoo Finance - Full**: Yahoo Finance page content
5. **MacroTrends Balance Sheet**: Balance sheet data
6. **SEC EDGAR Filing**: SEC filing data
7. **Invalid URL Test**: Error handling test
8. **GET Request Test**: Alternative request method

## 🔄 Alternative Methods

### Method 1: Direct Command Line (No HTTP server needed)
```powershell
# Run individual tests directly
python quick_scraper.py "https://www.morningstar.com/stocks/xnas/aapl/dividends" stats

# Run batch tests
python run_tests.py
```

### Method 2: Manual HTTP Requests
You can also test manually using curl:
```powershell
# POST request with JSON
curl -X POST http://localhost:8000/scrape `
  -H "Content-Type: application/json" `
  -d '{"url": "https://www.morningstar.com/stocks/xnas/aapl/dividends", "mode": "stats"}'

# GET request with query parameters
curl "http://localhost:8000/scrape?url=https://www.morningstar.com/stocks/xnas/aapl/dividends&mode=stats"
```

## 📊 Understanding Results

### Successful Response Example:
```json
{
  "success": true,
  "url": "https://www.morningstar.com/stocks/xnas/aapl/dividends",
  "mode": "stats",
  "temp_file": "C:\\Users\\Username\\AppData\\Local\\Temp\\scraper_morningstar_com_a1b2c3d4_1725456789_stats.md",
  "duration": 52.61,
  "output_exists": true,
  "file_size": 1234,
  "timestamp": "2025-09-04 10:30:45"
}
```

### Error Response Example:
```json
{
  "success": false,
  "url": "https://invalid-url.com",
  "mode": "stats",
  "temp_file": null,
  "duration": 30.0,
  "output_exists": false,
  "stderr": "Connection error",
  "timestamp": "2025-09-04 10:31:00"
}
```

## 🛠️ Troubleshooting

### Problem: "URL parameter is required"
**Solution**: Make sure your request has proper JSON body or query parameters

### Problem: Server not responding
**Solution**: 
1. Check if `scraper_server.py` is running
2. Verify the server is on port 8000
3. Try restarting the server

### Problem: REST Client not working
**Solution**:
1. Make sure REST Client extension is installed
2. Try right-clicking in the .http file and select "Send Request"
3. Check VS Code output panel for errors

### Problem: Tests taking too long
**Reason**: Anti-bot challenges can take 30-60 seconds
**Solution**: Be patient, this is normal for protected sites

## 📁 Output Files

All test results are saved to temporary files:
- **Stats mode**: `*.md` files with summary
- **Full mode**: `*.html` files with complete content  
- **Errors**: `*_error.md` files with error details

File paths are shown in the HTTP response `temp_file` field.

## 💡 Tips

1. **Start Simple**: Try Test 8 (GET request) first - it's the simplest
2. **Check Server Logs**: Watch the terminal running the server for detailed logs
3. **Use Stats Mode**: It's faster than full mode for testing
4. **Be Patient**: Financial sites often have anti-bot protection
5. **Check Temp Files**: The actual scraped content is in the temporary files

---

**Happy Testing! 🧪🚀**
