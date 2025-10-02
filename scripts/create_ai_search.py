# Create Azure AI Search Index

from azure.search.documents import SearchClient
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

import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT') 
search_key = os.getenv('AZURE_SEARCH_KEY')
index_name = "articles-index"

# Create index with vector search
index_client = SearchIndexClient(
    endpoint=search_endpoint,
    credential=AzureKeyCredential(search_key)
)

# Define index schema
fields = [
    SearchField(name="id", type=SearchFieldDataType.String, key=True),
    SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
    SearchField(name="source_file", type=SearchFieldDataType.String, filterable=True),
    SearchField(name="page_number", type=SearchFieldDataType.Int32, filterable=True),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=384,  # all-MiniLM-L6-v2 dimension
        vector_search_profile_name="vector-profile"
    ),
]

# Configure vector search
vector_search = VectorSearch(
    profiles=[
        VectorSearchProfile(
            name="vector-profile",
            algorithm_configuration_name="hnsw-config"
        )
    ],
    algorithms=[
        HnswAlgorithmConfiguration(name="hnsw-config")
    ],
)

# Create the index
index = SearchIndex(
    name=index_name,
    fields=fields,
    vector_search=vector_search
)

index_client.create_or_update_index(index)