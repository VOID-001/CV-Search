import numpy as np

def normalize(embedding):
    embeddings = np.array(embedding)
    norm = np.linalg.norm(embeddings)
    return embedding / norm if norm != 0 else embedding

def process_embeddings(embeddings):
    combined_embedding = np.mean(embeddings, axis=0)
    normalized_embedding = normalize(combined_embedding)
    return normalized_embedding