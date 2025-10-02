"""
Test Query Script for Azure RAG System
Run predefined test queries to verify the system works
"""

import sys
import os

# Add parent directory to path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.query import query_azure_rag, query_with_hybrid_search


def run_test_queries():
    """Run a set of test queries"""
    
    print("=" * 70)
    print("🧪 Azure RAG System - Test Queries")
    print("=" * 70)
    print()
    
    # Test queries
    test_queries = [
        "What topics are covered in my articles?",
        "What did I write about machine learning?",
        "List all the tools and frameworks mentioned",
        "Summarize the main ideas"
    ]