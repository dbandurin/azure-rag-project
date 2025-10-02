"""
Test Query Script for Azure RAG System
Simple script to test queries
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.query import query_azure_rag


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
    
    print(f"Running {len(test_queries)} test queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print("=" * 70)
        print(f"Test Query {i}/{len(test_queries)}")
        print("=" * 70)
        print(f"Question: {query}\n")
        
        try:
            result = query_azure_rag(query, top_k=4, verbose=False)
            
            print("📝 Answer:")
            print("-" * 70)
            print(result['answer'])
            print("-" * 70)
            print()
            print(f"📊 Retrieved {result['num_chunks']} chunks from {len(result['sources'])} file(s)")
            if result['sources']:
                print(f"📚 Sources: {', '.join(result['sources'][:3])}")
            print("\n")
            
        except Exception as e:
            print(f"❌ Error: {e}\n\n")
        
        if i < len(test_queries):
            input("Press Enter for next query...")
            print()
    
    print("=" * 70)
    print("✅ All test queries completed!")
    print("=" * 70)


def run_single_query(question: str):
    """Run a single query"""
    
    print("=" * 70)
    print("🔍 Single Query Test")
    print("=" * 70)
    print(f"Question: {question}\n")
    
    try:
        result = query_azure_rag(question, top_k=4, verbose=True)
        
        print("\n" + "=" * 70)
        print("📝 Answer:")
        print("=" * 70)
        print(result['answer'])
        print("\n" + "=" * 70)
        print(f"📊 Retrieved {result['num_chunks']} chunks from {len(result['sources'])} file(s)")
        if result['sources']:
            print(f"📚 Sources: {', '.join(result['sources'])}")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/test_query.py test              # Run predefined test queries")
        print("  python scripts/test_query.py '<your question>' # Run single query")
        print()
        print("Examples:")
        print("  python scripts/test_query.py test")
        print("  python scripts/test_query.py 'What did I write about AI?'")
        sys.exit(1)
    
    if sys.argv[1] == "test":
        run_test_queries()
    else:
        question = " ".join(sys.argv[1:])
        run_single_query(question)