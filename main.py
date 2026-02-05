"""
Command-line interface for the search engine.
"""
import asyncio
import logging
from typing import List

from crawler.web_crawler import WebCrawler
from indexer.indexer import Indexer
from utils.text_processor import TextProcessor
from ranking.ranker import Ranker
from ranking.snippets import SnippetGenerator
from utils.logger import setup_logging
from config import config

# Setup logging
logger = setup_logging("search_engine")

class SearchEngineUI:
    """Command-line interface for the search engine."""
    
    def __init__(self):
        """Initialize CLI."""
        self.text_processor = TextProcessor()
        self.snippet_generator = SnippetGenerator()
        self.indexer = None
        self.ranker = None
    
    def run(self):
        """Run the CLI."""
        print("\n" + "="*60)
        print("Welcome to the Search Engine")
        print("="*60 + "\n")
        
        while True:
            print("\nOptions:")
            print("1. Crawl and index websites")
            print("2. Search documents")
            print("3. Load existing index")
            print("4. Exit")
            
            choice = input("\nSelect an option (1-4): ").strip()
            
            if choice == "1":
                self._crawl_and_index()
            elif choice == "2":
                self._search()
            elif choice == "3":
                self._load_index()
            elif choice == "4":
                print("\nGoodbye!")
                break
            else:
                print("Invalid option. Please try again.")
    
    def _crawl_and_index(self):
        """Crawl and index websites."""
        print("\n" + "-"*60)
        print("Crawling and Indexing")
        print("-"*60)
        
        # Initialize crawler
        crawler = WebCrawler(config.crawler)
        print(f"Starting crawl from: {config.crawler.seed_urls}")
        print(f"Max pages: {config.crawler.max_pages}")
        print(f"Max workers: {config.crawler.max_workers}")
        
        # Run crawler
        print("\nCrawling websites...")
        pages = asyncio.run(crawler.crawl())
        
        print(f"Crawled {len(pages)} pages")
        
        if not pages:
            print("No pages were crawled. Exiting.")
            return
        
        # Initialize indexer
        self.indexer = Indexer(config.indexer)
        print("\nIndexing pages...")
        self.indexer.index_pages(pages)
        
        # Save index
        self.indexer.save_index()
        print("Index saved to disk")
        
        # Initialize ranker
        self.ranker = Ranker(self.indexer.inverted_index, config.ranking)
        print("Ready to search!")
    
    def _search(self):
        """Search documents."""
        if not self.indexer or not self.ranker:
            print("\nNo index loaded. Please crawl and index first, or load existing index.")
            return
        
        print("\n" + "-"*60)
        print("Search")
        print("-"*60)
        print("(Type 'back' to return to main menu)")
        
        while True:
            query = input("\nEnter search query: ").strip()
            
            if query.lower() == 'back':
                break
            
            if not query:
                print("Please enter a query.")
                continue
            
            # Process query
            query_terms = self.text_processor.tokenize(query)
            
            if not query_terms:
                print("No valid search terms found.")
                continue
            
            # Search
            results = self.ranker.search(query_terms, max_results=20)
            
            # Display results
            self._display_results(query, query_terms, results)
    
    def _load_index(self):
        """Load existing index."""
        print("\n" + "-"*60)
        print("Loading Index")
        print("-"*60)
        
        try:
            self.indexer = Indexer(config.indexer)
            self.indexer.load_index()
            self.ranker = Ranker(self.indexer.inverted_index, config.ranking)
            
            print(f"Index loaded successfully")
            print(f"Documents: {self.indexer.inverted_index.document_count}")
            print(f"Terms: {len(self.indexer.inverted_index.index)}")
            print("Ready to search!")
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            print(f"Error loading index: {e}")
    
    def _display_results(self, query: str, query_terms: List[str], results: list):
        """Display search results."""
        print(f"\n{'='*60}")
        print(f"Results for: '{query}'")
        print(f"Found: {len(results)} results")
        print(f"{'='*60}\n")
        
        if not results:
            print("No results found.")
            return
        
        for i, result in enumerate(results, 1):
            doc = self.indexer.db.get_document(result['doc_id'])
            
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Score: {result['score']:.4f}")
            
            if doc:
                snippet = self.snippet_generator.generate_snippet(
                    doc.get('text', ''),
                    query_terms
                )
                print(f"   Snippet: {snippet}")
            
            print()

def main():
    """Main entry point."""
    ui = SearchEngineUI()
    ui.run()

if __name__ == "__main__":
    main()
