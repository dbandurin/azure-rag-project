#Upload PDFs to Azure Blob Storage

"""
Upload PDFs to Azure Blob Storage
"""

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Configuration
CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "pdf-articles")
PDF_FOLDER = "./pdfs"


def create_container_if_not_exists(blob_service_client, container_name):
    """Create container if it doesn't exist"""
    try:
        container_client = blob_service_client.create_container(container_name)
        print(f"✓ Created container: {container_name}")
        return container_client
    except Exception as e:
        if "ContainerAlreadyExists" in str(e):
            print(f"✓ Container already exists: {container_name}")
            return blob_service_client.get_container_client(container_name)
        else:
            raise e


def upload_pdfs(pdf_folder=PDF_FOLDER):
    """
    Upload all PDFs from local folder to Azure Blob Storage
    
    Args:
        pdf_folder: Path to folder containing PDF files
    """
    
    print("=" * 70)
    print("📤 Upload PDFs to Azure Blob Storage")
    print("=" * 70)
    print()
    
    # Validate configuration
    if not CONNECTION_STRING:
        print("❌ Error: AZURE_STORAGE_CONNECTION_STRING not set in .env")
        return
    
    print(f"📋 Configuration:")
    print(f"   Container: {CONTAINER_NAME}")
    print(f"   Local folder: {pdf_folder}")
    print()
    
    # Check if folder exists
    if not os.path.exists(pdf_folder):
        print(f"❌ Error: Folder '{pdf_folder}' does not exist")
        return
    
    # Get list of PDF files
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"⚠️  No PDF files found in '{pdf_folder}'")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF files:")
    for i, filename in enumerate(pdf_files, 1):
        size_mb = os.path.getsize(os.path.join(pdf_folder, filename)) / (1024 * 1024)
        print(f"   {i}. {filename} ({size_mb:.2f} MB)")
    print()
    
    # Connect to storage
    print("🔌 Connecting to Azure Blob Storage...")
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    print("   ✓ Connected")
    print()
    
    # Create container if needed
    container_client = create_container_if_not_exists(blob_service_client, CONTAINER_NAME)
    print()
    
    # Upload each PDF
    print("📤 Uploading files...")
    print()
    
    uploaded = 0
    skipped = 0
    errors = 0
    
    for i, filename in enumerate(pdf_files, 1):
        filepath = os.path.join(pdf_folder, filename)
        blob_client = container_client.get_blob_client(filename)
        
        try:
            print(f"[{i}/{len(pdf_files)}] Uploading: {filename}")
            
            # Check if blob already exists
            if blob_client.exists():
                print(f"   ⚠️  File already exists, overwriting...")
            
            # Upload file
            with open(filepath, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            
            print(f"   ✓ Uploaded successfully\n")
            uploaded += 1
            
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
            errors += 1
    
    # Summary
    print("=" * 70)
    print("📊 Upload Summary")
    print("=" * 70)
    print(f"   Total files: {len(pdf_files)}")
    print(f"   Uploaded: {uploaded}")
    print(f"   Errors: {errors}")
    print()
    
    if uploaded > 0:
        print("✅ Upload complete!")
        print()
        print("💡 Next steps:")
        print("   1. Run indexing: python scripts/index_documents.py")
        print("   2. Or use: python index_documents.py")
    
    print("=" * 70)


def list_blobs():
    """List all blobs in the container"""
    
    print("\n📚 Files in Azure Blob Storage:")
    print("-" * 70)
    
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    
    try:
        blobs = list(container_client.list_blobs())
        
        if not blobs:
            print("   (No files found)")
        else:
            for i, blob in enumerate(blobs, 1):
                size_mb = blob.size / (1024 * 1024)
                print(f"   {i}. {blob.name} ({size_mb:.2f} MB)")
        
        print(f"\nTotal: {len(blobs)} files")
        
    except Exception as e:
        print(f"❌ Error listing blobs: {e}")


def delete_blob(filename):
    """Delete a specific blob"""
    
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    
    try:
        blob_client = container_client.get_blob_client(filename)
        blob_client.delete_blob()
        print(f"✓ Deleted: {filename}")
        
    except Exception as e:
        print(f"❌ Error deleting {filename}: {e}")


def delete_all_blobs():
    """Delete all blobs in container (use with caution!)"""
    
    response = input("⚠️  Delete ALL files? This cannot be undone! (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return
    
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    
    try:
        blobs = list(container_client.list_blobs())
        
        for blob in blobs:
            blob_client = container_client.get_blob_client(blob.name)
            blob_client.delete_blob()
            print(f"✓ Deleted: {blob.name}")
        
        print(f"\n✅ Deleted {len(blobs)} files")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_blobs()
        elif command == "delete" and len(sys.argv) > 2:
            delete_blob(sys.argv[2])
        elif command == "delete-all":
            delete_all_blobs()
        else:
            print("Usage:")
            print("  python files_upload.py           # Upload PDFs")
            print("  python files_upload.py list      # List uploaded files")
            print("  python files_upload.py delete <filename>  # Delete a file")
            print("  python files_upload.py delete-all  # Delete all files")
    else:
        # Default: upload PDFs
        upload_pdfs()