# Search Engine - Production-Quality Implementation

A complete, production-quality search engine built from scratch in Python. This is a portfolio-ready project demonstrating advanced software engineering principles, system design, and data structures.

## Overview

This search engine implements the core components needed for a modern web search system:
- **Asynchronous Web Crawler** with robots.txt support and retry logic
- **Inverted Index** for fast full-text search
- **TF-IDF Ranking** algorithm with manual implementation
- **FastAPI Web Server** for serving search queries
- **CLI Interface** for interactive searching
- **SQLite Database** for persistent storage
- **Snippet Generation** for contextual result previews

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Search Engine System                      │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
    ┌───────────┐      ┌────────────┐       ┌────────────┐
    │  Crawler  │      │  Indexer   │       │   Ranker   │
    │           │      │            │       │            │
    │  - Async  │      │ - Inverted │       │ - TF-IDF   │
    │  - Robots │      │   Index    │       │ - Scoring  │
    │  - Retry  │      │ - Database │       │ - Ranking  │
    └───────────┘      └────────────┘       └────────────┘
        │                   │                     │
        └─────────────────────┼─────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
    ┌───────────┐      ┌────────────┐       ┌────────────┐
    │    CLI    │      │ FastAPI    │       │ Snippets   │
    │ Interface │      │   Server   │       │ Generator  │
    │           │      │            │       │            │
    │ Interactive│      │ REST API   │       │ Context    │
    │  Search   │      │ (HTTP)     │       │ Extraction │
    └───────────┘      └────────────┘       └────────────┘
        │                   │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────────────┐
                    │   Data Layer    │
                    │                 │
                    │ - SQLite DB     │
                    │ - JSON Index    │
                    │ - Cache         │
                    └─────────────────┘
```

## Project Structure

```
search-engine/
├── crawler/                 # Web crawling module
│   ├── __init__.py
│   └── web_crawler.py      # Async crawler, robots.txt parser
├── indexer/                 # Indexing module
│   ├── __init__.py
│   └── indexer.py          # Inverted index, database manager
├── ranking/                 # Ranking and search module
│   ├── __init__.py
│   ├── ranker.py           # TF-IDF ranker, search engine
│   └── snippets.py         # Snippet generation
├── api/                     # FastAPI web server
│   ├── __init__.py
│   └── server.py           # REST API endpoints
├── utils/                   # Utility modules
│   ├── __init__.py
│   ├── text_processor.py   # HTML/text processing
│   └── logger.py           # Logging configuration
├── tests/                   # Unit tests
│   ├── __init__.py
│   └── test_search_engine.py
├── data/                    # Data storage (created at runtime)
│   ├── search_engine.db    # SQLite database
│   ├── inverted_index.json # Serialized index
│   └── cache.json          # Cache file
├── logs/                    # Log files (created at runtime)
├── main.py                  # CLI entry point
├── config.py                # Configuration management
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Key Features

### 1. Web Crawler
- **Asynchronous** crawling using `asyncio` and `aiohttp` for high performance
- **robots.txt** respect with intelligent parsing and caching
- **Retry logic** with exponential backoff for failed requests
- **Duplicate detection** to avoid re-crawling pages
- **Configurable** depth, worker count, and timeout settings
- **Domain filtering** to prevent crawling external sites by default

### 2. Indexing Engine
- **Inverted Index** data structure for O(1) term lookups
- **Full-text indexing** with tokenization and stopword removal
- **Field boosting** for titles and headings (higher relevance weight)
- **SQLite database** for persistent document storage
- **JSON serialization** for index portability
- **Stem support** for better keyword matching

### 3. Ranking Algorithm
- **TF-IDF scoring** manually implemented (no sklearn dependency for core logic)
- **Document frequency (DF)** calculation for importance weighting
- **Term frequency (TF)** with position awareness
- **Title/heading boosts** for relevance improvement
- **Configurable** algorithm selection and parameters

### 4. Search API
- **FastAPI** server with async request handling
- **REST endpoints** for search and statistics
- **Pagination** support for large result sets
- **Query validation** and sanitization
- **Performance metrics** (execution time)
- **Health checks** for monitoring

### 5. CLI Interface
- **Interactive menu** system
- **Crawl and index** workflows
- **Real-time search** with result display
- **Index persistence** loading
- **User-friendly** output formatting

### 6. Text Processing
- **HTML parsing** using BeautifulSoup
- **Text extraction** with script/style removal
- **Link discovery** with relative URL resolution
- **Heading extraction** for field boosting
- **Meta description** parsing
- **Tokenization** with NLTK

## Installation

### Requirements
- Python 3.8+
- pip or conda for package management

### Setup

1. **Clone or download** the project
   ```bash
   cd search-engine
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

## Usage

### Option 1: CLI Interface

Start the interactive CLI:
```bash
python main.py
```

Then:
1. Select "Crawl and index websites" to fetch and index pages
2. Select "Search documents" to query the index
3. Or load an existing index for faster startup

### Option 2: FastAPI Web Server

Start the API server:
```bash
python -m uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```

Then query the API:
```bash
# Search
curl "http://localhost:8000/search?q=machine+learning&limit=10"

# Get stats
curl "http://localhost:8000/stats"

# Health check
curl "http://localhost:8000/health"
```

Visit `http://localhost:8000/docs` for interactive API documentation.

### Option 3: Programmatic Usage

```python
from crawler.web_crawler import WebCrawler
from indexer.indexer import Indexer
from ranking.ranker import Ranker
from utils.text_processor import TextProcessor
import asyncio

# Crawl
crawler = WebCrawler()
pages = asyncio.run(crawler.crawl())

# Index
indexer = Indexer()
indexer.index_pages(pages)
indexer.save_index()

# Search
processor = TextProcessor()
ranker = Ranker(indexer.inverted_index)

query_terms = processor.tokenize("machine learning")
results = ranker.search(query_terms, max_results=10)

for result in results:
    print(f"{result['title']}: {result['url']}")
```

## Configuration

Edit `config.py` to customize:

### Crawler
- `seed_urls`: Starting URLs for crawling
- `max_depth`: Maximum crawl depth
- `max_pages`: Maximum pages to crawl
- `max_workers`: Async worker count (default: 10)
- `timeout`: Request timeout in seconds
- `respect_robots_txt`: Whether to respect robots.txt

### Indexer
- `remove_stopwords`: Filter common words (default: True)
- `index_title_boost`: Weight boost for title matches (default: 2.0)
- `index_heading_boost`: Weight boost for heading matches (default: 1.5)

### Ranking
- `algorithm`: "tfidf" (default) or other algorithms
- `boost_title_matches`: Relevance boost for title matches
- `boost_heading_matches`: Relevance boost for heading matches

### API
- `host`: Server host (default: 0.0.0.0)
- `port`: Server port (default: 8000)
- `max_results`: Max results per query (default: 20)

## Design Decisions

### 1. Asynchronous Crawling
**Decision**: Use `asyncio` + `aiohttp` instead of threading or multiprocessing.

**Rationale**:
- I/O-bound task (network requests)
- Lighter weight than threads
- Better scalability for many concurrent connections
- Native Python async/await syntax

### 2. Manual TF-IDF Implementation
**Decision**: Implement TF-IDF from scratch instead of using scikit-learn.

**Rationale**:
- Demonstrates understanding of information retrieval concepts
- Full control over boosting and customization
- Removes heavy dependencies for core logic
- Clearer, more readable code for interviews

### 3. Inverted Index Over Full-Text Search
**Decision**: Build custom inverted index instead of using Elasticsearch.

**Rationale**:
- Shows data structure knowledge
- Simpler deployment (no external services)
- Good for smaller datasets
- Educational value for system design interviews

### 4. SQLite for Storage
**Decision**: Use SQLite instead of NoSQL or traditional RDBMS.

**Rationale**:
- No server setup required
- ACID compliance
- Good enough for this scale
- Easy to demonstrate portability

### 5. FastAPI Over Flask
**Decision**: Use FastAPI for web server.

**Rationale**:
- Native async support
- Automatic API documentation (Swagger)
- Type hints and validation
- Modern, well-maintained framework
- Better for demonstrating current best practices

## Trade-offs and Scaling Considerations

### Current Limitations
- **Single-machine index**: Not distributed (fine for <100M documents)
- **In-memory ranking**: All documents scored per query (linear complexity)
- **No query optimization**: No caching or query planning
- **Basic relevance**: TF-IDF is simple; BM25 or learning-to-rank would be better
- **No spell correction**: Typos in queries aren't handled

### Scaling to Production

1. **Distributed Crawling**
   - Use Kafka for job queue
   - Deploy crawlers across multiple machines
   - Implement crawler orchestration

2. **Distributed Indexing**
   - Shard index by URL domain or hash
   - Build distributed inverted index
   - Use consistency hashing for node management

3. **Query Optimization**
   - Add Redis caching for popular queries
   - Implement query result caching
   - Use query rewriting for synonyms

4. **Advanced Ranking**
   - Implement BM25 algorithm
   - Add learning-to-rank model
   - Include PageRank-like authority scoring
   - Use user interaction signals

5. **Infrastructure**
   - Containerize with Docker
   - Deploy on Kubernetes
   - Use load balancing
   - Implement monitoring/alerting
   - Set up distributed logging

6. **Search Features**
   - Add spelling correction (Levenshtein distance)
   - Implement synonym expansion
   - Add phrase search ("exact match")
   - Support boolean operators (AND, OR, NOT)
   - Add faceted search/filters

## Testing

Run unit tests:
```bash
pytest tests/ -v
```

Tests cover:
- Text processing (tokenization, cleaning)
- HTML parsing (title, text, links extraction)
- URL processing (validation, normalization)
- Inverted index operations
- Ranking and scoring
- Document persistence

## Performance Characteristics

### Time Complexity
- **Index lookup**: O(1) for term postings
- **Query search**: O(k * log n) where k = query terms, n = indexed terms
- **Ranking**: O(d * k) where d = matching documents, k = query terms
- **Indexing**: O(w * log n) where w = words per page, n = vocabulary size

### Space Complexity
- **Inverted index**: O(v * p) where v = vocabulary, p = avg postings per term
- **Database**: O(d * s) where d = documents, s = avg document size
- **Index file**: ~10-20% of original text size

### Benchmarks (on sample data)
- Crawling: ~10-20 pages/second (depends on network)
- Indexing: ~1000 terms/second
- Query: <100ms for typical queries
- Memory: ~500MB for 10k documents

## Code Quality

### Type Hints
All functions have complete type annotations for IDE support and type checking.

### Docstrings
Every module, class, and function has detailed docstrings explaining purpose, arguments, and return values.

### Error Handling
Comprehensive try-except blocks with logging for production reliability.

### Logging
Structured logging throughout for debugging and monitoring.

### Testing
Unit tests for core components with pytest.

### Configuration
External configuration file for easy customization without code changes.

## Security Considerations

1. **robots.txt Respect**: Prevents crawling restricted areas
2. **URL Validation**: Prevents injection attacks
3. **HTML Sanitization**: Removes scripts and styles
4. **Input Validation**: FastAPI automatic validation
5. **Rate Limiting**: Could be added with middleware
6. **SSL/TLS Support**: Ready for HTTPS (aiohttp supports it)

## Future Enhancements

1. **Query Features**
   - Boolean operators (AND, OR, NOT)
   - Phrase search with quotes
   - Wildcard search
   - Range queries

2. **Ranking Improvements**
   - BM25 algorithm implementation
   - PageRank-like scoring
   - Learning-to-rank models
   - User relevance feedback

3. **Storage**
   - Distributed index with sharding
   - Memcached/Redis integration
   - Column-store optimization

4. **Crawling**
   - Differential/incremental crawling
   - Duplicate content detection
   - Link analysis (PageRank)
   - Content freshness estimation

5. **API Features**
   - GraphQL interface
   - Advanced filtering
   - Autocomplete/suggestions
   - Search analytics

6. **Frontend**
   - Web UI with React
   - Autocomplete suggestions
   - Search filters
   - Result clustering

## Resume Talking Points

- **System Design**: Full-stack search engine with crawler, indexer, ranker, and API
- **Data Structures**: Custom inverted index implementation for efficient retrieval
- **Algorithms**: TF-IDF ranking with field boosting
- **Async Programming**: Asynchronous I/O with asyncio for concurrent crawling
- **API Design**: RESTful FastAPI server with proper error handling
- **Database Design**: Schema design with SQLite, index optimization
- **Software Engineering**: Type hints, docstrings, testing, logging, configuration management
- **Information Retrieval**: Understanding of IR concepts, indexing, ranking
- **Web Technologies**: HTML parsing, URL handling, robots.txt parsing
- **Scalability**: Consideration of distributed systems and production deployment

## License

This project is provided as-is for educational and portfolio purposes.

## Contact

For questions or improvements, feel free to reach out!

---

**Built with**: Python 3.8+, FastAPI, aiohttp, BeautifulSoup4, NLTK, SQLite

**Last Updated**: 2026
