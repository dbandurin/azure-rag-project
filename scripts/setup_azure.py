"""
Azure RAG Setup Script
Creates index in Azure AI Search with vector search capability
"""

from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
)
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configuration
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "articles-index")


def create_search_index():
    """Create Azure AI Search index with vector search"""
    
    print("🔧 Setting up Azure AI Search...")
    print(f"   Endpoint: {SEARCH_ENDPOINT}")
    print(f"   Index Name: {INDEX_NAME}")
    
    # Validate credentials
    if not SEARCH_ENDPOINT or not SEARCH_KEY:
        print("❌ Error: AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY must be set in .env")
        return False
    
    # Create index client
    index_client = SearchIndexClient(
        endpoint=SEARCH_ENDPOINT,
        credential=AzureKeyCredential(SEARCH_KEY)
    )
    
    print("\n📋 Defining index schema...")
    
    # Define index fields
    fields = [
        SearchField(
            name="id",
            type=SearchFieldDataType.String,
            key=True,
            sortable=True,
            filterable=True
        ),
        SearchField(
            name="content",
            type=SearchFieldDataType.String,
            searchable=True,
            analyzer_name="en.microsoft"
        ),
        SearchField(
            name="source_file",
            type=SearchFieldDataType.String,
            filterable=True,
            facetable=True,
            sortable=True
        ),
        SearchField(
            name="page_number",
            type=SearchFieldDataType.Int32,
            filterable=True,
            sortable=True
        ),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=384,  # all-MiniLM-L6-v2 produces 384-dim vectors
            vector_search_profile_name="vector-profile"
        ),
    ]
    
    print("   ✓ Fields defined:")
    print("     - id (key)")
    print("     - content (searchable text)")
    print("     - source_file (filterable)")
    print("     - page_number (filterable)")
    print("     - chunk_id (filterable)")
    print("     - content_vector (384 dimensions)")
    
    # Configure vector search with HNSW algorithm
    vector_search = VectorSearch(
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw-config"
            )
        ],
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-config",
                parameters={
                    "m": 4,  # Number of bi-directional links
                    "efConstruction": 400,  # Size of dynamic candidate list for construction
                    "efSearch": 500,  # Size of dynamic candidate list for search
                    "metric": "cosine"  # Similarity metric
                }
            )
        ],
    )
    
    print("\n🔍 Configuring vector search:")
    print("   - Algorithm: HNSW (Hierarchical Navigable Small World)")
    print("   - Metric: Cosine similarity")
    print("   - Optimized for semantic search")
    
    # Create the index
    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        vector_search=vector_search
    )
    
    print(f"\n📤 Creating index '{INDEX_NAME}'...")
    
    try:
        result = index_client.create_or_update_index(index)
        print(f"   ✅ Index '{result.name}' created successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating index: {e}")
        return False


def verify_index():
    """Verify that index was created successfully"""
    
    print("\n🔎 Verifying index...")
    
    index_client = SearchIndexClient(
        endpoint=SEARCH_ENDPOINT,
        credential=AzureKeyCredential(SEARCH_KEY)
    )
    
    try:
        index = index_client.get_index(INDEX_NAME)
        print(f"   ✓ Index found: {index.name}")
        print(f"   ✓ Fields: {len(index.fields)}")
        print(f"   ✓ Vector search configured: {index.vector_search is not None}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error verifying index: {e}")
        return False


def list_all_indexes():
    """List all indexes in the search service"""
    
    print("\n📚 All indexes in search service:")
    
    index_client = SearchIndexClient(
        endpoint=SEARCH_ENDPOINT,
        credential=AzureKeyCredential(SEARCH_KEY)
    )
    
    try:
        indexes = index_client.list_indexes()
        for idx in indexes:
            print(f"   - {idx.name}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error listing indexes: {e}")
        return False


def test_connection():
    """Test connection to Azure AI Search"""
    
    print("\n🔌 Testing connection to Azure AI Search...")
    
    try:
        index_client = SearchIndexClient(
            endpoint=SEARCH_ENDPOINT,
            credential=AzureKeyCredential(SEARCH_KEY)
        )
        
        # Try to list indexes (this will fail if credentials are wrong)
        list(index_client.list_index_names())
        
        print("   ✅ Connection successful!")
        return True
        
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print("\n💡 Tips:")
        print("   - Verify AZURE_SEARCH_ENDPOINT in .env")
        print("   - Verify AZURE_SEARCH_KEY in .env")
        print("   - Check that search service is running in Azure Portal")
        return False


def main():
    """Main setup function"""
    
    print("=" * 70)
    print("🚀 Azure RAG System Setup")
    print("=" * 70)
    
    # Test connection first
    if not test_connection():
        return
    
    # Create index
    if not create_search_index():
        return
    
    # Verify index
    if not verify_index():
        return
    
    # List all indexes
    list_all_indexes()
    
    print("\n" + "=" * 70)
    print("✅ Setup Complete!")
    print("=" * 70)
    print("\n📝 Next steps:")
    print("   1. Upload PDFs to Azure Blob Storage")
    print("   2. Run indexing script: python scripts/index_documents.py")
    print("   3. Test queries: python scripts/test_query.py")
    print("\n")


if __name__ == "__main__":
    main()