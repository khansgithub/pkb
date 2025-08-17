from app.app_logging import logger
import hashlib

import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoModel, AutoTokenizer
import torch

tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
model = AutoModel.from_pretrained("microsoft/codebert-base")

embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")



def embed_text_old(input_str: str) -> np.ndarray:
    hashed: bytes = hashlib.sha256(input_str.encode()).digest()
    vec = np.frombuffer(hashed, dtype=np.uint8).astype(np.float32)[:64]
    return vec / np.linalg.norm(vec)


def embed_text(input: str) -> np.ndarray:
    return np.asarray(embedder.embed_query(input))

def embed_text_bert(input: str) -> np.ndarray:
    logger.debug(f"{input=}")
    inputs: dict[str, torch.Tensor] = tokenizer(input, padding=True, truncation=True, return_tensors="pt")

    with torch.no_grad():
        outputs = model(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"])
        last_hidden_states = outputs.last_hidden_state  # shape: (batch_size, seq_len, hidden_size)

    # Mean pooling
    # attention_mask = inputs['attention_mask']
    attention_mask = inputs['attention_mask'].unsqueeze(-1)
    masked_hidden = last_hidden_states * attention_mask
    sentence_embeddings = masked_hidden.sum(dim=1) / attention_mask.sum(dim=1)
    # embeddings = (last_hidden_states * attention_mask.unsqueeze(-1)).sum(dim=1) / attention_mask.sum(dim=1, keepdim=True)
    embeddings_np = sentence_embeddings.cpu().numpy()
    embeddings_np = embeddings_np.squeeze(0)
    return embeddings_np


