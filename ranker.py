"""
Ranking and relevance scoring for search results.
"""
import math
from typing import List, Dict, Tuple
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class TFIDFRanker:
    """TF-IDF ranking algorithm (manual implementation)."""
    
    def __init__(self, inverted_index, boost_title: float = 2.0, boost_heading: float = 1.5):
        """
        Initialize TF-IDF ranker.
        
        Args:
            inverted_index: InvertedIndex object
            boost_title: Title match boost factor
            boost_heading: Heading match boost factor
        """
        self.inverted_index = inverted_index
        self.boost_title = boost_title
        self.boost_heading = boost_heading
        self.idf_cache: Dict[str, float] = {}
    
    def calculate_idf(self, term: str) -> float:
        """
        Calculate IDF (Inverse Document Frequency).
        
        Args:
            term: Search term
        
        Returns:
            IDF value
        """
        if term in self.idf_cache:
            return self.idf_cache[term]
        
        postings = self.inverted_index.get_postings(term)
        if not postings:
            return 0.0
        
        # IDF = log(N / df)
        N = self.inverted_index.document_count
        df = len(postings)  # Document frequency
        
        if df == 0:
            return 0.0
        
        idf = math.log(N / df) if N > 0 else 0.0
        self.idf_cache[term] = idf
        return idf
    
    def calculate_tf(self, term: str, doc_id: int) -> float:
        """
        Calculate TF (Term Frequency).
        
        Args:
            term: Search term
            doc_id: Document ID
        
        Returns:
            TF value
        """
        postings = self.inverted_index.get_postings(term)
        
        for posting_doc_id, frequency, _ in postings:
            if posting_doc_id == doc_id:
                # TF = frequency
                return float(frequency)
        
        return 0.0
    
    def score_document(self, query_terms: List[str], doc_id: int, 
                      doc_metadata: Dict) -> float:
        """
        Score a document for a query.
        
        Args:
            query_terms: List of query terms
            doc_id: Document ID
            doc_metadata: Document metadata
        
        Returns:
            Relevance score
        """
        score = 0.0
        
        for term in query_terms:
            tf = self.calculate_tf(term, doc_id)
            idf = self.calculate_idf(term)
            tfidf = tf * idf
            
            # Apply title boost
            if term.lower() in (doc_metadata.get('title', '') or '').lower():
                tfidf *= self.boost_title
            
            score += tfidf
        
        return score
    
    def rank_results(self, query_terms: List[str], 
                     doc_ids: List[int]) -> List[Tuple[int, float]]:
        """
        Rank documents by relevance.
        
        Args:
            query_terms: List of query terms
            doc_ids: List of document IDs to rank
        
        Returns:
            List of (doc_id, score) sorted by score descending
        """
        scores = []
        
        for doc_id in doc_ids:
            doc_metadata = self.inverted_index.documents.get(doc_id, {})
            score = self.score_document(query_terms, doc_id, doc_metadata)
            
            if score > 0:
                scores.append((doc_id, score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

class Ranker:
    """Main ranking engine."""
    
    def __init__(self, inverted_index, config_obj=None):
        """
        Initialize ranker.
        
        Args:
            inverted_index: InvertedIndex object
            config_obj: Configuration object
        """
        from config import config as default_config
        self.config = config_obj or default_config.ranking
        self.inverted_index = inverted_index
        
        # Initialize ranker based on algorithm
        if self.config.algorithm == 'tfidf':
            self.ranker = TFIDFRanker(
                inverted_index,
                boost_title=self.config.boost_title_matches,
                boost_heading=self.config.boost_heading_matches
            )
        else:
            self.ranker = TFIDFRanker(
                inverted_index,
                boost_title=self.config.boost_title_matches,
                boost_heading=self.config.boost_heading_matches
            )
    
    def search(self, query_terms: List[str], max_results: int = 20) -> List[Dict]:
        """
        Search for documents.
        
        Args:
            query_terms: List of query terms
            max_results: Maximum number of results to return
        
        Returns:
            List of ranked results with metadata
        """
        # Find documents containing any of the query terms
        doc_ids_set = set()
        
        for term in query_terms:
            postings = self.inverted_index.get_postings(term)
            for doc_id, _, _ in postings:
                doc_ids_set.add(doc_id)
        
        if not doc_ids_set:
            logger.info(f"No results found for query: {' '.join(query_terms)}")
            return []
        
        # Rank documents
        ranked = self.ranker.rank_results(query_terms, list(doc_ids_set))
        
        # Format results
        results = []
        for doc_id, score in ranked[:max_results]:
            doc_metadata = self.inverted_index.documents.get(doc_id, {})
            results.append({
                'doc_id': doc_id,
                'url': doc_metadata.get('url', ''),
                'title': doc_metadata.get('title', ''),
                'description': doc_metadata.get('description', ''),
                'score': score
            })
        
        logger.info(f"Found {len(results)} results for query: {' '.join(query_terms)}")
        return results
