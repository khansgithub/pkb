import hashlib

import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings

embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def embed_text_old(input_str: str) -> np.ndarray:
    hashed: bytes = hashlib.sha256(input_str.encode()).digest()
    vec = np.frombuffer(hashed, dtype=np.uint8).astype(np.float32)[:64]
    return vec / np.linalg.norm(vec)


def embed_text(input: str) -> np.ndarray:
    return np.asarray(embedder.embed_query(input))
