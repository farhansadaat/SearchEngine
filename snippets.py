"""
Snippet generation for search results.
"""
from typing import List, Optional
import re
from utils.text_processor import TextProcessor

class SnippetGenerator:
    """Generates snippets from document text."""
    
    def __init__(self, snippet_length: int = 200):
        """
        Initialize snippet generator.
        
        Args:
            snippet_length: Maximum length of snippet
        """
        self.snippet_length = snippet_length
        self.text_processor = TextProcessor()
    
    def generate_snippet(self, text: str, query_terms: List[str]) -> str:
        """
        Generate a snippet around the most relevant sentence.
        
        Args:
            text: Document text
            query_terms: Query terms for context
        
        Returns:
            Generated snippet
        """
        if not text or not query_terms:
            return text[:self.snippet_length]
        
        # Split text into sentences
        sentences = self._split_sentences(text)
        
        if not sentences:
            return text[:self.snippet_length]
        
        # Find best sentence containing query terms
        best_sentence = None
        best_score = 0
        
        for sentence in sentences:
            score = self._score_sentence(sentence, query_terms)
            if score > best_score:
                best_score = score
                best_sentence = sentence
        
        # If no matching sentence, take first sentence
        if best_sentence is None:
            best_sentence = sentences[0]
        
        # Truncate if needed
        if len(best_sentence) > self.snippet_length:
            best_sentence = best_sentence[:self.snippet_length] + "..."
        
        return best_sentence.strip()
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitter
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _score_sentence(self, sentence: str, query_terms: List[str]) -> float:
        """Score a sentence based on query term presence."""
        sentence_lower = sentence.lower()
        score = 0.0
        
        for term in query_terms:
            if term.lower() in sentence_lower:
                score += 1.0
        
        return score
