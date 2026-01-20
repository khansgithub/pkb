import hashlib

import numpy as np

from app.app_logging import logger


def embed_text_old(input_str: str) -> np.ndarray:
    """
    Always-available tiny embedding (hash-based). Not semantic, but stable.
    """
    hashed: bytes = hashlib.sha256(input_str.encode("utf-8")).digest()
    vec = np.frombuffer(hashed, dtype=np.uint8).astype(np.float32)[:64]
    return vec / np.linalg.norm(vec)


def embed_text(input: str) -> np.ndarray:
    """
    Optional semantic embedding using langchain + HuggingFace.
    """
    try:
        from langchain_huggingface import HuggingFaceEmbeddings  # type: ignore

        embedder = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        return np.asarray(embedder.embed_query(input))
    except Exception as e:
        raise RuntimeError(
            "Optional dependency missing for embed_text(). "
            "Install langchain_huggingface + its dependencies, or use embed_text_old()."
        ) from e


def embed_text_bert(input: str) -> np.ndarray:
    """
    Optional BERT embedding (CodeBERT). Heavy deps (torch/transformers).
    """
    try:
        import torch  # type: ignore
        from transformers import AutoModel, AutoTokenizer  # type: ignore

        tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
        model = AutoModel.from_pretrained("microsoft/codebert-base")

        logger.debug(f"{input=}")
        inputs: dict[str, torch.Tensor] = tokenizer(
            input, padding=True, truncation=True, return_tensors="pt"
        )

        with torch.no_grad():
            outputs = model(
                input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"]
            )
            last_hidden_states = outputs.last_hidden_state

        attention_mask = inputs["attention_mask"].unsqueeze(-1)
        masked_hidden = last_hidden_states * attention_mask
        sentence_embeddings = masked_hidden.sum(dim=1) / attention_mask.sum(dim=1)
        embeddings_np = sentence_embeddings.cpu().numpy().squeeze(0)
        return embeddings_np
    except Exception as e:
        raise RuntimeError(
            "Optional dependency missing for embed_text_bert(). "
            "Install torch + transformers, or use embed_text_old()."
        ) from e
