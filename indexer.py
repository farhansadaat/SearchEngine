"""
Indexing engine for building and managing the inverted index.
"""
import json
import sqlite3
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from datetime import datetime
import logging

from utils.text_processor import TextProcessor
from config import config

logger = logging.getLogger(__name__)

class InvertedIndex:
    """In-memory inverted index."""
    
    def __init__(self):
        """Initialize inverted index."""
        # Maps term -> List[(doc_id, frequency, positions)]
        self.index: Dict[str, List[Tuple[int, int, List[int]]]] = defaultdict(list)
        self.document_count = 0
        self.documents: Dict[int, Dict] = {}  # doc_id -> document metadata
    
    def add_document(self, doc_id: int, doc_metadata: Dict):
        """
        Add document metadata.
        
        Args:
            doc_id: Document ID
            doc_metadata: Document metadata
        """
        self.documents[doc_id] = doc_metadata
        self.document_count += 1
    
    def index_terms(self, doc_id: int, terms: List[str]):
        """
        Index terms from a document.
        
        Args:
            doc_id: Document ID
            terms: List of terms to index
        """
        term_positions = defaultdict(list)
        
        # Build position map
        for position, term in enumerate(terms):
            term_positions[term].append(position)
        
        # Add to inverted index
        for term, positions in term_positions.items():
            frequency = len(positions)
            self.index[term].append((doc_id, frequency, positions))
    
    def get_postings(self, term: str) -> List[Tuple[int, int, List[int]]]:
        """
        Get postings for a term.
        
        Args:
            term: Search term
        
        Returns:
            List of (doc_id, frequency, positions)
        """
        return self.index.get(term, [])
    
    def save_to_json(self, path: str):
        """
        Save index to JSON file.
        
        Args:
            path: File path
        """
        # Convert defaultdict and tuples to JSON-serializable format
        data = {
            'documents': self.documents,
            'index': {
                term: [(doc_id, freq, pos) for doc_id, freq, pos in postings]
                for term, postings in self.index.items()
            }
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Index saved to {path}")
    
    def load_from_json(self, path: str):
        """
        Load index from JSON file.
        
        Args:
            path: File path
        """
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            self.documents = data['documents']
            self.document_count = len(self.documents)
            
            # Reconstruct index
            for term, postings in data['index'].items():
                self.index[term] = [tuple(p) for p in postings]
            
            logger.info(f"Index loaded from {path}")
        except Exception as e:
            logger.error(f"Error loading index: {e}")

class DatabaseManager:
    """Manages SQLite database for storing documents."""
    
    def __init__(self, db_path: str):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        self.connection = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            cursor = self.connection.cursor()
            
            # Create documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    title TEXT,
                    text TEXT,
                    headings TEXT,
                    description TEXT,
                    crawl_time TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            self.connection.commit()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def insert_document(self, url: str, title: str, text: str, 
                       headings: List[str], description: str, crawl_time: datetime) -> int:
        """
        Insert document into database.
        
        Args:
            url: Document URL
            title: Document title
            text: Document text
            headings: Document headings
            description: Document description
            crawl_time: When document was crawled
        
        Returns:
            Document ID
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO documents 
                (url, title, text, headings, description, crawl_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (url, title, text, json.dumps(headings), description, crawl_time.isoformat()))
            
            self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error inserting document: {e}")
            return -1
    
    def get_document(self, doc_id: int) -> Dict:
        """
        Get document by ID.
        
        Args:
            doc_id: Document ID
        
        Returns:
            Document data
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'url': row[1],
                    'title': row[2],
                    'text': row[3],
                    'headings': json.loads(row[4] or '[]'),
                    'description': row[5],
                    'crawl_time': row[6]
                }
        except Exception as e:
            logger.error(f"Error getting document: {e}")
        
        return {}
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()

class Indexer:
    """Main indexing engine."""
    
    def __init__(self, config_obj=None):
        """
        Initialize indexer.
        
        Args:
            config_obj: Configuration object
        """
        self.config = config_obj or config.indexer
        self.text_processor = TextProcessor(
            remove_stopwords=self.config.remove_stopwords,
            language=self.config.language
        )
        self.inverted_index = InvertedIndex()
        self.db = DatabaseManager(config.get_full_db_path())
    
    def index_page(self, doc_id: int, page_content) -> bool:
        """
        Index a single page.
        
        Args:
            doc_id: Document ID
            page_content: PageContent object
        
        Returns:
            True if successful
        """
        try:
            # Store document metadata
            doc_metadata = {
                'url': page_content.url,
                'title': page_content.title,
                'description': page_content.description,
                'crawl_time': page_content.crawl_time.isoformat()
            }
            
            # Insert into database
            db_id = self.db.insert_document(
                page_content.url,
                page_content.title,
                page_content.text,
                page_content.headings,
                page_content.description,
                page_content.crawl_time
            )
            
            if db_id <= 0:
                logger.warning(f"Failed to insert document: {page_content.url}")
                return False
            
            # Add to inverted index
            self.inverted_index.add_document(db_id, doc_metadata)
            
            # Index title with boost
            title_tokens = self.text_processor.tokenize(page_content.title)
            for _ in range(int(self.config.index_title_boost)):
                self.inverted_index.index_terms(db_id, title_tokens)
            
            # Index headings with boost
            heading_text = ' '.join(page_content.headings)
            heading_tokens = self.text_processor.tokenize(heading_text)
            for _ in range(int(self.config.index_heading_boost)):
                self.inverted_index.index_terms(db_id, heading_tokens)
            
            # Index main text
            text_tokens = self.text_processor.tokenize(page_content.text)
            self.inverted_index.index_terms(db_id, text_tokens)
            
            logger.info(f"Indexed document: {page_content.url}")
            return True
        
        except Exception as e:
            logger.error(f"Error indexing page: {e}")
            return False
    
    def index_pages(self, pages) -> int:
        """
        Index multiple pages.
        
        Args:
            pages: List of PageContent objects
        
        Returns:
            Number of successfully indexed pages
        """
        indexed_count = 0
        
        for i, page in enumerate(pages):
            if self.index_page(i + 1, page):
                indexed_count += 1
        
        logger.info(f"Indexed {indexed_count}/{len(pages)} pages")
        return indexed_count
    
    def save_index(self):
        """Save index to disk."""
        self.inverted_index.save_to_json(str(config.get_full_index_path()))
    
    def load_index(self):
        """Load index from disk."""
        self.inverted_index.load_from_json(str(config.get_full_index_path()))
    
    def close(self):
        """Close indexer resources."""
        self.db.close()
