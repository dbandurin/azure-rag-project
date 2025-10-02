"""
Query Module for Azure RAG System
Handles vector search and LLM response generation
"""

from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from langchain_anthropic import ChatAnthropic
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
from typing import Dict, List

# Load environment variables
load_dotenv()

# Configuration
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "articles-index")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Initialize global clients (lazy loading)
_embedding_model = None
_search_client = None
_llm = None


def get_embedding_model():
    """Lazy load embedding model"""
    global _embedding_model
    if _embedding_model is None:
        print("Loading embedding model...")
        _embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return _embedding_model


def get_search_client():
    """Lazy load search client"""
    global _search_client
    if _search_client is None:
        _search_client = SearchClient(
            endpoint=SEARCH_ENDPOINT,
            index_name=INDEX_NAME,
            credential=AzureKeyCredential(SEARCH_KEY)
        )
    return _search_client


def get_llm():
    """Lazy load Claude LLM"""
    global _llm
    if _llm is None:
        _llm = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",
            temperature=0,
            anthropic_api_key=ANTHROPIC_API_KEY
        )
    return _llm


def query_azure_rag(question: str, top_k: int = 4, verbose: bool = True) -> Dict:
    """
    Query Azure AI Search RAG system
    
    Args:
        question: User's question
        top_k: Number of chunks to retrieve
        verbose: Print search details
        
    Returns:
        dict: Result with 'answer', 'sources', 'num_chunks', 'chunks'
    """
    
    if verbose:
        print(f"\n🔍 Searching for: '{question}'")
        print(f"   Retrieving top {top_k} chunks...\n")
    
    # Get clients
    embedding_model = get_embedding_model()
    search_client = get_search_client()
    llm = get_llm()
    
    # Generate query embedding
    query_embedding = embedding_model.encode(question).tolist()
    
    # Vector search in Azure AI Search
    results = search_client.search(
        search_text=None,  # Pure vector search
        vector_queries=[{
            "vector": query_embedding,
            "k_nearest_neighbors": top_k,
            "fields": "content_vector"
        }],
        select=["content", "source_file", "page_number", "chunk_id"]
    )
    
    # Gather context
    context_chunks = []
    sources = set()
    retrieved_chunks = []
    
    for result in results:
        content = result.get('content', '')
        source = result.get('source_file', 'Unknown')
        page = result.get('page_number', 0)
        
        context_chunks.append(content)
        sources.add(source)
        retrieved_chunks.append({
            'content': content,
            'source': source,
            'page': page
        })
        
        if verbose:
            print(f"📄 {source} (page {page})")
            print(f"   {content[:100]}...")
            print()
    
    # Combine context
    context = "\n\n---\n\n".join(context_chunks)
    
    # Create prompt for Claude
    prompt = f"""You are helping the user explore their written articles.
Use the following context from their articles to answer the question thoughtfully.

Guidelines:
- If you reference specific information, mention which article it comes from
- If you're not certain about something, say so honestly
- Provide detailed, helpful answers based on the context
- If the context doesn't contain relevant information, say so

Context from articles:
{context}

Question: {question}

Answer:"""
    
    if verbose:
        print("🤖 Generating answer with Claude...\n")
    
    # Query Claude
    answer = llm.invoke(prompt).content
    
    return {
        'answer': answer,
        'sources': list(sources),
        'num_chunks': len(context_chunks),
        'chunks': retrieved_chunks
    }


def query_with_hybrid_search(question: str, top_k: int = 4, verbose: bool = True) -> Dict:
    """
    Query using hybrid search (vector + keyword)
    
    Args:
        question: User's question
        top_k: Number of chunks to retrieve
        verbose: Print search details
        
    Returns:
        dict: Result with 'answer', 'sources', 'num_chunks'
    """
    
    if verbose:
        print(f"\n🔍 Hybrid search for: '{question}'")
        print(f"   Using both vector and keyword search...\n")
    
    # Get clients
    embedding_model = get_embedding_model()
    search_client = get_search_client()
    llm = get_llm()
    
    # Generate query embedding
    query_embedding = embedding_model.encode(question).tolist()
    
    # Hybrid search (vector + text)
    results = search_client.search(
        search_text=question,  # Keyword search
        vector_queries=[{
            "vector": query_embedding,
            "k_nearest_neighbors": top_k,
            "fields": "content_vector"
        }],
        select=["content", "source_file", "page_number"],
        top=top_k
    )
    
    # Process results (same as pure vector search)
    context_chunks = []
    sources = set()
    
    for result in results:
        content = result.get('content', '')
        source = result.get('source_file', 'Unknown')
        
        context_chunks.append(content)
        sources.add(source)
        
        if verbose:
            print(f"📄 {source}")
            print(f"   {content[:100]}...")
            print()
    
    context = "\n\n---\n\n".join(context_chunks)
    
    # Query Claude
    prompt = f"""You are helping the user explore their written articles.
Use the following context to answer the question.

Context from articles:
{context}

Question: {question}

Answer:"""
    
    if verbose:
        print("🤖 Generating answer...\n")
    
    answer = llm.invoke(prompt).content
    
    return {
        'answer': answer,
        'sources': list(sources),
        'num_chunks': len(context_chunks)
    }


def interactive_query():
    """Interactive CLI for querying the RAG system"""
    
    print("=" * 70)
    print("💬 Azure RAG Query Interface")
    print("=" * 70)
    print("\nAsk questions about your articles, or type 'quit' to exit")
    print("\nCommands:")
    print("  'quit' or 'exit' - Exit the program")
    print("  'hybrid: <question>' - Use hybrid search instead of pure vector")
    print("\nExample questions:")
    print("  - What did I write about machine learning?")
    print("  - Summarize my thoughts on startups")
    print("  - What tools or frameworks did I mention?")
    print("=" * 70 + "\n")
    
    while True:
        try:
            question = input("You: ").strip()
            
            # Exit commands
            if question.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not question:
                continue
            
            # Check for hybrid search
            use_hybrid = False
            if question.lower().startswith('hybrid:'):
                use_hybrid = True
                question = question[7:].strip()
            
            print()
            
            # Query the system
            if use_hybrid:
                result = query_with_hybrid_search(question)
            else:
                result = query_azure_rag(question)
            
            # Display answer
            print("-" * 70)
            print(f"💡 Answer:\n")
            print(result['answer'])
            print()
            
            # Display metadata
            print("-" * 70)
            print(f"📊 Retrieved {result['num_chunks']} chunks from {len(result['sources'])} file(s)")
            if result['sources']:
                print(f"📚 Sources: {', '.join(result['sources'])}")
            print("-" * 70)
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            print("Please try again.\n")


if __name__ == "__main__":
    interactive_query()