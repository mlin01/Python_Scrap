# Universal Web Scraper - Advanced Usage Guide

## Quick Start

### 1. Installation and Setup

```bash
# Clone the repository
git clone <repository-url>
cd universal-web-scraper

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements_proper.txt

# Copy environment template
copy .env.example .env
# Edit .env file with your configuration
```

### 2. Basic Usage

```bash
# Simple scraping
cd universal_scraper
scrapy crawl universal -a url=https://example.com

# With output file
scrapy crawl universal -a url=https://example.com -o output.json

# Using the convenience script
python scraper.py json https://example.com
python scraper.py html https://example.com
```

## Advanced Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Basic settings
DEBUG_MODE=False
REQUEST_DELAY=3.0
CONCURRENT_REQUESTS=1

# Enable proxy rotation
PROXY_ENABLED=True
PROXY_LIST=["http://proxy1:8080", "http://proxy2:8080"]

# Enable CAPTCHA solving
CAPTCHA_SOLVER_ENABLED=True
CAPTCHA_API_KEY=your_api_key_here
```

### Custom Settings

Edit `universal_scraper/settings.py` for advanced configuration:

```python
# Custom user agents
USER_AGENTS_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
]

# Enable custom middlewares
DOWNLOADER_MIDDLEWARES = {
    'universal_scraper.middlewares.ProxyRotationMiddleware': 350,
    'universal_scraper.middlewares.CaptchaSolverMiddleware': 400,
    'universal_scraper.middlewares.user_agent_rotation.UserAgentRotationMiddleware': 400,
}
```

## Anti-Scraping Bypass Techniques

### 1. User Agent Rotation
Automatically rotates through different browser user agents:

```python
# Enabled by default
USER_AGENT_ROTATION_ENABLED = True
```

### 2. Proxy Rotation
Rotate through multiple proxy servers:

```python
PROXY_ROTATION_ENABLED = True
PROXY_LIST = [
    "http://proxy1:8080",
    "http://proxy2:8080",
    "http://username:password@proxy3:8080"
]
```

### 3. Rate Limiting and Delays
Configure delays to avoid triggering rate limits:

```python
DOWNLOAD_DELAY = 2.0  # 2 seconds between requests
RANDOMIZE_DOWNLOAD_DELAY = 0.5  # 0.5 * to 1.5 * DOWNLOAD_DELAY
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
```

### 4. JavaScript Rendering
For sites that require JavaScript execution:

```bash
# Use Selenium spider for JavaScript-heavy sites
scrapy crawl selenium_spider -a url=https://spa-website.com
```

### 5. CAPTCHA Solving
Integrate with CAPTCHA solving services:

```python
CAPTCHA_SOLVER_ENABLED = True
CAPTCHA_SERVICE_API_KEY = "your_api_key"
```

## Handling Different Website Types

### Static HTML Sites
```bash
scrapy crawl universal -a url=https://static-site.com
```

### JavaScript-Heavy Sites
```bash
scrapy crawl selenium_spider -a url=https://dynamic-site.com
```

### API Endpoints
```bash
scrapy crawl universal -a url=https://api.example.com/data
```

### Financial Data (Yahoo Finance)
```bash
scrapy crawl universal -a url=https://finance.yahoo.com/quote/AAPL
```

## Output Formats

### JSON Output (Default)
```bash
scrapy crawl universal -a url=https://example.com -o data.json
```

### CSV Output
```bash
scrapy crawl universal -a url=https://example.com -o data.csv
```

### Custom Fields Only
```bash
scrapy crawl universal -a url=https://example.com -a format=html -o content.json
```

## Testing and Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-scrapy

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_universal_spider.py

# Run with coverage
pytest --cov=universal_scraper tests/
```

### Development Mode
```bash
# Enable debug mode
export DEBUG_MODE=True

# Verbose logging
export LOG_LEVEL=DEBUG

# Test with local server
scrapy crawl universal -a url=http://localhost:8000
```

## Performance Optimization

### Concurrent Requests
```python
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8
```

### Memory Optimization
```python
# Disable item caching for large datasets
ITEM_PIPELINES = {
    'universal_scraper.pipelines.StreamingPipeline': 100,
}

# Enable HTTP caching for development
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600  # 1 hour
```

### Database Storage
```python
# Store data in database instead of files
ITEM_PIPELINES = {
    'universal_scraper.pipelines.DatabasePipeline': 300,
}

DATABASE_URL = "postgresql://user:pass@localhost/scraperdb"
```

## Monitoring and Logging

### Log Files
- `logs/universal_scraper.log` - General logs
- `logs/universal_scraper_errors.log` - Error-only logs
- `logs/scrapy.log` - Scrapy framework logs

### Statistics
Monitor scraping performance:
```python
STATS_CLASS = 'universal_scraper.stats.CustomStatsCollector'
```

### Alerts
Set up alerts for critical issues:
```python
ALERT_EMAIL_ENABLED = True
ALERT_EMAIL_RECIPIENTS = ["admin@example.com"]
ALERT_THRESHOLDS = {
    'error_rate': 0.1,  # 10% error rate
    'captcha_rate': 0.05  # 5% CAPTCHA rate
}
```

## Legal and Ethical Considerations

### Respect robots.txt
```python
ROBOTSTXT_OBEY = True  # Always respect robots.txt
```

### Rate Limiting
Always implement reasonable delays:
```python
DOWNLOAD_DELAY = 1.0  # Minimum 1 second delay
```

### User Agent Identification
Use descriptive user agents:
```python
USER_AGENT = "MyBot/1.0 (+http://mywebsite.com/bot-info)"
```

### Terms of Service
Always review and comply with website terms of service before scraping.

## Troubleshooting

### Common Issues

#### 1. No Data Extracted
- Check if JavaScript is required: Use selenium_spider
- Verify CSS selectors are correct
- Check for CAPTCHA or blocking

#### 2. Getting Blocked
- Enable proxy rotation
- Increase request delays
- Rotate user agents
- Check robots.txt compliance

#### 3. Memory Issues
- Enable streaming pipelines
- Reduce concurrent requests
- Clear browser cache for Selenium

#### 4. Selenium Issues
- Install ChromeDriver: `pip install chromedriver-autoinstaller`
- Check Chrome/Chromium installation
- Verify headless mode settings

### Debug Mode
Enable detailed logging:
```bash
export DEBUG_MODE=True
export LOG_LEVEL=DEBUG
scrapy crawl universal -a url=https://example.com -L DEBUG
```

### Contact Support
For additional help:
- Check the documentation
- Review error logs
- Create GitHub issues for bugs
- Follow ethical scraping guidelines
