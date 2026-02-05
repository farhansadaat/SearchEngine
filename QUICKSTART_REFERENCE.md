# SEARCH ENGINE - QUICK REFERENCE & HOW TO RUN

## ONE-TIME SETUP (2 minutes)

```bash
cd /Users/farhansadaat/Desktop/python/search-engine

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data (required once)
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

Done! Now you're ready.

---

## FASTEST WAY TO TEST (5 minutes)

```bash
cd /Users/farhansadaat/Desktop/python/search-engine
python quickstart.py
```

**What happens:**
- Crawls 2 Wikipedia pages
- Builds search index
- Runs 3 example searches
- Shows statistics

**Result:** You see the search engine working end-to-end.

---

## INTERACTIVE SEARCH (Recommended)

```bash
python main.py
```

**Menu appears:**
```
Options:
1. Crawl and index websites
2. Search documents
3. Load existing index
4. Exit
```

**Try this:**
1. Select `1` (crawl) - takes 2-5 minutes
2. Select `2` (search) - try "machine learning", "python", etc.
3. See ranked results with snippets

---

## USE AS WEB API

**Terminal 1: Start the server**
```bash
python -m uvicorn api.server:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
Press CTRL+C to quit
```

**Terminal 2: Make requests**
```bash
# Search
curl "http://localhost:8000/search?q=python&limit=10"

# Get stats
curl "http://localhost:8000/stats"

# Health check
curl "http://localhost:8000/health"
```

**Browser: Interactive API docs**
```
Open: http://localhost:8000/docs
```
(You can test all endpoints with Swagger UI - try it!)

---

## RUN TESTS

```bash
pytest tests/ -v
```

Expected: All 30+ tests pass ✓

Run specific tests:
```bash
pytest tests/test_search_engine.py::TestTextProcessor -v
pytest tests/test_search_engine.py::TestInvertedIndex -v
```

---

## CHEAT SHEET

| Task | Command |
|------|---------|
| Demo | `python quickstart.py` |
| Interactive | `python main.py` |
| API Server | `python -m uvicorn api.server:app --reload` |
| All Tests | `pytest tests/ -v` |
| View API Docs | Open http://localhost:8000/docs |
| Check Index | `ls -la data/search_engine.db` |
| View Logs | `tail -f logs/search_engine.log` |

---

## CUSTOMIZE CRAWLING

Edit `config.py`:

```python
self.crawler = CrawlerConfig(
    seed_urls=[
        "https://example.com",
        "https://another-site.com"
    ],
    max_pages=500,        # Crawl this many pages
    max_workers=10,       # Use 10 concurrent workers
)
```

Then run `python main.py` and select option 1.

---

## EXPECTED RESULTS

### After quickstart.py
```
Crawled 47 pages
✓ Indexed 47 pages
Found 12 results for: 'machine learning'
```

### After python main.py + search
```
Query: 'python'
Found: 24 results

1. Python (programming language)
   URL: https://en.wikipedia.org/wiki/Python_...
   Score: 12.54
   Snippet: Python is an interpreted, high-level...
```

### After API search
```json
{
  "query": "machine learning",
  "results": [
    {
      "title": "Machine Learning",
      "url": "https://...",
      "snippet": "Machine learning is a field of...",
      "score": 8.25
    }
  ],
  "total_results": 12,
  "execution_time": 0.032
}
```

---

## TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run: `pip install -r requirements.txt` |
| Tests fail | Install: `pip install pytest pytest-asyncio` |
| No results found | Run crawl first (option 1 in main.py) |
| API port in use | Use: `python -m uvicorn api.server:app --port 9000` |
| Slow crawling | Reduce `max_workers` in config.py |

---

## API Endpoints

### Search
```bash
curl "http://localhost:8000/search?q=machine+learning&limit=10"
```

### Statistics
```bash
curl "http://localhost:8000/stats"
```

### Health Check
```bash
curl "http://localhost:8000/health"
```

### Interactive Docs
```
http://localhost:8000/docs
http://localhost:8000/redoc
```

### Health
```bash
curl "http://localhost:8000/health"
```

## Configuration

Edit `config.py` to change:
- `config.crawler.seed_urls` - Starting URLs
- `config.crawler.max_pages` - Page limit
- `config.crawler.max_workers` - Parallel workers
- `config.indexer.remove_stopwords` - Filter common words
- `config.ranking.algorithm` - Ranking algorithm
- `config.api.port` - API port

## Code Usage

```python
# Crawl websites
from crawler.web_crawler import WebCrawler
import asyncio

crawler = WebCrawler()
pages = asyncio.run(crawler.crawl())

# Index pages
from indexer.indexer import Indexer
indexer = Indexer()
indexer.index_pages(pages)

# Search
from ranking.ranker import Ranker
from utils.text_processor import TextProcessor

processor = TextProcessor()
ranker = Ranker(indexer.inverted_index)

terms = processor.tokenize("machine learning")
results = ranker.search(terms)

for r in results[:5]:
    print(f"{r['title']}: {r['url']} (score: {r['score']:.2f})")
```

## Testing

Run all tests:
```bash
pytest tests/ -v
```

Run specific test:
```bash
pytest tests/test_search_engine.py::TestTextProcessor -v
```

## File Structure Quick Map

```
main.py              → CLI interface
config.py            → Configuration
crawler/             → Web crawling
indexer/             → Full-text index
ranking/             → Search ranking
api/server.py        → REST API
utils/               → Helpers
tests/               → Unit tests
data/                → Storage (auto-created)
logs/                → Logs (auto-created)
```

## Common Tasks

### Change seed URLs
```python
# In config.py, modify:
config.crawler.seed_urls = [
    "https://example.com",
    "https://another.com"
]
```

### Increase crawl speed
```python
# In config.py:
config.crawler.max_workers = 20  # Default: 10
```

### Improve ranking relevance
```python
# In config.py:
config.indexer.index_title_boost = 3.0  # Default: 2.0
config.ranking.boost_title_matches = 3.0
```

### Change database location
```python
# In config.py:
config.storage.db_path = "/custom/path/search.db"
```

## Performance Tips

1. **Faster crawling**: Increase `max_workers` (default 10)
2. **Better ranking**: Increase title/heading boosts
3. **Lower memory**: Reduce `max_pages`
4. **Faster startup**: Load existing index with option 3 in CLI

## Troubleshooting

### Import errors
```bash
# Make sure you're in the right directory
cd search-engine

# And venv is activated
source venv/bin/activate
```

### NLTK data missing
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Port already in use
```bash
# Change port in config.py:
config.api.port = 9000
```

### No results found
- Check seed URLs are accessible
- Verify crawler completed successfully
- Check index was saved
- Try common terms like "the", "python", "web"

## Database

### View documents
```python
from indexer.indexer import DatabaseManager
db = DatabaseManager("data/search_engine.db")
doc = db.get_document(1)
print(doc)
```

### Count documents
```python
import sqlite3
conn = sqlite3.connect("data/search_engine.db")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM documents")
print(cursor.fetchone()[0])
```

## Monitoring

### Check logs
```bash
tail -f logs/search_engine.log
```

### View stats
```bash
curl http://localhost:8000/stats
```

### Check health
```bash
curl http://localhost:8000/health
```

## Deployment

### Docker
```bash
docker-compose up -d
```

### Linux Server
```bash
sudo systemctl start search-engine-api
sudo systemctl status search-engine-api
```

### Kubernetes
```bash
kubectl apply -f k8s/deployment.yaml
```

## Memory/Performance Expectations

- **1,000 documents**: ~50 MB
- **10,000 documents**: ~500 MB
- **100,000 documents**: ~5 GB
- **1M documents**: ~50 GB

Query time: <100ms (depends on query complexity)

## Help

- Full docs: See README.md
- API docs: http://localhost:8000/docs
- Deployment: See DEPLOYMENT.md
- Project overview: See PROJECT_SUMMARY.md

## Key Concepts

**Inverted Index**: Maps words → documents
- Fast lookups: O(1) per term
- Used for full-text search

**TF-IDF**: Relevance scoring
- TF = term frequency in document
- IDF = log(total_docs / docs_with_term)
- Score = TF × IDF × boosting factors

**Field Boosting**: Increase weight of certain fields
- Title matches weighted 2-3x
- Heading matches weighted 1.5x
- Better relevance ranking

## Next Steps

1. ✓ Install and run
2. ✓ Crawl some websites
3. ✓ Try searching
4. ✓ Check API at /docs
5. ✓ Customize config
6. ✓ Deploy to production
7. ✓ Add to portfolio!

---

**Happy searching!**
