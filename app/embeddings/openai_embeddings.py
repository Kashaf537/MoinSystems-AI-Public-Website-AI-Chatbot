from openai import OpenAI

from app.core.config import get_settings


class OpenAIEmbeddingProvider:
    """Generate embeddings using OpenAI."""

    def __init__(self) -> None:
        settings = get_settings()

        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured.")

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.EMBEDDING_MODEL

    def embed(self, text: str) -> list[float]:
        """Generate a single embedding vector."""
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )

        embedding = response.data[0].embedding

        if not embedding:
            raise ValueError("OpenAI returned an empty embedding.")

        return embedding