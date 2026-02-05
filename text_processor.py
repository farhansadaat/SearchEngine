"""
Utility functions for text processing and HTML handling.
"""
import re
from typing import List, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

class TextProcessor:
    """Handles text processing tasks."""
    
    def __init__(self, remove_stopwords: bool = True, language: str = "english"):
        """
        Initialize text processor.
        
        Args:
            remove_stopwords: Whether to remove stopwords
            language: Language for stopwords
        """
        self.remove_stopwords = remove_stopwords
        self.language = language
        self.stopwords_set: Set[str] = set()
        
        if self.remove_stopwords:
            try:
                self.stopwords_set = set(stopwords.words(language))
            except Exception:
                pass
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Text to tokenize
        
        Returns:
            List of tokens
        """
        text = text.lower()
        tokens = word_tokenize(text)
        
        # Filter out non-alphanumeric tokens
        tokens = [t for t in tokens if re.match(r'^[a-z0-9]+$', t)]
        
        # Remove stopwords if enabled
        if self.remove_stopwords:
            tokens = [t for t in tokens if t not in self.stopwords_set]
        
        return tokens
    
    def clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace.
        
        Args:
            text: Text to clean
        
        Returns:
            Cleaned text
        """
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

class HTMLProcessor:
    """Handles HTML parsing and content extraction."""
    
    @staticmethod
    def extract_text(html: str) -> str:
        """
        Extract plain text from HTML.
        
        Args:
            html: HTML content
        
        Returns:
            Extracted text
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            return text
        except Exception:
            return ""
    
    @staticmethod
    def extract_title(html: str) -> str:
        """
        Extract title from HTML.
        
        Args:
            html: HTML content
        
        Returns:
            Page title
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.find('title')
            if title:
                return title.get_text().strip()
        except Exception:
            pass
        return ""
    
    @staticmethod
    def extract_headings(html: str) -> List[str]:
        """
        Extract all headings from HTML.
        
        Args:
            html: HTML content
        
        Returns:
            List of headings
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            headings = []
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                text = heading.get_text().strip()
                if text:
                    headings.append(text)
            return headings
        except Exception:
            return []
    
    @staticmethod
    def extract_description(html: str) -> str:
        """
        Extract meta description from HTML.
        
        Args:
            html: HTML content
        
        Returns:
            Meta description
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            meta = soup.find('meta', attrs={'name': 'description'})
            if meta and meta.get('content'):
                return meta['content']
        except Exception:
            pass
        return ""
    
    @staticmethod
    def extract_links(html: str, base_url: str) -> List[str]:
        """
        Extract all links from HTML.
        
        Args:
            html: HTML content
            base_url: Base URL for resolving relative links
        
        Returns:
            List of absolute URLs
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Resolve relative URLs
                absolute_url = urljoin(base_url, href)
                # Remove fragments and query parameters
                absolute_url = absolute_url.split('#')[0]
                
                if absolute_url and absolute_url.startswith('http'):
                    links.append(absolute_url)
            
            return list(set(links))  # Remove duplicates
        except Exception:
            return []

class URLProcessor:
    """Handles URL processing and validation."""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Validate if string is a valid URL.
        
        Args:
            url: URL to validate
        
        Returns:
            True if valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Normalize URL for comparison.
        
        Args:
            url: URL to normalize
        
        Returns:
            Normalized URL
        """
        url = url.strip()
        # Remove trailing slashes
        if url.endswith('/') and url.count('/') > 3:
            url = url.rstrip('/')
        # Remove fragment
        url = url.split('#')[0]
        return url
    
    @staticmethod
    def get_domain(url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: URL
        
        Returns:
            Domain
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return ""
    
    @staticmethod
    def should_follow_link(current_url: str, link_url: str, follow_external: bool = False) -> bool:
        """
        Determine if a link should be followed.
        
        Args:
            current_url: Current page URL
            link_url: Link URL to check
            follow_external: Whether to follow external links
        
        Returns:
            True if link should be followed
        """
        if not URLProcessor.is_valid_url(link_url):
            return False
        
        current_domain = URLProcessor.get_domain(current_url)
        link_domain = URLProcessor.get_domain(link_url)
        
        if not follow_external and current_domain != link_domain:
            return False
        
        # Skip certain file types
        skip_extensions = {'.pdf', '.zip', '.exe', '.jpg', '.png', '.gif', '.mp4'}
        for ext in skip_extensions:
            if link_url.lower().endswith(ext):
                return False
        
        return True
