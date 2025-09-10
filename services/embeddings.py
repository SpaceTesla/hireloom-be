from functools import lru_cache
from typing import List

try:
    from sentence_transformers import SentenceTransformer
except Exception as exc:  # pragma: no cover
    raise RuntimeError(
        "sentence-transformers is required. Please install it in your environment."
    ) from exc


EMBEDDING_MODEL_NAME = "BAAI/bge-base-en-v1.5"
EMBEDDING_DIMENSION = 768


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return model


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_embedding_model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return vectors.tolist()

