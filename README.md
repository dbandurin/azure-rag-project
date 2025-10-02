# Azure RAG System for Personal Articles

A production-ready Retrieval-Augmented Generation (RAG) system built on Azure Cloud for querying personal articles and documents.

## 🏗️ Architecture

- **Vector Database**: Azure AI Search with HNSW algorithm
- **Document Storage**: Azure Blob Storage
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2, 384 dimensions)
- **LLM**: Claude Sonnet 4.5 via Anthropic API
- **Deployment**: Azure Functions (serverless API)

## 📋 Prerequisites

- Python 3.9+
- Azure Subscription
- Anthropic API Key
- Azure CLI (for setup)

## 🚀 Quick Start

### 1. Clone and Setup Virtual Environment

```bash
# Clone repository
git clone <your-repo>
cd azure-rag-project

# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Create Azure Resources

```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-rag-system --location eastus

# Create AI Search service
az search service create \
  --name srch-articles-rag \
  --resource-group rg-rag-system \
  --location eastus \
  --sku basic

# Create Storage Account
az storage account create \
  --name stragdocsrag \
  --resource-group rg-rag-system \
  --location eastus \
  --sku Standard_LRS

# Get credentials
az search admin-key show \
  --resource-group rg-rag-system \
  --service-name srch-articles-rag

az storage account show-connection-string \
  --name stragdocsrag \
  --resource-group rg-rag-system
```

### 3. Configure Environment Variables

Create `.env` file in project root:

```bash
# Azure Search
AZURE_SEARCH_ENDPOINT=https://srch-articles-rag.search.windows.net
AZURE_SEARCH_KEY=your-admin-key-here
AZURE_SEARCH_INDEX_NAME=articles-index

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_STORAGE_CONTAINER_NAME=pdf-articles

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-your-api-key

# Resource Info
AZURE_RESOURCE_GROUP=rg-rag-system
AZURE_LOCATION=eastus
```

### 4. Setup and Index Documents

```bash
# Verify setup
python test_setup.py

# Create search index
python scripts/create_ai_search.py

# Upload PDFs to blob storage
python scripts/files_upload.py

# Index documents (extract text, create embeddings, upload to search)
python scripts/index_documents.py
```

### 5. Query Your Articles

```bash
# Interactive query mode
python src/query.py

# Run test queries
python scripts/test_query.py test

# Single query
python scripts/test_query.py "What did I write about AI?"

# Hybrid search
python scripts/test_query.py hybrid "Summarize my articles"
```

## 📁 Project Structure

```
azure-rag-project/
├── venv/                       # Virtual environment
├── .env                        # Environment variables (not in git)
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── scripts/                   # Setup and utility scripts
│   ├── create_ai_search.py   # Create Azure AI Search index
│   ├── files_upload.py       # Upload PDFs to blob storage
│   ├── index_documents.py    # Process and index documents
│   └── test_query.py         # Test query functionality
│
├── src/                       # Core application code
│   ├── query.py              # Query and RAG logic
│   ├── function_app.py       # Azure Functions API
│   └── indexer.py            # Indexing utilities
│
├── tests/                     # Test files
│   └── test_setup.py         # Setup verification
│
├── pdfs/                      # Local PDFs for upload
│   └── (your-articles.pdf)
│
└── notebooks/                 # Jupyter notebooks
    └── exploration.ipynb     # Experimentation
```

## 🔧 Available Scripts

### Upload PDFs
```bash
# Upload all PDFs from ./pdfs folder
python scripts/files_upload.py

# List uploaded files
python scripts/files_upload.py list

# Delete a specific file
python scripts/files_upload.py delete filename.pdf

# Delete all files (careful!)
python scripts/files_upload.py delete-all
```

### Indexing
```bash
# Index all documents
python scripts/index_documents.py

This will:
- Download PDFs from Blob Storage
- Extract text from each page
- Chunk the text
- Generate embeddings (384-dim vectors)
- Upload to Azure AI Search

# Show index statistics
python scripts/index_documents.py stats
```

### Querying
```bash
# Interactive mode
python src/query.py

# Test mode (predefined queries)
python scripts/test_query.py test

# Single query
python scripts/test_query.py "Your question here"

# Hybrid search (vector + keyword)
python scripts/test_query.py hybrid "Your question"

# Test search only (no LLM call)
python scripts/test_query.py search "Your question"

# Interactive test mode
python scripts/test_query.py interactive
```

## 🌐 API Deployment (Azure Functions)

### Deploy to Azure Functions

```bash
# Create Function App
az functionapp create \
  --resource-group rg-rag-system \
  --name func-rag-query \
  --storage-account stragdocsrag \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.10 \
  --functions-version 4

# Deploy
func azure functionapp publish func-rag-query
```

### API Usage

```bash
# Query endpoint
POST https://func-rag-query.azurewebsites.net/api/query

# Request body
{
  "question": "What did I write about machine learning?"
}

# Response
{
  "answer": "Based on your articles...",
  "sources": ["article1.pdf", "article2.pdf"],
  "num_chunks": 4
}
```

## 📊 Features

- ✅ Vector similarity search using Azure AI Search
- ✅ Hybrid search (vector + keyword)
- ✅ Automatic PDF text extraction
- ✅ Intelligent text chunking with overlap
- ✅ Source attribution (which article, which page)
- ✅ Interactive CLI for querying
- ✅ Batch document processing
- ✅ RESTful API via Azure Functions
- ✅ Environment-based configuration

## 🔒 Security Best Practices

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Use Azure Key Vault** for production secrets
3. **Enable Azure AD authentication** for API endpoints
4. **Restrict network access** to Azure resources
5. **Rotate API keys** regularly

## 💰 Cost Estimation

**Development/Testing:**
- Azure AI Search (Basic): ~$75/month
- Blob Storage: ~$0.02/GB/month
- Azure Functions: First 1M executions free
- **Total**: ~$80-100/month

**Production:**
- Azure AI Search (Standard): ~$250/month
- Consider reserved capacity for cost savings

## 🐛 Troubleshooting

### Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Azure Connection Issues
```bash
# Test Azure credentials
python test_setup.py

# Verify search service is running
az search service show --name srch-articles-rag --resource-group rg-rag-system
```

### Embedding Model Not Found
```bash
# The model will auto-download on first run
# Ensure you have internet connection
# Model size: ~80MB
```

### No Results from Search
```bash
# Check if documents are indexed
python scripts/index_documents.py stats

# Re-index if needed
python scripts/index_documents.py
```

## 📚 Additional Resources

- [Azure AI Search Documentation](https://docs.microsoft.com/en-us/azure/search/)
- [Azure Functions Python Guide](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Sentence Transformers](https://www.sbert.net/)
- [Anthropic Claude API](https://docs.anthropic.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details
