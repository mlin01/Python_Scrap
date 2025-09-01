"""
Enhanced error handling and logging utilities for the universal scraper
"""
import logging
import traceback
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum


class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ScrapingError(Exception):
    """Base exception for scraping errors"""
    def __init__(self, message: str, url: Optional[str] = None, status_code: Optional[int] = None):
        self.message = message
        self.url = url
        self.status_code = status_code
        self.timestamp = datetime.now()
        super().__init__(self.message)


class AntiScrapingDetected(ScrapingError):
    """Raised when anti-scraping measures are detected"""
    pass


class CaptchaDetected(ScrapingError):
    """Raised when CAPTCHA is detected"""
    pass


class RateLimitExceeded(ScrapingError):
    """Raised when rate limit is exceeded"""
    pass


class JavaScriptRequired(ScrapingError):
    """Raised when JavaScript execution is required"""
    pass


class ScraperLogger:
    """Enhanced logger for the scraper with structured logging"""
    
    def __init__(self, name: str = "universal_scraper", log_dir: Optional[Path] = None):
        self.name = name
        self.log_dir = log_dir or Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Setup handlers
        self._setup_console_handler()
        self._setup_file_handler()
        self._setup_error_file_handler()
    
    def _setup_console_handler(self):
        """Setup console logging handler"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """Setup file logging handler"""
        log_file = self.log_dir / f"{self.name}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def _setup_error_file_handler(self):
        """Setup error-only file handler"""
        error_file = self.log_dir / f"{self.name}_errors.log"
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d\n'
            'URL: %(url)s\nError: %(message)s\nTraceback:\n%(traceback)s\n'
            + '-' * 80,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        error_handler.setFormatter(error_formatter)
        self.logger.addHandler(error_handler)
    
    def log_scraping_start(self, url: str, spider_name: str):
        """Log scraping start"""
        self.logger.info(f"Starting scraping: {url} with spider: {spider_name}")
    
    def log_scraping_success(self, url: str, items_count: int, duration: float):
        """Log successful scraping"""
        self.logger.info(f"Successfully scraped {url}: {items_count} items in {duration:.2f}s")
    
    def log_scraping_error(self, error: ScrapingError, url: Optional[str] = None):
        """Log scraping error with context"""
        extra_data = {
            'url': url or error.url or 'Unknown',
            'traceback': traceback.format_exc()
        }
        self.logger.error(error.message, extra=extra_data)
    
    def log_anti_scraping_detected(self, url: str, detection_type: str, details: Dict[str, Any]):
        """Log anti-scraping detection"""
        self.logger.warning(
            f"Anti-scraping detected on {url}: {detection_type}. Details: {details}"
        )
    
    def log_retry_attempt(self, url: str, attempt: int, max_attempts: int, reason: str):
        """Log retry attempt"""
        self.logger.info(f"Retry {attempt}/{max_attempts} for {url}: {reason}")
    
    def log_proxy_rotation(self, old_proxy: Optional[str], new_proxy: str):
        """Log proxy rotation"""
        self.logger.debug(f"Proxy rotated: {old_proxy} -> {new_proxy}")
    
    def log_user_agent_rotation(self, user_agent: str):
        """Log user agent rotation"""
        self.logger.debug(f"User agent set: {user_agent[:50]}...")
    
    def log_performance_metrics(self, metrics: Dict[str, Any]):
        """Log performance metrics"""
        self.logger.info(f"Performance metrics: {metrics}")


class ErrorHandler:
    """Error handling utilities for the scraper"""
    
    def __init__(self, logger: ScraperLogger):
        self.logger = logger
        self.error_counts = {}
        self.max_errors_per_domain = 10
    
    def handle_http_error(self, response, spider) -> bool:
        """
        Handle HTTP errors and determine if scraping should continue
        
        Returns:
            bool: True if scraping should continue, False otherwise
        """
        status_code = response.status
        url = response.url
        
        if status_code == 403:
            error = AntiScrapingDetected(
                f"Access forbidden (403) - possible anti-scraping",
                url=url,
                status_code=status_code
            )
            self.logger.log_scraping_error(error)
            return False
            
        elif status_code == 429:
            error = RateLimitExceeded(
                f"Rate limit exceeded (429)",
                url=url,
                status_code=status_code
            )
            self.logger.log_scraping_error(error)
            return False
            
        elif status_code >= 500:
            error = ScrapingError(
                f"Server error ({status_code})",
                url=url,
                status_code=status_code
            )
            self.logger.log_scraping_error(error)
            return True  # Server errors might be temporary
            
        elif status_code == 404:
            self.logger.logger.warning(f"Page not found (404): {url}")
            return False
            
        else:
            self.logger.logger.warning(f"Unexpected status code {status_code}: {url}")
            return True
    
    def detect_captcha(self, response) -> bool:
        """Detect if response contains CAPTCHA"""
        captcha_indicators = [
            'captcha', 'recaptcha', 'hcaptcha',
            'verify you are human', 'robot check',
            'security check', 'prove you are not a robot'
        ]
        
        response_text = response.text.lower()
        for indicator in captcha_indicators:
            if indicator in response_text:
                error = CaptchaDetected(
                    f"CAPTCHA detected: {indicator}",
                    url=response.url
                )
                self.logger.log_scraping_error(error)
                return True
        
        return False
    
    def should_retry(self, failure, spider) -> bool:
        """Determine if a failed request should be retried"""
        domain = failure.request.url.split('/')[2]
        
        # Track error counts per domain
        if domain not in self.error_counts:
            self.error_counts[domain] = 0
        
        self.error_counts[domain] += 1
        
        # Stop retrying if too many errors for this domain
        if self.error_counts[domain] > self.max_errors_per_domain:
            self.logger.logger.error(
                f"Too many errors for domain {domain}, stopping retries"
            )
            return False
        
        # Retry on connection errors
        if hasattr(failure.value, 'errno'):
            return True
        
        # Retry on timeout errors
        if 'timeout' in str(failure.value).lower():
            return True
        
        return False


# Global logger instance
scraper_logger = ScraperLogger()
error_handler = ErrorHandler(scraper_logger)
