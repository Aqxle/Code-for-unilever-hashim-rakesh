import json
import faiss
import numpy as np
import requests

def load_faiss_index(index_path="vector_database.index", metadata_path="metadata.json"):
    """
    Loads the FAISS index and metadata from disk.

    Args:
        index_path (str): Path to the FAISS index file.
        metadata_path (str): Path to the metadata JSON file.

    Returns:
        faiss.IndexFlatL2, List[str]: The FAISS index and corresponding metadata (company names).
    """
    index = faiss.read_index(index_path)
    with open(metadata_path, "r") as f:
        company_names = json.load(f)
    return index, company_names

def get_ollama_embedding(query: str, model: str = "nomic-embed-text"):
    """
    Generates an embedding for the given query using Ollama's direct API.

    Args:
        query (str): The input text to embed.
        model (str): The embedding model to use.

    Returns:
        np.ndarray: The embedding vector.
    """
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": model, "prompt": query}
    )
    response_data = response.json()
    return np.array([response_data["embedding"]])

def search_similar(query: str, top_k: int = 10, index_path="vector_database.index", metadata_path="metadata.json"):
    """
    Searches for the top_k most similar company descriptions in the FAISS vector database.

    Args:
        query (str): Input string (company name or company name + short description).
        top_k (int): Number of results to return.
        index_path (str): Path to the FAISS index file.
        metadata_path (str): Path to the metadata JSON file.

    Returns:
        List of tuples containing (company_name, similarity_score).
    """
    # Load FAISS Index and Metadata
    index, company_names = load_faiss_index(index_path, metadata_path)

    # Generate query embedding using Ollama API
    query_embedding = get_ollama_embedding(query)

    # Search for the top_k most similar embeddings
    distances, indices = index.search(query_embedding, top_k)

    # Retrieve matching company names
    results = [(company_names[i], distances[0][j]) for j, i in enumerate(indices[0])]

    return results

query_text = "what is the spend by whisper"
top_k_results = 10  

# Run search
results = search_similar(query_text, top_k_results)

# Display Results
print("\nTop Similar Companies:")
for name, score in results:
    print(f"{name} - Similarity Score: {score:.4f}")
