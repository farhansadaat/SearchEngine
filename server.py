"""
FastAPI web server for the search engine.
"""
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import logging

from utils.text_processor import TextProcessor
from ranking.ranker import Ranker
from ranking.snippets import SnippetGenerator
from indexer.indexer import Indexer
from config import config

logger = logging.getLogger(__name__)

# Initialize components
text_processor = TextProcessor()
snippet_generator = SnippetGenerator()
indexer = Indexer()
indexer.load_index()
ranker = Ranker(indexer.inverted_index)

# Create FastAPI app
app = FastAPI(
    title="Search Engine API",
    description="A production-quality search engine built from scratch",
    version="1.0.0"
)

class SearchResult(BaseModel):
    """Search result model."""
    title: str
    url: str
    snippet: str
    score: float

class SearchResponse(BaseModel):
    """Search response model."""
    query: str
    results: List[SearchResult]
    total_results: int
    execution_time: float

@app.get("/", tags=["health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Search Engine API is running",
        "version": "1.0.0"
    }

@app.get("/search", response_model=SearchResponse, tags=["search"])
async def search(
    q: str = Query(..., min_length=1, max_length=200),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Search for documents.
    
    Args:
        q: Search query
        limit: Maximum number of results (default: 20, max: 100)
        offset: Result offset for pagination (default: 0)
    
    Returns:
        SearchResponse with ranked results
    """
    import time
    start_time = time.time()
    
    try:
        # Process query
        query_terms = text_processor.tokenize(q)
        
        if not query_terms:
            return SearchResponse(
                query=q,
                results=[],
                total_results=0,
                execution_time=time.time() - start_time
            )
        
        # Search
        raw_results = ranker.search(query_terms, max_results=limit + offset)
        
        # Apply pagination
        paginated_results = raw_results[offset:offset + limit]
        
        # Generate snippets
        results = []
        for result in paginated_results:
            doc = indexer.db.get_document(result['doc_id'])
            if doc:
                snippet = snippet_generator.generate_snippet(
                    doc.get('text', ''),
                    query_terms
                )
                
                results.append(SearchResult(
                    title=result['title'],
                    url=result['url'],
                    snippet=snippet,
                    score=result['score']
                ))
        
        return SearchResponse(
            query=q,
            results=results,
            total_results=len(raw_results),
            execution_time=time.time() - start_time
        )
    
    except Exception as e:
        logger.error(f"Error processing search: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

@app.get("/stats", tags=["stats"])
async def stats():
    """Get search engine statistics."""
    return {
        "total_documents": indexer.inverted_index.document_count,
        "index_size": len(indexer.inverted_index.index),
        "max_results_per_query": config.api.max_results
    }

@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint with index status."""
    return {
        "status": "healthy",
        "indexed_documents": indexer.inverted_index.document_count,
        "terms_indexed": len(indexer.inverted_index.index)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.api.host,
        port=config.api.port,
        debug=config.api.debug
    )
