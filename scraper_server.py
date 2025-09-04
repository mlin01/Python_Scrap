#!/usr/bin/env python3
"""
HTTP Server Wrapper for Quick Scraper
Provides REST API interface for the quick_scraper functionality
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import os
import sys
import time
from urllib.parse import urlparse, parse_qs

class ScraperHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/scrape'):
            self.handle_scrape_request()
        elif self.path == '/':
            self.serve_api_docs()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        if self.path.startswith('/scrape'):
            self.handle_scrape_request()
        else:
            self.send_error(404, "Not Found")
    
    def handle_scrape_request(self):
        try:
            # Parse request data
            request_data = {}
            
            if self.command == 'POST':
                # Handle POST with JSON body
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    try:
                        request_data = json.loads(post_data.decode('utf-8'))
                    except json.JSONDecodeError:
                        self.send_error(400, "Invalid JSON in request body")
                        return
            else:
                # Handle GET with query parameters
                parsed_url = urlparse(self.path)
                query_params = parse_qs(parsed_url.query)
                request_data = {
                    'url': query_params.get('url', [''])[0],
                    'mode': query_params.get('mode', ['full'])[0]
                }
            
            # Extract parameters
            url = request_data.get('url', '').strip()
            mode = request_data.get('mode', 'full').strip()
            include_content = request_data.get('include_content', True)  # New parameter
            
            # Validate required parameters
            if not url:
                self.send_error(400, "URL parameter is required. Use either JSON body {'url': '...', 'mode': '...'} or query params ?url=...&mode=...")
                return
            
            print(f"🚀 Processing scrape request:")
            print(f"   Method: {self.command}")
            print(f"   URL: {url}")
            print(f"   Mode: {mode}")
            print(f"   Include Content: {include_content}")
            
            # Run the scraper with --return-content flag (no file saving)
            start_time = time.time()
            cmd_args = [sys.executable, 'quick_scraper.py', url, mode]
            if include_content:
                cmd_args.append('--return-content')
            
            result = subprocess.run(cmd_args, capture_output=True, text=True, cwd=os.getcwd())
            
            duration = time.time() - start_time
            
            # Parse JSON output from the scraper if using return-content mode
            content_data = None
            scraper_json_data = None
            
            if include_content and result.returncode == 0:
                # Look for JSON markers in stdout
                stdout_lines = result.stdout
                if "JSON_RESULT_START" in stdout_lines and "JSON_RESULT_END" in stdout_lines:
                    try:
                        start_marker = stdout_lines.find("JSON_RESULT_START") + len("JSON_RESULT_START")
                        end_marker = stdout_lines.find("JSON_RESULT_END")
                        json_text = stdout_lines[start_marker:end_marker].strip()
                        
                        scraper_json_data = json.loads(json_text)
                        content_data = scraper_json_data.get('content', '')
                        
                        # Limit content size to prevent response overflow
                        if len(content_data) > 1000000:  # 1MB limit
                            content_data = content_data[:1000000] + "\n\n... [CONTENT TRUNCATED - Response too large] ..."
                        
                        print(f"✅ Parsed JSON result from scraper: {scraper_json_data.get('status', 'unknown status')}")
                    except (json.JSONDecodeError, ValueError) as e:
                        print(f"❌ Error parsing JSON from scraper output: {str(e)}")
                        print(f"Raw stdout: {result.stdout[:500]}...")
                else:
                    print(f"⚠️ No JSON markers found in scraper output")
            
            # Prepare response
            response_data = {
                'success': result.returncode == 0,
                'url': url,
                'mode': mode,
                'duration': round(duration, 2),
                'stdout': result.stdout,
                'stderr': result.stderr if result.stderr else None,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'content': content_data  # Include the actual content
            }
            
            # Add scraper-specific data if available
            if scraper_json_data:
                response_data.update({
                    'scraper_status': scraper_json_data.get('status'),
                    'scraper_duration': scraper_json_data.get('duration'),
                    'scraper_analysis': scraper_json_data.get('analysis'),
                    'content_length': len(content_data) if content_data else 0,
                    'mode_used': scraper_json_data.get('mode'),
                    'output_exists': True
                })
            else:
                response_data['output_exists'] = False
            
            # Send response
            if result.returncode == 0 and content_data and include_content:
                # Success: return just the content directly
                self.send_response(200)
                self.send_header('Content-type', 'text/plain; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(content_data.encode('utf-8'))
            else:
                # Error or no content: return JSON with error info
                response_data = {
                    'success': result.returncode == 0,
                    'url': url,
                    'mode': mode,
                    'duration': round(duration, 2),
                    'stderr': result.stderr if result.stderr else None,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'error': 'Scraping failed or no content returned'
                }
                
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps(response_data, indent=2).encode('utf-8'))
            
            print(f"✅ Request completed in {duration:.2f}s")
            
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON in request body")
        except Exception as e:
            print(f"❌ Error handling request: {str(e)}")
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def serve_api_docs(self):
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Quick Scraper HTTP API</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .method { background: #007acc; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }
        code { background: #f0f0f0; padding: 2px 5px; border-radius: 3px; }
        pre { background: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>🚀 Quick Scraper HTTP API</h1>
    
    <h2>📡 Endpoints</h2>
    
    <div class="endpoint">
        <h3><span class="method">POST</span> /scrape</h3>
        <p>Scrape a website and return content directly in response (no file saving)</p>
        <h4>Request Body (JSON):</h4>
        <pre>{
  "url": "https://www.morningstar.com/stocks/xnas/aapl/dividends",
  "mode": "full",  // "stats" or "full"
  "include_content": true  // true to include content in response, false for summary only
}</pre>
        
        <h4>Response:</h4>
        <pre>{
  "success": true,
  "url": "https://...",
  "mode": "full",
  "duration": 45.23,
  "output_exists": true,
  "content_length": 683453,
  "content": "<!DOCTYPE html>...",  // Actual scraped content (if include_content=true)
  "scraper_status": "success",
  "scraper_duration": 44.8,
  "timestamp": "2025-09-04 10:30:45"
}</pre>
    </div>
    
    <div class="endpoint">
        <h3><span class="method">GET</span> /scrape</h3>
        <p>Scrape using query parameters</p>
        <h4>Example:</h4>
        <code>/scrape?url=https://finance.yahoo.com/quote/AAPL&mode=stats&include_content=true</code>
    </div>
    
    <h2>📝 Usage with .http files</h2>
    <p>Use the provided <code>test_scraper.http</code> file with VS Code REST Client extension to test different endpoints.</p>
    
    <h2>📊 Output</h2>
    <ul>
        <li><strong>include_content=true:</strong> Content returned directly in HTTP response (no file saving)</li>
        <li><strong>include_content=false:</strong> Only summary and metadata returned</li>
        <li><strong>Stats mode:</strong> Analysis and key data points</li>
        <li><strong>Full mode:</strong> Complete HTML content (up to 1MB in response)</li>
        <li><strong>Error cases:</strong> Error details included in response</li>
    </ul>
    
    <h2>🔗 Test URLs</h2>
    <ul>
        <li>Apple Dividends: <code>https://www.morningstar.com/stocks/xnas/aapl/dividends</code></li>
        <li>Yahoo Finance: <code>https://finance.yahoo.com/quote/AAPL</code></li>
        <li>MacroTrends: <code>https://www.macrotrends.net/stocks/charts/AAPL/apple/balance-sheet</code></li>
    </ul>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def log_message(self, format, *args):
        # Custom logging format
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    
    print(f"🌐 Starting Quick Scraper HTTP Server on port {port}")
    print(f"📡 API Documentation: http://localhost:{port}/")
    print(f"🧪 Test endpoint: http://localhost:{port}/scrape")
    print(f"📄 Use test_scraper.http file for testing")
    print(f"⏹️  Press Ctrl+C to stop\n")
    
    server = HTTPServer(('localhost', port), ScraperHTTPHandler)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Shutting down server...")
        server.shutdown()

if __name__ == "__main__":
    main()
