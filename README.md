# Universal Web Scraper

A powerful, flexible web scraping tool built with Python and Scrapy that can handle various anti-scraping measures and scrape content from any website.

## Features

- **Universal Compatibility**: Scrape static and dynamic websites
- **Anti-Scraping Measures**:
  - Configurable user agents
  - Rate limiting and delays
  - AutoThrottle for adaptive throttling
  - Custom request headers
- **Flexible Data Extraction**: Extract titles, links, and custom data
- **Command Line Interface**: Easy to use with URL arguments

## Installation

1. Clone or download the project
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`

## Usage

### Basic Usage
```bash
cd universal_scraper
scrapy crawl universal
```

### Scrape Specific URL
```bash
scrapy crawl universal -a url=https://example.com
```

### Export Data
```bash
scrapy crawl universal -a url=https://example.com -o output.json
```

## Configuration

Edit `universal_scraper/settings.py` to configure:
- User agents
- Request delays
- Concurrency settings
- AutoThrottle parameters

## Project Structure

```
universal_scraper/
├── scrapy.cfg
├── universal_scraper/
│   ├── __init__.py
│   ├── items.py
│   ├── middlewares.py
│   ├── pipelines.py
│   ├── settings.py
│   └── spiders/
│       ├── __init__.py
│       └── universal.py
```

## Development

- Add new spiders in `universal_scraper/spiders/`
- Implement custom middlewares in `universal_scraper/middlewares.py`
- Configure pipelines in `universal_scraper/pipelines.py`

## License

This project is for educational purposes. Always respect website terms of service and robots.txt files.
