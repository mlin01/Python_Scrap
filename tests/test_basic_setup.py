"""
Basic tests for the scraper project setup and configuration
"""
import pytest
import sys
from pathlib import Path


def test_project_structure():
    """Test that the project has the expected structure"""
    project_root = Path(__file__).parent.parent
    
    # Check main directories exist
    assert (project_root / "universal_scraper").exists()
    assert (project_root / "tests").exists()
    assert (project_root / "config").exists()
    assert (project_root / "utils").exists()
    assert (project_root / "docs").exists()


def test_requirements_file():
    """Test that requirements.txt exists and has content"""
    project_root = Path(__file__).parent.parent
    requirements_file = project_root / "requirements.txt"
    
    assert requirements_file.exists()
    
    content = requirements_file.read_text()
    assert "scrapy" in content.lower()
    assert "selenium" in content.lower()
    assert "beautifulsoup4" in content.lower()


def test_scrapy_project_structure():
    """Test that the Scrapy project has the correct structure"""
    scrapy_dir = Path(__file__).parent.parent / "universal_scraper"
    
    assert (scrapy_dir / "scrapy.cfg").exists()
    assert (scrapy_dir / "universal_scraper").exists()
    assert (scrapy_dir / "universal_scraper" / "spiders").exists()
    assert (scrapy_dir / "universal_scraper" / "settings.py").exists()
    assert (scrapy_dir / "universal_scraper" / "items.py").exists()
    assert (scrapy_dir / "universal_scraper" / "pipelines.py").exists()


def test_spider_files_exist():
    """Test that spider files exist"""
    spiders_dir = Path(__file__).parent.parent / "universal_scraper" / "universal_scraper" / "spiders"
    
    assert (spiders_dir / "universal.py").exists()
    assert (spiders_dir / "selenium_spider.py").exists()


def test_config_files_exist():
    """Test that configuration files exist"""
    project_root = Path(__file__).parent.parent
    
    assert (project_root / ".env.example").exists()
    assert (project_root / "config" / "scraper_config.py").exists()


def test_utility_files_exist():
    """Test that utility files exist"""
    utils_dir = Path(__file__).parent.parent / "utils"
    
    assert (utils_dir / "error_handling.py").exists()
    assert (utils_dir / "proxy_management.py").exists()


def test_documentation_exists():
    """Test that documentation files exist"""
    docs_dir = Path(__file__).parent.parent / "docs"
    
    assert (docs_dir / "ADVANCED_USAGE.md").exists()


def test_python_version():
    """Test that Python version is suitable"""
    assert sys.version_info >= (3, 8), "Python 3.8+ is required"


class TestPackageImports:
    """Test that required packages can be imported"""
    
    def test_scrapy_import(self):
        """Test that Scrapy can be imported"""
        try:
            import scrapy
            assert scrapy.__version__ is not None
        except ImportError:
            pytest.fail("Scrapy is not installed or not importable")
    
    def test_selenium_import(self):
        """Test that Selenium can be imported"""
        try:
            import selenium
            assert selenium.__version__ is not None
        except ImportError:
            pytest.fail("Selenium is not installed or not importable")
    
    def test_beautifulsoup_import(self):
        """Test that BeautifulSoup can be imported"""
        try:
            import bs4
            assert bs4.__version__ is not None
        except ImportError:
            pytest.fail("BeautifulSoup4 is not installed or not importable")
    
    def test_requests_import(self):
        """Test that Requests can be imported"""
        try:
            import requests
            assert requests.__version__ is not None
        except ImportError:
            pytest.fail("Requests is not installed or not importable")


class TestScraperConfiguration:
    """Test scraper configuration"""
    
    def test_scrapy_settings_file(self):
        """Test that Scrapy settings file is properly configured"""
        settings_file = Path(__file__).parent.parent / "universal_scraper" / "universal_scraper" / "settings.py"
        
        assert settings_file.exists()
        
        content = settings_file.read_text()
        assert "BOT_NAME" in content
        assert "SPIDER_MODULES" in content
        assert "USER_AGENT" in content
    
    def test_env_example_has_required_settings(self):
        """Test that .env.example has all required settings"""
        env_file = Path(__file__).parent.parent / ".env.example"
        
        assert env_file.exists()
        
        content = env_file.read_text()
        required_settings = [
            "DEBUG_MODE",
            "LOG_LEVEL", 
            "REQUEST_DELAY",
            "USER_AGENT_ROTATION",
            "PROXY_ENABLED"
        ]
        
        for setting in required_settings:
            assert setting in content, f"Missing required setting: {setting}"
