"""
Web crawler module for discovering and fetching web pages.
"""
import asyncio
import aiohttp
import time
from typing import Set, List, Optional, Dict
from urllib.parse import urlparse
from datetime import datetime, timedelta
import logging

from utils.text_processor import HTMLProcessor, URLProcessor
from config import config

logger = logging.getLogger(__name__)

class RobotsTxtParser:
    """Simple parser for robots.txt."""
    
    def __init__(self):
        self.cache: Dict[str, List[str]] = {}
        self.cache_expiry: Dict[str, datetime] = {}
    
    async def can_fetch(self, url: str, user_agent: str, session: aiohttp.ClientSession) -> bool:
        """
        Check if URL can be fetched according to robots.txt.
        
        Args:
            url: URL to check
            user_agent: User agent string
            session: aiohttp session
        
        Returns:
            True if URL can be fetched
        """
        try:
            parsed = urlparse(url)
            domain = f"{parsed.scheme}://{parsed.netloc}"
            
            # Check cache
            if domain in self.cache:
                if datetime.now() < self.cache_expiry.get(domain, datetime.min):
                    disallowed = self.cache[domain]
                    return not any(url.startswith(f"{domain}{path}") for path in disallowed)
            
            # Fetch robots.txt
            robots_url = f"{domain}/robots.txt"
            try:
                async with session.get(robots_url, timeout=5) as resp:
                    if resp.status == 200:
                        content = await resp.text()
                        disallowed = self._parse_robots_txt(content, user_agent)
                        self.cache[domain] = disallowed
                        self.cache_expiry[domain] = datetime.now() + timedelta(hours=24)
                        return not any(url.startswith(f"{domain}{path}") for path in disallowed)
            except Exception as e:
                logger.debug(f"Could not fetch robots.txt for {domain}: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Error checking robots.txt: {e}")
            return True
    
    def _parse_robots_txt(self, content: str, user_agent: str) -> List[str]:
        """Parse robots.txt file."""
        disallowed = []
        current_agent = None
        
        for line in content.split('\n'):
            line = line.split('#')[0].strip()
            if not line:
                continue
            
            if line.lower().startswith('user-agent:'):
                current_agent = line.split(':', 1)[1].strip()
            elif line.lower().startswith('disallow:') and (current_agent == '*' or current_agent == user_agent):
                path = line.split(':', 1)[1].strip()
                if path:
                    disallowed.append(path)
        
        return disallowed

class PageContent:
    """Represents a crawled page."""
    
    def __init__(self, url: str, html: str, status_code: int = 200):
        """
        Initialize page content.
        
        Args:
            url: Page URL
            html: HTML content
            status_code: HTTP status code
        """
        self.url = url
        self.html = html
        self.status_code = status_code
        self.title = HTMLProcessor.extract_title(html)
        self.text = HTMLProcessor.extract_text(html)
        self.headings = HTMLProcessor.extract_headings(html)
        self.description = HTMLProcessor.extract_description(html)
        self.links = HTMLProcessor.extract_links(html, url)
        self.crawl_time = datetime.now()

class WebCrawler:
    """Asynchronous web crawler."""
    
    def __init__(self, config_obj=None):
        """
        Initialize web crawler.
        
        Args:
            config_obj: Configuration object
        """
        self.config = config_obj or config.crawler
        self.visited_urls: Set[str] = set()
        self.to_visit: List[str] = list(self.config.seed_urls)
        self.crawled_pages: List[PageContent] = []
        self.robots_parser = RobotsTxtParser()
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def fetch_page(self, url: str, attempt: int = 0) -> Optional[PageContent]:
        """
        Fetch a single page with retry logic.
        
        Args:
            url: URL to fetch
            attempt: Current attempt number
        
        Returns:
            PageContent if successful, None otherwise
        """
        if not self.session:
            return None
        
        try:
            headers = {'User-Agent': self.config.user_agent}
            
            async with self.session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                headers=headers,
                ssl=False
            ) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    logger.info(f"Fetched {url}")
                    return PageContent(url, html, resp.status)
                else:
                    logger.warning(f"Failed to fetch {url}: status {resp.status}")
                    return None
        
        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching {url}")
            if attempt < self.config.retry_attempts:
                await asyncio.sleep(self.config.retry_backoff ** attempt)
                return await self.fetch_page(url, attempt + 1)
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            if attempt < self.config.retry_attempts:
                await asyncio.sleep(self.config.retry_backoff ** attempt)
                return await self.fetch_page(url, attempt + 1)
        
        return None
    
    async def crawl_worker(self):
        """Worker coroutine for crawling."""
        while self.to_visit and len(self.crawled_pages) < self.config.max_pages:
            url = self.to_visit.pop(0)
            
            # Normalize and check if already visited
            url = URLProcessor.normalize_url(url)
            if url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            
            # Check robots.txt
            if self.config.respect_robots_txt:
                if not await self.robots_parser.can_fetch(url, self.config.user_agent, self.session):
                    logger.info(f"Skipped {url} (robots.txt)")
                    continue
            
            # Fetch page
            page = await self.fetch_page(url)
            if page:
                self.crawled_pages.append(page)
                
                # Extract links and add to queue
                for link in page.links:
                    link = URLProcessor.normalize_url(link)
                    if link not in self.visited_urls and URLProcessor.should_follow_link(
                        url, link, self.config.follow_external_links
                    ):
                        self.to_visit.append(link)
            
            # Small delay to be respectful
            await asyncio.sleep(0.5)
    
    async def crawl(self) -> List[PageContent]:
        """
        Start the crawling process.
        
        Returns:
            List of crawled pages
        """
        connector = aiohttp.TCPConnector(limit=self.config.max_workers)
        timeout = aiohttp.ClientTimeout(total=None, connect=10, sock_read=10)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            self.session = session
            
            # Create worker tasks
            workers = [
                self.crawl_worker() 
                for _ in range(self.config.max_workers)
            ]
            
            try:
                await asyncio.gather(*workers)
            except Exception as e:
                logger.error(f"Error during crawling: {e}")
            
            self.session = None
        
        logger.info(f"Crawling completed. Total pages: {len(self.crawled_pages)}")
        return self.crawled_pages
