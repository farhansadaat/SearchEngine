"""
Unit tests for the search engine.
"""
import pytest
import asyncio
from pathlib import Path
import tempfile
import json

from crawler.web_crawler import WebCrawler, PageContent
from indexer.indexer import Indexer, InvertedIndex
from ranking.ranker import Ranker, TFIDFRanker
from utils.text_processor import TextProcessor, HTMLProcessor, URLProcessor
from config import CrawlerConfig, IndexerConfig

class TestTextProcessor:
    """Test TextProcessor class."""
    
    def test_tokenize(self):
        """Test tokenization."""
        processor = TextProcessor(remove_stopwords=False)
        tokens = processor.tokenize("Hello World Python 123")
        assert "hello" in tokens
        assert "world" in tokens
        assert "python" in tokens
    
    def test_remove_stopwords(self):
        """Test stopword removal."""
        processor = TextProcessor(remove_stopwords=True)
        tokens = processor.tokenize("the quick brown fox")
        assert "the" not in tokens
        assert "quick" in tokens
        assert "brown" in tokens
        assert "fox" in tokens
    
    def test_clean_text(self):
        """Test text cleaning."""
        processor = TextProcessor()
        cleaned = processor.clean_text("hello    world   test")
        assert cleaned == "hello world test"

class TestHTMLProcessor:
    """Test HTMLProcessor class."""
    
    def test_extract_text(self):
        """Test text extraction."""
        html = "<html><body><p>Hello World</p></body></html>"
        text = HTMLProcessor.extract_text(html)
        assert "Hello World" in text
    
    def test_extract_title(self):
        """Test title extraction."""
        html = "<html><head><title>Test Page</title></head></html>"
        title = HTMLProcessor.extract_title(html)
        assert title == "Test Page"
    
    def test_extract_links(self):
        """Test link extraction."""
        html = '''<html><body>
            <a href="https://example.com/page1">Link 1</a>
            <a href="/page2">Link 2</a>
        </body></html>'''
        links = HTMLProcessor.extract_links(html, "https://example.com")
        assert "https://example.com/page1" in links
        assert "https://example.com/page2" in links

class TestURLProcessor:
    """Test URLProcessor class."""
    
    def test_is_valid_url(self):
        """Test URL validation."""
        assert URLProcessor.is_valid_url("https://example.com")
        assert URLProcessor.is_valid_url("http://example.com/path")
        assert not URLProcessor.is_valid_url("not a url")
    
    def test_normalize_url(self):
        """Test URL normalization."""
        url = "https://example.com/path/#fragment"
        normalized = URLProcessor.normalize_url(url)
        assert "#fragment" not in normalized
    
    def test_get_domain(self):
        """Test domain extraction."""
        domain = URLProcessor.get_domain("https://example.com/path")
        assert domain == "example.com"

class TestInvertedIndex:
    """Test InvertedIndex class."""
    
    def test_add_document(self):
        """Test adding documents."""
        index = InvertedIndex()
        index.add_document(1, {'url': 'https://example.com', 'title': 'Example'})
        assert index.document_count == 1
    
    def test_index_terms(self):
        """Test indexing terms."""
        index = InvertedIndex()
        index.add_document(1, {'url': 'https://example.com'})
        index.index_terms(1, ['hello', 'world', 'hello'])
        
        postings = index.get_postings('hello')
        assert len(postings) == 1
        assert postings[0][1] == 2  # frequency
    
    def test_json_persistence(self):
        """Test saving/loading from JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Create and save index
            index1 = InvertedIndex()
            index1.add_document(1, {'url': 'https://example.com'})
            index1.index_terms(1, ['test', 'data'])
            index1.save_to_json(temp_path)
            
            # Load index
            index2 = InvertedIndex()
            index2.load_from_json(temp_path)
            
            assert index2.document_count == 1
            assert len(index2.get_postings('test')) > 0
        finally:
            Path(temp_path).unlink()

class TestTFIDFRanker:
    """Test TFIDFRanker class."""
    
    def test_calculate_idf(self):
        """Test IDF calculation."""
        index = InvertedIndex()
        index.add_document(1, {'url': 'doc1'})
        index.add_document(2, {'url': 'doc2'})
        index.index_terms(1, ['hello', 'world'])
        index.index_terms(2, ['hello'])
        
        ranker = TFIDFRanker(index)
        idf_hello = ranker.calculate_idf('hello')
        idf_world = ranker.calculate_idf('world')
        
        # 'world' is less common, should have higher IDF
        assert idf_world > idf_hello
    
    def test_calculate_tf(self):
        """Test TF calculation."""
        index = InvertedIndex()
        index.add_document(1, {'url': 'doc1'})
        index.index_terms(1, ['hello', 'hello', 'world'])
        
        ranker = TFIDFRanker(index)
        tf = ranker.calculate_tf('hello', 1)
        
        assert tf == 2.0

class TestPageContent:
    """Test PageContent class."""
    
    def test_page_content_creation(self):
        """Test creating PageContent."""
        html = "<html><head><title>Test</title></head><body><p>Test content</p></body></html>"
        page = PageContent("https://example.com", html)
        
        assert page.url == "https://example.com"
        assert page.title == "Test"
        assert "Test content" in page.text

def run_tests():
    """Run all tests."""
    pytest.main([__file__, "-v"])

if __name__ == "__main__":
    run_tests()
