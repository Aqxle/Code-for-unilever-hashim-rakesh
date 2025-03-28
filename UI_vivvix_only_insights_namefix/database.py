import json
import faiss
import numpy as np
import requests
from tqdm import tqdm

# Load JSON Data
with open("companies_summaries_full.json", "r") as file:
    data = json.load(file)

# Extract keys and values
company_names = list(data.keys())
descriptions = list(data.values())

# Concatenate company name and description before embedding
full_texts = [f"{name}: {desc}" for name, desc in zip(company_names, descriptions)]
print(f"Processing {len(full_texts)} entries...")

# Function to get embeddings from Ollama API
def get_embedding(text):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text}
    )
    response.raise_for_status()
    return response.json()["embedding"]

# Generate embeddings with tqdm progress bar
embeddings = np.array([get_embedding(text) for text in tqdm(full_texts, desc="Generating Embeddings")])

# Create FAISS Index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)  # L2 (Euclidean) distance
index.add(embeddings)  # Add embeddings to the index

# Save FAISS Index and metadata
faiss.write_index(index, "vector_database.index")
with open("metadata.json", "w") as f:
    json.dump(company_names, f)

print("Vector database saved successfully.")
