"""
Configuration management for the search engine.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List
import os

@dataclass
class CrawlerConfig:
    """Configuration for the web crawler."""
    seed_urls: List[str]
    max_depth: int = 3
    max_pages: int = 1000
    max_workers: int = 10
    timeout: int = 10
    user_agent: str = "SearchEngineBot/1.0 (+http://searchengine.local/bot)"
    respect_robots_txt: bool = True
    retry_attempts: int = 3
    retry_backoff: float = 2.0
    follow_external_links: bool = False

@dataclass
class IndexerConfig:
    """Configuration for the indexing engine."""
    min_token_length: int = 2
    max_token_length: int = 50
    remove_stopwords: bool = True
    language: str = "english"
    enable_stemming: bool = True
    index_title_boost: float = 2.0
    index_heading_boost: float = 1.5

@dataclass
class RankingConfig:
    """Configuration for the ranking algorithm."""
    algorithm: str = "tfidf"  # Options: "tfidf", "bm25"
    use_sklearn: bool = True
    boost_title_matches: float = 2.0
    boost_heading_matches: float = 1.5

@dataclass
class APIConfig:
    """Configuration for the FastAPI server."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    max_results: int = 20

@dataclass
class StorageConfig:
    """Configuration for data storage."""
    db_path: str = "data/search_engine.db"
    index_path: str = "data/inverted_index.json"
    cache_path: str = "data/cache.json"
    use_sqlite: bool = True

class Config:
    """Main configuration class."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize sub-configs
        self.crawler = CrawlerConfig(
            seed_urls=[
                "https://en.wikipedia.org/wiki/Python_(programming_language)",
                "https://en.wikipedia.org/wiki/Machine_learning",
            ]
        )
        
        self.indexer = IndexerConfig()
        self.ranking = RankingConfig()
        self.api = APIConfig()
        self.storage = StorageConfig(
            db_path=str(self.data_dir / "search_engine.db"),
            index_path=str(self.data_dir / "inverted_index.json"),
            cache_path=str(self.data_dir / "cache.json"),
        )
    
    def get_full_db_path(self) -> Path:
        """Get full path to the database."""
        return self.project_root / self.storage.db_path
    
    def get_full_index_path(self) -> Path:
        """Get full path to the inverted index."""
        return self.project_root / self.storage.index_path
    
    def get_full_cache_path(self) -> Path:
        """Get full path to the cache."""
        return self.project_root / self.storage.cache_path

# Global config instance
config = Config()
