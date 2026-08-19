from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import get_settings


class LocalEmbeddingProvider:
    """Generate embeddings locally using Sentence Transformers."""

    def __init__(self) -> None:
        settings = get_settings()

        self.model_name = settings.EMBEDDING_MODEL
        self.model = self._load_model()

    @lru_cache(maxsize=1)
    def _load_model(self) -> SentenceTransformer:
        return SentenceTransformer(self.model_name)

    def embed(self, text: str) -> list[float]:
        """Generate one embedding."""

        if not text or not text.strip():
            raise ValueError("Cannot generate an embedding for empty text.")

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""

        if not texts:
            return []

        if any(not text or not text.strip() for text in texts):
            raise ValueError("Cannot generate embeddings for empty text.")

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        """Return embedding vector dimension."""

        return self.model.get_embedding_dimension()