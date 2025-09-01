"""
Proxy management and rotation middleware for anti-scraping
"""
import random
import time
import requests
import logging
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware


logger = logging.getLogger(__name__)


class ProxyManager:
    """Manages proxy rotation and validation"""
    
    def __init__(self, proxy_list: List[str], validation_timeout: int = 10):
        self.proxy_list = proxy_list
        self.validation_timeout = validation_timeout
        self.working_proxies = []
        self.failed_proxies = set()
        self.proxy_stats = {}
        self.last_validation = 0
        self.validation_interval = 300  # 5 minutes
        
    def validate_proxy(self, proxy: str) -> bool:
        """Validate a single proxy"""
        try:
            proxy_dict = {
                'http': proxy,
                'https': proxy
            }
            
            # Test with a simple request
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxy_dict,
                timeout=self.validation_timeout
            )
            
            if response.status_code == 200:
                logger.debug(f"Proxy {proxy} is working")
                return True
            else:
                logger.warning(f"Proxy {proxy} returned status {response.status_code}")
                return False
                
        except Exception as e:
            logger.warning(f"Proxy {proxy} failed validation: {e}")
            return False
    
    def validate_all_proxies(self) -> None:
        """Validate all proxies and update working list"""
        logger.info("Validating proxy list...")
        self.working_proxies = []
        
        for proxy in self.proxy_list:
            if proxy not in self.failed_proxies:
                if self.validate_proxy(proxy):
                    self.working_proxies.append(proxy)
                    self.proxy_stats[proxy] = self.proxy_stats.get(proxy, {'success': 0, 'failed': 0})
                else:
                    self.failed_proxies.add(proxy)
        
        logger.info(f"Found {len(self.working_proxies)} working proxies out of {len(self.proxy_list)}")
        self.last_validation = time.time()
    
    def get_random_proxy(self) -> Optional[str]:
        """Get a random working proxy"""
        # Re-validate if needed
        if time.time() - self.last_validation > self.validation_interval:
            self.validate_all_proxies()
        
        if not self.working_proxies:
            logger.error("No working proxies available")
            return None
        
        return random.choice(self.working_proxies)
    
    def mark_proxy_failed(self, proxy: str) -> None:
        """Mark a proxy as failed"""
        if proxy in self.working_proxies:
            self.working_proxies.remove(proxy)
        self.failed_proxies.add(proxy)
        
        if proxy in self.proxy_stats:
            self.proxy_stats[proxy]['failed'] += 1
        
        logger.warning(f"Marked proxy {proxy} as failed")
    
    def mark_proxy_success(self, proxy: str) -> None:
        """Mark a proxy as successful"""
        if proxy in self.proxy_stats:
            self.proxy_stats[proxy]['success'] += 1


class ProxyRotationMiddleware:
    """Middleware for rotating proxies to avoid IP blocking"""
    
    def __init__(self, proxy_list: List[str], enabled: bool = True):
        self.enabled = enabled
        if not self.enabled:
            return
            
        if not proxy_list:
            logger.warning("No proxies provided, proxy rotation disabled")
            self.enabled = False
            return
        
        self.proxy_manager = ProxyManager(proxy_list)
        self.proxy_manager.validate_all_proxies()
        self.current_proxy = None
        
        logger.info(f"ProxyRotationMiddleware initialized with {len(proxy_list)} proxies")
    
    @classmethod
    def from_crawler(cls, crawler):
        """Create middleware instance from crawler settings"""
        enabled = crawler.settings.getbool('PROXY_ROTATION_ENABLED', False)
        proxy_list = crawler.settings.get('PROXY_LIST', [])
        
        if not enabled:
            logger.info("Proxy rotation is disabled")
            raise NotConfigured("Proxy rotation disabled")
        
        instance = cls(proxy_list=proxy_list, enabled=enabled)
        
        # Connect signals
        crawler.signals.connect(instance.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(instance.spider_closed, signal=signals.spider_closed)
        
        return instance
    
    def spider_opened(self, spider):
        """Called when spider is opened"""
        logger.info(f"Proxy rotation enabled for spider {spider.name}")
    
    def spider_closed(self, spider):
        """Called when spider is closed"""
        if self.enabled and self.proxy_manager:
            logger.info("Proxy rotation statistics:")
            for proxy, stats in self.proxy_manager.proxy_stats.items():
                success_rate = stats['success'] / (stats['success'] + stats['failed']) * 100
                logger.info(f"  {proxy}: {success_rate:.1f}% success rate")
    
    def process_request(self, request, spider):
        """Process request and assign proxy"""
        if not self.enabled:
            return None
        
        # Get a random proxy
        proxy = self.proxy_manager.get_random_proxy()
        if proxy:
            request.meta['proxy'] = proxy
            self.current_proxy = proxy
            logger.debug(f"Using proxy: {proxy}")
        else:
            logger.warning("No proxies available, proceeding without proxy")
        
        return None
    
    def process_response(self, request, response, spider):
        """Process response and handle proxy issues"""
        if not self.enabled:
            return response
        
        proxy = request.meta.get('proxy')
        
        # Handle successful responses
        if response.status == 200:
            if proxy:
                self.proxy_manager.mark_proxy_success(proxy)
            return response
        
        # Handle proxy-related errors
        if response.status in [403, 407, 429]:
            if proxy:
                logger.warning(f"Proxy {proxy} blocked (status {response.status})")
                self.proxy_manager.mark_proxy_failed(proxy)
                
                # Retry with a different proxy
                new_proxy = self.proxy_manager.get_random_proxy()
                if new_proxy and new_proxy != proxy:
                    request.meta['proxy'] = new_proxy
                    logger.info(f"Retrying with different proxy: {new_proxy}")
                    return request
        
        return response
    
    def process_exception(self, request, exception, spider):
        """Process exceptions and handle proxy failures"""
        if not self.enabled:
            return None
        
        proxy = request.meta.get('proxy')
        
        # Handle connection errors that might be proxy-related
        if proxy and any(error in str(exception).lower() for error in 
                        ['connection', 'timeout', 'refused', 'unreachable']):
            logger.warning(f"Proxy {proxy} connection failed: {exception}")
            self.proxy_manager.mark_proxy_failed(proxy)
            
            # Retry with a different proxy
            new_proxy = self.proxy_manager.get_random_proxy()
            if new_proxy and new_proxy != proxy:
                request.meta['proxy'] = new_proxy
                logger.info(f"Retrying with different proxy after exception: {new_proxy}")
                return request
        
        return None


class FreeProxyProvider:
    """Provider for free proxy lists (use with caution)"""
    
    @staticmethod
    def get_free_proxies() -> List[str]:
        """Get a list of free proxies (educational purposes only)"""
        # WARNING: Free proxies are often unreliable and potentially unsafe
        # This is for educational/testing purposes only
        
        free_proxy_sources = [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        ]
        
        proxies = []
        
        for source in free_proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    proxy_list = response.text.strip().split('\n')
                    for proxy in proxy_list:
                        proxy = proxy.strip()
                        if proxy and ':' in proxy:
                            proxies.append(f"http://{proxy}")
            except Exception as e:
                logger.warning(f"Failed to fetch proxies from {source}: {e}")
        
        logger.info(f"Retrieved {len(proxies)} free proxies")
        return proxies[:50]  # Limit to first 50


# Configuration for different proxy services
PROXY_SERVICES = {
    'free': {
        'provider': FreeProxyProvider,
        'cost': 0,
        'reliability': 'low',
        'speed': 'slow'
    },
    # Add other proxy service configurations here
    # 'premium': {
    #     'provider': PremiumProxyProvider,
    #     'cost': 'paid',
    #     'reliability': 'high',
    #     'speed': 'fast'
    # }
}
