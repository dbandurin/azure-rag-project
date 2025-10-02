"""
Index Documents from Azure Blob Storage to Azure AI Search
Processes PDFs, creates embeddings, and uploads to search index
"""

from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import io
import os
from dotenv import load_dotenv
from typing import List, Dict
import time
import re

# Load environment variables
load_dotenv()

# Configuration
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "articles-index")
STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "pdf-articles")

# Chunking parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def load_embedding_model():
    """Load the sentence transformer model for embeddings"""
    print("🧮 Loading embedding model...")
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print("   ✓ Model loaded (384 dimensions)\n")
    return model


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        
        # Only add non-empty chunks
        if chunk.strip():
            chunks.append(chunk.strip())
        
        start += (chunk_size - overlap)
    
    return chunks


def extract_text_from_pdf(pdf_bytes: bytes) -> List[Dict]:
    """
    Extract text from PDF and return pages with metadata
    
    Args:
        pdf_bytes: PDF file content as bytes
        
    Returns:
        List of dicts with page text and page number
    """
    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = []
    
    for page_num, page in enumerate(pdf_reader.pages):
        text = page.extract_text()
        if text.strip():  # Only include pages with text
            pages.append({
                'text': text,
                'page_number': page_num + 1  # 1-indexed
            })
    
    return pages

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to create valid Azure Search document key"""
    # Remove .pdf extension
    name = filename.replace('.pdf', '')
    # Replace spaces and special chars with underscore
    name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    # Remove consecutive underscores
    name = re.sub(r'_+', '_', name)
    # Remove leading/trailing underscores
    name = name.strip('_')
    return name

def process_pdf(blob_name: str, pdf_bytes: bytes, embedding_model) -> List[Dict]:
    """Process a single PDF: extract text, chunk, and create embeddings"""
    print(f"   Processing: {blob_name}")
    
    pages = extract_text_from_pdf(pdf_bytes)
    print(f"      - Extracted {len(pages)} pages")
    
    documents = []
    doc_id = 0
    
    for page_info in pages:
        chunks = chunk_text(page_info['text'])
        print(f"      - Page {page_info['page_number']}: {len(chunks)} chunks")
        
        for chunk in chunks:
            if len(chunk.strip()) < 50:
                continue
                
            embedding = embedding_model.encode(chunk).tolist()
            
            doc = {
                'id': f"{sanitize_filename(blob_name)}_{page_info['page_number']}_{doc_id}",
                'content': chunk,
                'source_file': blob_name,
                'page_number': page_info['page_number'],
                'content_vector': embedding
            }
            
            documents.append(doc)
            doc_id += 1
    
    print(f"      ✓ Created {len(documents)} indexed documents\n")
    return documents


def upload_documents_batch(search_client, documents: List[Dict], batch_size: int = 100):
    """
    Upload documents to Azure AI Search in batches
    
    Args:
        search_client: Azure Search client
        documents: List of documents to upload
        batch_size: Number of documents per batch
    """
    total = len(documents)
    uploaded = 0
    
    print(f"\n📤 Uploading {total} documents in batches of {batch_size}...")
    
    for i in range(0, total, batch_size):
        batch = documents[i:i + batch_size]
        
        try:
            result = search_client.upload_documents(documents=batch)
            uploaded += len(batch)
            print(f"   ✓ Uploaded batch {i//batch_size + 1}: {uploaded}/{total} documents")
            
        except Exception as e:
            print(f"   ❌ Error uploading batch {i//batch_size + 1}: {e}")
            # Continue with next batch
    
    print(f"\n✅ Upload complete! {uploaded}/{total} documents indexed")


def index_all_pdfs():
    """Main function to index all PDFs from Blob Storage"""
    
    print("=" * 70)
    print("📚 Azure RAG Document Indexing")
    print("=" * 70)
    print()
    
    # Validate configuration
    if not all([SEARCH_ENDPOINT, SEARCH_KEY, STORAGE_CONNECTION_STRING]):
        print("❌ Error: Missing required environment variables")
        print("   Required: AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, AZURE_STORAGE_CONNECTION_STRING")
        return
    
    print(f"📋 Configuration:")
    print(f"   Search Endpoint: {SEARCH_ENDPOINT}")
    print(f"   Index Name: {INDEX_NAME}")
    print(f"   Storage Container: {CONTAINER_NAME}")
    print()
    
    # Initialize clients
    print("🔌 Connecting to Azure services...")
    
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_KEY)
    )
    
    print("   ✓ Connected to Blob Storage")
    print("   ✓ Connected to AI Search")
    print()
    
    # Load embedding model
    embedding_model = load_embedding_model()
    
    # List all PDFs in container
    print("📂 Listing PDFs in container...")
    blobs = list(container_client.list_blobs())
    pdf_blobs = [b for b in blobs if b.name.endswith('.pdf')]
    
    if not pdf_blobs:
        print("⚠️  No PDF files found in container!")
        print(f"   Please upload PDFs to: {CONTAINER_NAME}")
        return
    
    print(f"   Found {len(pdf_blobs)} PDF files:")
    for blob in pdf_blobs:
        size_mb = blob.size / (1024 * 1024)
        print(f"   - {blob.name} ({size_mb:.2f} MB)")
    print()
    
    # Process each PDF
    all_documents = []
    start_time = time.time()
    
    print("🔄 Processing PDFs...")
    print()
    
    for i, blob in enumerate(pdf_blobs, 1):
        print(f"📄 [{i}/{len(pdf_blobs)}] {blob.name}")
        
        try:
            # Download PDF
            blob_client = container_client.get_blob_client(blob.name)
            pdf_bytes = blob_client.download_blob().readall()
            
            # Process PDF
            documents = process_pdf(blob.name, pdf_bytes, embedding_model)
            all_documents.extend(documents)
            
        except Exception as e:
            print(f"   ❌ Error processing {blob.name}: {e}\n")
            continue
    
    # Upload all documents
    if all_documents:
        upload_documents_batch(search_client, all_documents)
    else:
        print("⚠️  No documents to upload!")
        return
    
    # Summary
    elapsed_time = time.time() - start_time
    print()
    print("=" * 70)
    print("📊 Indexing Summary")
    print("=" * 70)
    print(f"   PDFs processed: {len(pdf_blobs)}")
    print(f"   Total chunks indexed: {len(all_documents)}")
    print(f"   Time elapsed: {elapsed_time:.2f} seconds")
    print(f"   Avg time per PDF: {elapsed_time/len(pdf_blobs):.2f} seconds")
    print()
    print("✅ Indexing complete! Your RAG system is ready.")
    print()
    print("💡 Next steps:")
    print("   - Test queries: python scripts/test_query.py")
    print("   - Or run: python src/query.py")
    print("=" * 70)


def get_index_stats():
    """Get statistics about the current index"""
    
    print("\n📊 Index Statistics")
    print("-" * 70)
    
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_KEY)
    )
    
    try:
        # Count total documents
        results = search_client.search(search_text="*", include_total_count=True)
        total_docs = results.get_count()
        
        print(f"   Total indexed documents: {total_docs}")
        
        # Get unique source files
        results = search_client.search(
            search_text="*",
            select=["source_file"],
            top=1000
        )
        
        sources = set()
        for result in results:
            sources.add(result.get('source_file', 'Unknown'))
        
        print(f"   Unique PDF files: {len(sources)}")
        print(f"\n   Files:")
        for source in sorted(sources):
            print(f"      - {source}")
        
    except Exception as e:
        print(f"   ❌ Error getting stats: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        # Show stats only
        get_index_stats()
    else:
        # Run full indexing
        index_all_pdfs()
        
        # Show final stats
        get_index_stats()