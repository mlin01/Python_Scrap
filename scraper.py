#!/usr/bin/env python3
"""
Universal Web Scraper
Supports two output methods: JSON and HTML
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def scrape_json(url):
    """Scrape URL and return JSON data"""
    print(f"Scraping {url} for JSON output...")

    # Change to the scrapy project directory
    project_dir = os.path.join(os.path.dirname(__file__), 'universal_scraper')

    # Run scrapy with JSON format
    cmd = [
        "scrapy", "crawl", "universal",
        "-a", f"url={url}",
        "-a", "format=json",
        "-s", "ROBOTSTXT_OBEY=False"
    ]

    try:
        result = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True)
        print("Scraping completed.")
        return result.stdout, result.stderr
    except Exception as e:
        return None, str(e)

def scrape_html(url):
    """Scrape URL and return HTML content"""
    print(f"Scraping {url} for HTML output...")

    # Change to the scrapy project directory
    project_dir = os.path.join(os.path.dirname(__file__), 'universal_scraper')

    # Run scrapy with HTML format
    cmd = [
        "scrapy", "crawl", "universal",
        "-a", f"url={url}",
        "-a", "format=html",
        "-s", "ROBOTSTXT_OBEY=False"
    ]

    try:
        result = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True)
        print("Scraping completed.")
        return result.stdout, result.stderr
    except Exception as e:
        return None, str(e)

def main():
    if len(sys.argv) < 3:
        print("Usage: python scraper.py <format> <url>")
        print("Formats: json, html")
        print("Example: python scraper.py json https://example.com")
        sys.exit(1)

    format_type = sys.argv[1].lower()
    url = sys.argv[2]

    if format_type not in ['json', 'html']:
        print("Error: Format must be 'json' or 'html'")
        sys.exit(1)

    if format_type == 'json':
        stdout, stderr = scrape_json(url)
    else:
        stdout, stderr = scrape_html(url)

    if stderr:
        print(f"Errors: {stderr}")

    if stdout:
        print(stdout)

if __name__ == "__main__":
    main()
