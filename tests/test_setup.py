"""Test script to verify installation"""

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import azure.search.documents
        print("✓ Azure Search Documents")
        
        import azure.storage.blob
        print("✓ Azure Storage Blob")
        
        import langchain
        print("✓ LangChain")
        
        import langchain_anthropic
        print("✓ LangChain Anthropic")
        
        from sentence_transformers import SentenceTransformer
        print("✓ Sentence Transformers")
        
        import pypdf
        print("✓ PyPDF")
        
        from dotenv import load_dotenv
        print("✓ Python Dotenv")
        
        print("\n✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import failed: {e}")
        return False


def test_environment():
    """Test that environment variables are loaded"""
    import os
    from dotenv import load_dotenv
    
    print("\nTesting environment variables...")
    load_dotenv()
    
    required_vars = [
        'AZURE_SEARCH_ENDPOINT',
        'AZURE_SEARCH_KEY',
        'ANTHROPIC_API_KEY'
    ]
    
    missing = []
    for var in required_vars:
        if os.getenv(var):
            print(f"✓ {var} is set")
        else:
            print(f"✗ {var} is missing")
            missing.append(var)
    
    if missing:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing)}")
        print("Please add them to your .env file")
        return False
    else:
        print("\n✅ All environment variables set!")
        return True


def test_embedding_model():
    """Test that embedding model can be loaded"""
    print("\nTesting embedding model...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        test_text = "This is a test sentence."
        embedding = model.encode(test_text)
        
        print(f"✓ Model loaded successfully")
        print(f"✓ Embedding dimension: {len(embedding)}")
        print("\n✅ Embedding model working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Embedding test failed: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("Azure RAG Setup Verification")
    print("="*60 + "\n")
    
    results = []
    results.append(test_imports())
    results.append(test_environment())
    results.append(test_embedding_model())
    
    print("\n" + "="*60)
    if all(results):
        print("🎉 Setup verification passed! You're ready to go!")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
    print("="*60)