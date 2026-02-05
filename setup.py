#!/usr/bin/env python3
"""
Setup and startup script for the search engine.
Checks for dependencies and provides helpful setup instructions.
"""

import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = {
        'aiohttp': 'aiohttp',
        'beautifulsoup4': 'bs4',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'pydantic': 'pydantic',
        'pytest': 'pytest',
        'nltk': 'nltk',
        'requests': 'requests',
        'numpy': 'numpy',
    }
    
    missing = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    return missing

def main():
    """Main setup routine."""
    print("\n" + "="*70)
    print("SEARCH ENGINE - SETUP CHECK")
    print("="*70 + "\n")
    
    missing = check_dependencies()
    
    if missing:
        print("❌ Missing dependencies detected:")
        for pkg in missing:
            print(f"   - {pkg}")
        
        print("\n" + "="*70)
        print("SOLUTION: Install dependencies")
        print("="*70 + "\n")
        
        print("Run this command:")
        print("  pip install -r requirements.txt\n")
        
        print("Or install manually:")
        print(f"  pip install {' '.join(missing)}\n")
        
        print("After installing, you can run:")
        print("  python quickstart.py  (Demo - recommended first)")
        print("  python main.py        (Interactive CLI)")
        print("  pytest tests/ -v      (Run tests)\n")
        
        sys.exit(1)
    
    else:
        print("✓ All dependencies installed!\n")
        
        # Try to import and show success
        try:
            from crawler.web_crawler import WebCrawler
            from indexer.indexer import Indexer
            from ranking.ranker import Ranker
            from api.server import app
            
            print("✓ All modules imported successfully!\n")
            print("="*70)
            print("READY TO RUN")
            print("="*70 + "\n")
            
            print("Choose how to run the search engine:\n")
            print("1. Demo (automatic):")
            print("   $ python quickstart.py\n")
            
            print("2. Interactive CLI:")
            print("   $ python main.py\n")
            
            print("3. API Server:")
            print("   $ python -m uvicorn api.server:app --reload\n")
            
            print("4. Tests:")
            print("   $ pytest tests/ -v\n")
            
        except ImportError as e:
            print(f"❌ Error importing modules: {e}")
            print("\nThis shouldn't happen if dependencies are installed.")
            print("Try reinstalling:")
            print("  pip install --force-reinstall -r requirements.txt")
            sys.exit(1)

if __name__ == "__main__":
    main()
