#Upload PDFs to Azure Blob Storage

from azure.storage.blob import BlobServiceClient

# Connect to storage
connection_string = "your_connection_string"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# Create container
container_client = blob_service_client.create_container("pdf-articles")

# Upload PDFs
import os
pdf_folder = "./pdfs"
for filename in os.listdir(pdf_folder):
    if filename.endswith('.pdf'):
        blob_client = container_client.get_blob_client(filename)
        with open(os.path.join(pdf_folder, filename), "rb") as data:
            
            blob_client.upload_blob(data, overwrite=True)