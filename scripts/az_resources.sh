 az login

#Create Resource group
az group create --name rg-rag-system --location eastus

#Create storage account
az storage account create   --name stragdocs   --resource-group rg-rag-system   --location eastus   --sku Standard_LRS

#Create AI Search 
az search service create   --name srch-articles-rag   --resource-group rg-rag-system   --location eastus   --sku basic


# Check your search service status
az search service show \
  --name srch-articles-rag \
  --resource-group rg-rag-system \
  --query "{name:name, status:status, sku:sku.name, location:location}"

# List all search services in your resource group
az search service list \
  --resource-group rg-rag-system \
  --output table