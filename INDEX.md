"""
INDEX.md - Project File Reference

Complete guide to all files in the search engine project.
"""

# SEARCH ENGINE PROJECT - FILE INDEX

## 📁 Project Structure

### Root Files

#### Documentation (Start here!)
- **README.md** - Main documentation with architecture, features, usage
- **PROJECT_SUMMARY.md** - Complete project overview and status
- **DEPLOYMENT.md** - Production deployment guide
- **QUICKSTART_REFERENCE.md** - Quick reference cheat sheet
- **INDEX.md** - This file

#### Configuration & Setup
- **config.py** - Configuration management (edit to customize)
- **requirements.txt** - Python dependencies (pip install)
- **.env.example** - Environment variables template
- **.gitignore** - Git ignore rules

#### Entry Points
- **main.py** - CLI interface (run with `python main.py`)
- **quickstart.py** - Demo script (run with `python quickstart.py`)

---

## 🕷️ Crawler Module (`crawler/`)

**Purpose**: Web crawling and page fetching

- **crawler/__init__.py** - Module initialization
- **crawler/web_crawler.py** - Main crawler implementation
  - `WebCrawler` class - Async crawler with workers
  - `PageContent` class - Crawled page data
  - `RobotsTxtParser` class - robots.txt handling

**Key Features**:
- Asynchronous crawling with asyncio
- robots.txt support with caching
- Retry logic with exponential backoff
- Link extraction and deduplication
- Configurable depth and worker count

---

## 📑 Indexer Module (`indexer/`)

**Purpose**: Building and managing the inverted index

- **indexer/__init__.py** - Module initialization
- **indexer/indexer.py** - Main indexing logic
  - `InvertedIndex` class - In-memory index
  - `DatabaseManager` class - SQLite persistence
  - `Indexer` class - Main indexing engine

**Key Features**:
- Custom inverted index implementation
- Full-text tokenization
- Field boosting (titles, headings)
- SQLite database storage
- JSON index serialization

---

## 🎯 Ranking Module (`ranking/`)

**Purpose**: Search ranking and relevance scoring

- **ranking/__init__.py** - Module initialization
- **ranking/ranker.py** - Ranking implementation
  - `TFIDFRanker` class - TF-IDF algorithm
  - `Ranker` class - Main search engine
- **ranking/snippets.py** - Snippet generation
  - `SnippetGenerator` class - Extract context snippets

**Key Features**:
- Manual TF-IDF implementation
- IDF calculation (log(N/df))
- Document scoring and ranking
- Title/heading boost application
- Snippet generation with context

---

## 🔌 API Module (`api/`)

**Purpose**: REST API server

- **api/__init__.py** - Module initialization
- **api/server.py** - FastAPI server
  - Search endpoint: GET /search?q=query
  - Stats endpoint: GET /stats
  - Health endpoint: GET /health
  - Auto docs: http://localhost:8000/docs

**Key Features**:
- FastAPI framework
- Async request handling
- Type validation with Pydantic
- Pagination support
- Performance metrics

---

## 🛠️ Utils Module (`utils/`)

**Purpose**: Utility functions and helpers

- **utils/__init__.py** - Module initialization
- **utils/logger.py** - Logging configuration
  - `setup_logging()` - Configure rotating file logs
- **utils/text_processor.py** - Text/HTML/URL processing
  - `TextProcessor` class - Tokenization, cleaning
  - `HTMLProcessor` class - HTML parsing, extraction
  - `URLProcessor` class - URL validation, normalization

**Key Features**:
- HTML parsing with BeautifulSoup
- NLTK-based tokenization
- Stopword removal
- Link discovery
- URL normalization

---

## ✅ Tests Module (`tests/`)

**Purpose**: Unit tests with pytest

- **tests/__init__.py** - Module initialization
- **tests/test_search_engine.py** - Test suite
  - TestTextProcessor - Text processing tests
  - TestHTMLProcessor - HTML parsing tests
  - TestURLProcessor - URL processing tests
  - TestInvertedIndex - Index operation tests
  - TestTFIDFRanker - Ranking algorithm tests
  - TestPageContent - Page data tests

**Key Features**:
- 30+ test cases
- Coverage of core components
- Edge case handling
- Run with: `pytest tests/ -v`

---

## 💾 Data Directory (`data/`)

**Purpose**: Runtime storage (created automatically)

- `search_engine.db` - SQLite database (documents)
- `inverted_index.json` - Serialized index
- `cache.json` - Query cache

---

## 📊 File Statistics

### Code Files
- **Python modules**: 15 files
- **Lines of code**: ~2,500+
- **Test cases**: 30+

### Documentation
- **Markdown files**: 4 files
- **Documentation lines**: ~1,500+

### Configuration
- **Config files**: 3 files
- **Dependencies**: 15+ packages

---

## 🚀 How to Use

### For Quick Start
1. Read: **README.md** (5 min)
2. Setup: Follow installation steps
3. Run: `python quickstart.py`

### For Understanding
1. Read: **PROJECT_SUMMARY.md** (15 min)
2. Browse: Source code starting with `main.py`
3. Review: **README.md** design decisions

### For Development
1. Check: **config.py** for customization
2. Edit: Individual module files
3. Test: `pytest tests/`
4. Debug: Check `logs/search_engine.log`

### For Deployment
1. Read: **DEPLOYMENT.md** completely
2. Choose: Deployment option (Linux, Docker, K8s)
3. Follow: Step-by-step instructions
4. Monitor: Health endpoints

### For Quick Reference
1. Use: **QUICKSTART_REFERENCE.md**
2. Common tasks and commands
3. Troubleshooting tips

---

## 📖 Reading Order (by purpose)

### If you want to understand the architecture:
1. README.md → Architecture section
2. PROJECT_SUMMARY.md → Architecture diagram
3. config.py → Configuration structure
4. main.py → Entry point logic

### If you want to understand the code:
1. utils/text_processor.py → Basic utilities
2. crawler/web_crawler.py → Web crawling logic
3. indexer/indexer.py → Indexing engine
4. ranking/ranker.py → Ranking algorithm
5. api/server.py → API endpoints

### If you want to deploy:
1. README.md → Installation section
2. DEPLOYMENT.md → Full deployment guide
3. QUICKSTART_REFERENCE.md → Quick reference

### If you want to modify/extend:
1. config.py → Edit configurations
2. Specific module → Modify functionality
3. tests/test_search_engine.py → Add/update tests

---

## 🎯 Module Dependencies

```
main.py
├── crawler/web_crawler.py
├── indexer/indexer.py
├── ranking/ranker.py
├── utils/text_processor.py
└── utils/logger.py

api/server.py
├── indexer/indexer.py
├── ranking/ranker.py
├── ranking/snippets.py
└── utils/text_processor.py

config.py (no dependencies)
```

---

## 🔑 Key Classes by Module

### crawler/web_crawler.py
- `WebCrawler` - Main crawler
- `PageContent` - Crawled page
- `RobotsTxtParser` - robots.txt handler

### indexer/indexer.py
- `InvertedIndex` - Index structure
- `DatabaseManager` - Database access
- `Indexer` - Indexing engine

### ranking/ranker.py
- `TFIDFRanker` - Ranking algorithm
- `Ranker` - Search interface

### ranking/snippets.py
- `SnippetGenerator` - Snippet extraction

### api/server.py
- `app` - FastAPI application
- `SearchResult` - Result schema
- `SearchResponse` - Response schema

### utils/text_processor.py
- `TextProcessor` - Text tokenization
- `HTMLProcessor` - HTML parsing
- `URLProcessor` - URL handling

### utils/logger.py
- `setup_logging()` - Log configuration

---

## 💡 Tips for Using This Project

1. **Start with README.md** for overview
2. **Check config.py** before running
3. **Use QUICKSTART_REFERENCE.md** for commands
4. **Read docstrings** in source code
5. **Run tests** after modifications
6. **Check logs** when debugging
7. **Refer to DEPLOYMENT.md** for production

---

## 📚 External Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **asyncio**: https://docs.python.org/3/library/asyncio.html
- **BeautifulSoup**: https://www.crummy.com/software/BeautifulSoup/
- **SQLite**: https://www.sqlite.org/
- **NLTK**: https://www.nltk.org/

---

## 🎓 Learning Path

**Beginner**:
1. Run `python quickstart.py` to see it work
2. Use CLI with `python main.py`
3. Try API with curl commands

**Intermediate**:
1. Read config.py and customize
2. Modify seed URLs
3. Change ranking boosts
4. Run tests

**Advanced**:
1. Study crawler/web_crawler.py
2. Understand TF-IDF in ranking/ranker.py
3. Modify indexing logic
4. Extend with new features

---

## 📋 Checklist for Getting Started

- [ ] Read README.md (15 min)
- [ ] Run `pip install -r requirements.txt` (5 min)
- [ ] Run `python quickstart.py` (5 min)
- [ ] Try CLI with `python main.py` (5 min)
- [ ] Start API server (5 min)
- [ ] Visit http://localhost:8000/docs
- [ ] Read config.py and understand structure
- [ ] Run tests with `pytest tests/ -v`
- [ ] Read one module source code
- [ ] Modify config and re-run

---

**Total Time: ~1 hour to understand the complete project**

---

For more details, see the individual files and their docstrings!
