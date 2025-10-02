from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexer,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataContainer
)

# Create data source
data_source = SearchIndexerDataSourceConnection(
    name="pdf-datasource",
    type="azureblob",
    connection_string=blob_connection_string,
    container=SearchIndexerDataContainer(name="pdf-articles")
)

indexer_client = SearchIndexerClient(search_endpoint, AzureKeyCredential(search_key))
indexer_client.create_or_update_data_source_connection(data_source)

# Create indexer (automatically processes PDFs)
indexer = SearchIndexer(
    name="pdf-indexer",
    data_source_name="pdf-datasource",
    target_index_name=index_name
)

indexer_client.create_or_update_indexer(indexer)