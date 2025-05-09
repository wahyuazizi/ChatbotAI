import os
from langchain_community.vectorstores import Qdrant
from langchain_openai import AzureOpenAIEmbeddings
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader

from qdrant_client import QdrantClient, models

from decouple import config

# Get configuration from .env file
qdrant_api_key = config("QDRANT_API_KEY")
qdrant_url = config("QDRANT_URL")
azure_openai_api_key = config("AZURE_OPENAI_API_KEY")
azure_openai_endpoint = config("AZURE_OPENAI_ENDPOINT")
collection_name = "Websites"

# Print the OpenAI package version to help diagnose
import openai
print(f"OpenAI package version: {openai.__version__}")

# Initialize Qdrant client
client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key
)

# Try different initialization approaches for AzureOpenAI
try:
    # Approach 1: Try with azure_endpoint
    print("Trying initialization with azure_endpoint...")
    azure_openai_client = AzureOpenAI(
        api_version="2024-02-01",
        azure_endpoint=azure_openai_endpoint,
        api_key=azure_openai_api_key
    )
    print("AzureOpenAI client initialized successfully with azure_endpoint")
except Exception as e1:
    print(f"Error with approach 1: {e1}")
    try:
        # Approach 2: Try with base_url
        print("Trying initialization with base_url...")
        azure_openai_client = AzureOpenAI(
            api_version="2024-02-01",
            base_url=f"{azure_openai_endpoint}/openai/deployments/text-embedding-3-small",
            api_key=azure_openai_api_key
        )
        print("AzureOpenAI client initialized successfully with base_url")
    except Exception as e2:
        print(f"Error with approach 2: {e2}")
        # Final attempt with alternate approach
        print("Using alternative approach with direct client initialization...")
        # Set environment variables for Azure OpenAI
        os.environ["AZURE_OPENAI_API_KEY"] = azure_openai_api_key
        os.environ["AZURE_OPENAI_ENDPOINT"] = azure_openai_endpoint

        # Initialize with environment variables
        azure_openai_client = AzureOpenAI()
        print("AzureOpenAI client initialized from environment variables")

# Initialize AzureOpenAIEmbeddings for LangChain
embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-small",
    openai_api_version="2024-02-01",
    azure_endpoint=azure_openai_endpoint,
    api_key=azure_openai_api_key
)

def get_embeddings(input_texts):
    """Generate embeddings using Azure OpenAI service."""
    print(f"Generating embeddings for {len(input_texts)} texts")
    try:
        response = azure_openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=input_texts,
        )
        print("Embeddings generated successfully")
        return [item.embedding for item in response.data]
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        # Fallback to using LangChain embeddings
        print("Falling back to LangChain embeddings")
        return embeddings.embed_documents(input_texts)

def create_collection(collection_name):
    """Create or recreate the Qdrant collection."""
    print(f"Creating collection {collection_name}...")
    try:
        # Check if collection exists and delete if it does
        if client.collection_exists(collection_name):
            print(f"Collection {collection_name} exists, deleting...")
            client.delete_collection(collection_name)
        
        # Create the collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=1536,  # Dimensions for text-embedding-3-small
                distance=models.Distance.COSINE,
            )
        )
        print(f"Collection {collection_name} created successfully")
    except Exception as e:
        print(f"Error creating collection: {e}")
        raise

def upload_website_to_collection(url):
    """Scrape website, create embeddings, and upload to Qdrant."""
    print(f"Loading content from {url}...")
    try:
        # Load the website content
        loader = WebBaseLoader(url)
        docs = loader.load()
        print(f"Loaded {len(docs)} documents from {url}")
        
        # Split documents into chunks
        docs = text_splitter.split_documents(docs)
        print(f"Split into {len(docs)} chunks")
        
        # Add metadata
        for doc in docs:
            doc.metadata = {"source_url": url}
        
        # Get text content to embed
        text_list = [doc.page_content for doc in docs]
        
        # Generate embeddings
        embeddings_list = get_embeddings(text_list)
        
        # Create vectors for Qdrant
        vectors = []
        for i, (doc, emb) in enumerate(zip(docs, embeddings_list)):
            vectors.append(
                models.PointStruct(
                    id=i,
                    vector=emb,
                    payload={"text": doc.page_content, "metadata": doc.metadata}
                )
            )
        
        # Upload vectors to Qdrant
        print(f"Uploading {len(vectors)} vectors to Qdrant...")
        client.upsert(
            collection_name=collection_name,
            points=vectors
        )
        
        print(f"Website {url} uploaded to collection {collection_name}")
    except Exception as e:
        print(f"Error uploading website: {e}")
        raise

# Set up text splitter for chunking documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)

if __name__ == "__main__":
    try:
        create_collection(collection_name)
        upload_website_to_collection("https://ft.hamzanwadi.ac.id/in/")
        print("Process completed successfully!")
    except Exception as e:
        print(f"Process failed with error: {e}")