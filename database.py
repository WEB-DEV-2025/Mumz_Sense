import chromadb
import os
from chromadb.utils import embedding_functions

# Define the local path for ChromaDB
DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

# Initialize the ChromaDB client
client = chromadb.PersistentClient(path=DB_DIR)

# Use local sentence-transformer model (Fast, free, no API key needed)
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

def get_catalog_db():
    """Collection for Mumzworld products."""
    return client.get_or_create_collection(
        name="mumz_catalog",
        embedding_function=embedding_func
    )

def get_safety_db():
    """Collection for GCC/General Pediatric Safety Policies."""
    return client.get_or_create_collection(
        name="safety_policies",
        embedding_function=embedding_func
    )

def query_products(milestone_text: str, n_results: int = 3):
    """Queries the catalog and returns a clean list of product dictionaries."""
    collection = get_catalog_db()
    raw_results = collection.query(
        query_texts=[milestone_text],
        n_results=n_results
    )
    
    # Clean up ChromaDB's nested list output into a friendly format for our Agent
    formatted_products = []
    if raw_results['ids'] and len(raw_results['ids']) > 0:
        for i in range(len(raw_results['ids'][0])):
            product = {
                "id": raw_results['ids'][0][i],
                "description": raw_results['documents'][0][i],
                "metadata": raw_results['metadatas'][0][i] if raw_results['metadatas'] else {}
            }
            formatted_products.append(product)
            
    return formatted_products

def query_safety_rules(product_description: str, n_results: int = 2):
    """Queries safety policies relevant to a specific product description."""
    collection = get_safety_db()
    raw_results = collection.query(
        query_texts=[product_description],
        n_results=n_results
    )
    
    rules = []
    if raw_results['documents'] and len(raw_results['documents']) > 0:
        rules = raw_results['documents'][0]
    return rules