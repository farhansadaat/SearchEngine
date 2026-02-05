#!/usr/bin/env python3
"""
Quick start script for the search engine.
This script sets up and demonstrates the search engine.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from crawler.web_crawler import WebCrawler
from indexer.indexer import Indexer
from ranking.ranker import Ranker
from utils.text_processor import TextProcessor
from utils.logger import setup_logging
from config import config

logger = setup_logging("quickstart")

def main():
    """Run quick start demo."""
    print("\n" + "="*70)
    print("SEARCH ENGINE - QUICK START DEMO")
    print("="*70 + "\n")
    
    # Step 1: Crawl
    print("STEP 1: CRAWLING")
    print("-" * 70)
    print(f"Starting crawl from: {config.crawler.seed_urls}")
    print(f"Max pages: {config.crawler.max_pages}")
    print(f"Max workers: {config.crawler.max_workers}\n")
    
    crawler = WebCrawler(config.crawler)
    pages = asyncio.run(crawler.crawl())
    
    print(f"\n✓ Crawled {len(pages)} pages\n")
    
    if not pages:
        print("No pages were crawled. Please check seed URLs and network.")
        return
    
    # Step 2: Index
    print("STEP 2: INDEXING")
    print("-" * 70)
    indexer = Indexer(config.indexer)
    indexed_count = indexer.index_pages(pages)
    indexer.save_index()
    
    print(f"\n✓ Indexed {indexed_count} pages")
    print(f"✓ Index saved to {config.get_full_index_path()}\n")
    
    # Step 3: Search
    print("STEP 3: SEARCHING")
    print("-" * 70)
    
    text_processor = TextProcessor()
    ranker = Ranker(indexer.inverted_index, config.ranking)
    
    # Example queries
    test_queries = [
        "machine learning",
        "python programming",
        "artificial intelligence"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("Results:")
        
        query_terms = text_processor.tokenize(query)
        results = ranker.search(query_terms, max_results=5)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title']}")
                print(f"     URL: {result['url']}")
                print(f"     Score: {result['score']:.4f}")
        else:
            print("  No results found")
    
    # Step 4: Statistics
    print("\n\nSTEP 4: STATISTICS")
    print("-" * 70)
    print(f"Total documents indexed: {indexer.inverted_index.document_count}")
    print(f"Total unique terms: {len(indexer.inverted_index.index)}")
    print(f"Database path: {config.get_full_db_path()}")
    print(f"Index path: {config.get_full_index_path()}\n")
    
    print("="*70)
    print("QUICK START COMPLETE!")
    print("="*70)
    print("\nNext steps:")
    print("1. Run interactive CLI: python main.py")
    print("2. Start API server: python -m uvicorn api.server:app --reload")
    print("3. Check docs: http://localhost:8000/docs")
    print("4. Run tests: pytest tests/ -v")
    print()

if __name__ == "__main__":
    main()
