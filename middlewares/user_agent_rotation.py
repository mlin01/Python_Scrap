"""
User-Agent Rotation Middleware for Anti-Scraping

This middleware rotates user agents to avoid detection by websites
that block requests based on user agent patterns.
"""

import random
import logging
from scrapy.exceptions import NotConfigured

logger = logging.getLogger(__name__)


class UserAgentRotationMiddleware:
    """
    Middleware for rotating user agents to avoid anti-scraping detection.

    Features:
    - Large pool of realistic user agents
    - Random rotation for each request
    - Browser fingerprinting avoidance
    - Configurable user agent lists
    """

    def __init__(self, user_agents=None, enabled=True):
        """
        Initialize the user agent rotation middleware.

        Args:
            user_agents (list): List of user agents to rotate through
            enabled (bool): Whether to enable user agent rotation
        """
        self.enabled = enabled
        if not self.enabled:
            return

        # Default comprehensive list of user agents
        self.user_agents = user_agents or [
            # Chrome Desktop
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',

            # Firefox Desktop
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:119.0) Gecko/20100101 Firefox/119.0',

            # Safari Desktop
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',

            # Edge Desktop
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',

            # Chrome Mobile
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.0.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',

            # Safari Mobile
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',

            # Other browsers
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]

        logger.info(f"UserAgentRotationMiddleware initialized with {len(self.user_agents)} user agents")

    @classmethod
    def from_crawler(cls, crawler):
        """
        Create middleware instance from crawler settings.

        Args:
            crawler: Scrapy crawler instance

        Returns:
            UserAgentRotationMiddleware: Configured middleware instance
        """
        enabled = crawler.settings.getbool('USER_AGENT_ROTATION_ENABLED', True)
        user_agents = crawler.settings.get('USER_AGENTS_LIST')

        if not enabled:
            logger.info("User agent rotation is disabled")
            return cls(enabled=False)

        return cls(user_agents=user_agents, enabled=enabled)

    def process_request(self, request, spider):
        """
        Process each request and set a random user agent.

        Args:
            request: Scrapy request object
            spider: Spider instance
        """
        if not self.enabled:
            return

        # Select random user agent
        user_agent = random.choice(self.user_agents)

        # Set the user agent in request headers
        request.headers['User-Agent'] = user_agent

        # Log the selected user agent (only in debug mode to avoid spam)
        logger.debug(f"Using User-Agent: {user_agent}")

        return None
