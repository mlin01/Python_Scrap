# Configuration for Universal Web Scraper
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseSettings, Field


class ScraperConfig(BaseSettings):
    """Configuration management for the universal scraper"""
    
    # Basic settings
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    output_dir: Path = Field(default=Path("output"), env="OUTPUT_DIR")
    
    # Scraping settings
    request_delay: float = Field(default=2.0, env="REQUEST_DELAY")
    concurrent_requests: int = Field(default=1, env="CONCURRENT_REQUESTS")
    download_timeout: int = Field(default=180, env="DOWNLOAD_TIMEOUT")
    retry_times: int = Field(default=3, env="RETRY_TIMES")
    
    # User agent settings
    user_agent_rotation: bool = Field(default=True, env="USER_AGENT_ROTATION")
    custom_user_agents: Optional[List[str]] = Field(default=None, env="CUSTOM_USER_AGENTS")
    
    # Proxy settings
    proxy_enabled: bool = Field(default=False, env="PROXY_ENABLED")
    proxy_list: Optional[List[str]] = Field(default=None, env="PROXY_LIST")
    proxy_rotation: bool = Field(default=True, env="PROXY_ROTATION")
    
    # Selenium settings
    selenium_headless: bool = Field(default=True, env="SELENIUM_HEADLESS")
    selenium_timeout: int = Field(default=30, env="SELENIUM_TIMEOUT")
    selenium_implicit_wait: int = Field(default=10, env="SELENIUM_IMPLICIT_WAIT")
    chrome_options: List[str] = Field(
        default=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-images",
            "--disable-javascript"
        ],
        env="CHROME_OPTIONS"
    )
    
    # Anti-detection settings
    captcha_solver_enabled: bool = Field(default=False, env="CAPTCHA_SOLVER_ENABLED")
    captcha_service_api_key: Optional[str] = Field(default=None, env="CAPTCHA_API_KEY")
    respect_robots_txt: bool = Field(default=True, env="RESPECT_ROBOTS_TXT")
    
    # Output settings
    export_formats: List[str] = Field(default=["json"], env="EXPORT_FORMATS")
    include_html: bool = Field(default=False, env="INCLUDE_HTML")
    compress_output: bool = Field(default=False, env="COMPRESS_OUTPUT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global config instance
config = ScraperConfig()


def get_config() -> ScraperConfig:
    """Get the global configuration instance"""
    return config


def update_config(**kwargs) -> None:
    """Update configuration values"""
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)


def load_config_from_file(config_path: str) -> ScraperConfig:
    """Load configuration from a specific file"""
    return ScraperConfig(_env_file=config_path)
