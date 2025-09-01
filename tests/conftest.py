"""
Test configuration and fixtures for the universal scraper
"""
import pytest
import tempfile
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add the universal_scraper directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "universal_scraper"))

try:
    from scrapy.http import HtmlResponse, Request
    from universal_scraper.spiders.universal import UniversalSpider
    SCRAPY_AVAILABLE = True
except ImportError:
    # Mock classes if Scrapy is not available
    class HtmlResponse:
        pass
    class Request:
        pass
    class UniversalSpider:
        pass
    SCRAPY_AVAILABLE = False


@pytest.fixture
def sample_html():
    """Sample HTML content for testing"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <h1>Main Heading</h1>
        <p>This is a test paragraph.</p>
        <a href="https://example.com">External Link</a>
        <a href="/internal">Internal Link</a>
        <div class="content">
            <p>More content here</p>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_json():
    """Sample JSON content for testing"""
    return {
        "data": [
            {"id": 1, "name": "Item 1", "url": "https://example.com/item1"},
            {"id": 2, "name": "Item 2", "url": "https://example.com/item2"}
        ],
        "meta": {
            "total": 2,
            "page": 1
        }
    }


@pytest.fixture
def mock_response(sample_html):
    """Create a mock Scrapy response"""
    if not SCRAPY_AVAILABLE:
        pytest.skip("Scrapy not available")
    
    request = Request(url="https://example.com")
    response = HtmlResponse(
        url="https://example.com",
        body=sample_html.encode('utf-8'),
        encoding='utf-8',
        request=request
    )
    return response


@pytest.fixture
def mock_json_response(sample_json):
    """Create a mock JSON response"""
    if not SCRAPY_AVAILABLE:
        pytest.skip("Scrapy not available")
        
    import json
    request = Request(url="https://api.example.com/data")
    response = HtmlResponse(
        url="https://api.example.com/data",
        body=json.dumps(sample_json).encode('utf-8'),
        encoding='utf-8',
        request=request,
        headers={'Content-Type': 'application/json'}
    )
    return response


@pytest.fixture
def spider():
    """Create a spider instance for testing"""
    if not SCRAPY_AVAILABLE:
        pytest.skip("Scrapy not available")
    
    return UniversalSpider(url="https://example.com")


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)
