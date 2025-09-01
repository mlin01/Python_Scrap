"""
Tests for the Universal Spider
"""
import pytest
import json
from datetime import datetime
from scrapy.http import HtmlResponse, Request
from universal_scraper.spiders.universal import UniversalSpider
from universal_scraper.items import UniversalScraperItem


class TestUniversalSpider:
    """Test cases for the Universal Spider"""
    
    def test_spider_initialization_with_url(self):
        """Test spider initialization with URL parameter"""
        url = "https://example.com"
        spider = UniversalSpider(url=url)
        
        assert spider.start_urls == [url]
        assert "example.com" in spider.allowed_domains
    
    def test_spider_initialization_without_url(self):
        """Test spider initialization without URL parameter"""
        spider = UniversalSpider()
        
        assert "example.com" in spider.allowed_domains
        assert "https://example.com" in spider.start_urls
    
    def test_parse_html_response(self, spider, mock_response):
        """Test parsing of HTML response"""
        results = list(spider.parse(mock_response))
        
        assert len(results) == 1
        item = results[0]
        
        assert item['url'] == "https://example.com"
        assert item['title'] == "Test Page"
        assert 'links' in item
        assert 'html_content' in item
        assert 'scraped_at' in item
    
    def test_parse_json_response(self, spider, mock_json_response):
        """Test parsing of JSON response"""
        results = list(spider.parse(mock_json_response))
        
        assert len(results) == 1
        item = results[0]
        
        assert item['url'] == "https://api.example.com/data"
        assert 'custom_data' in item
        assert isinstance(item['custom_data'], dict)
    
    def test_link_extraction(self, spider, mock_response):
        """Test link extraction functionality"""
        results = list(spider.parse(mock_response))
        item = results[0]
        
        assert 'internal_links' in item
        assert 'external_links' in item
        assert len(item['external_links']) > 0
        assert "https://example.com" in str(item['external_links'])
    
    def test_output_format_html(self, spider, mock_response):
        """Test HTML output format"""
        spider.output_format = 'html'
        results = list(spider.parse(mock_response))
        
        assert len(results) == 1
        item = results[0]
        
        assert 'html_content' in item
        assert 'url' in item
        assert 'title' in item
    
    def test_metadata_fields(self, spider, mock_response):
        """Test that all required metadata fields are present"""
        results = list(spider.parse(mock_response))
        item = results[0]
        
        required_fields = [
            'url', 'status', 'response_headers', 'title',
            'text_content', 'html_content', 'links',
            'internal_links', 'external_links', 'scraped_at',
            'user_agent', 'custom_data'
        ]
        
        for field in required_fields:
            assert field in item
    
    def test_yahoo_finance_special_handling(self, spider):
        """Test special handling for Yahoo Finance URLs"""
        request = Request(url="https://finance.yahoo.com/quote/AAPL")
        response = HtmlResponse(
            url="https://finance.yahoo.com/quote/AAPL",
            body=b"<html><title>AAPL</title><body>Stock data</body></html>",
            request=request
        )
        
        results = list(spider.parse(response))
        item = results[0]
        
        assert 'custom_data' in item
        # Yahoo Finance specific processing should be triggered


class TestSpiderConfiguration:
    """Test spider configuration and settings"""
    
    def test_format_parameter(self):
        """Test different format parameters"""
        spider_json = UniversalSpider(format='json')
        spider_html = UniversalSpider(format='html')
        
        assert spider_json.output_format == 'json'
        assert spider_html.output_format == 'html'
    
    def test_domain_extraction(self):
        """Test domain extraction from URLs"""
        test_urls = [
            "https://example.com/page",
            "http://subdomain.example.com",
            "https://example.org/path/to/page"
        ]
        
        for url in test_urls:
            spider = UniversalSpider(url=url)
            assert len(spider.allowed_domains) > 0
