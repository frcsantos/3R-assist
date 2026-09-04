from abc import ABC, abstractmethod
from functools import lru_cache

from app.config import get_settings


class EmbedderAdapter(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        pass


class SentenceTransformerEmbedder(EmbedderAdapter):
    def __init__(self, model_name: str) -> None:
        self._model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            import torch
            from sentence_transformers import SentenceTransformer

            if torch.backends.mps.is_available():
                device = "mps"
            elif torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"
            self._model = SentenceTransformer(self._model_name, device=device)
        return self._model

    def embed(self, text: str) -> list[float]:
        return self._get_model().encode(text, normalize_embeddings=True).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        vectors = self._get_model().encode(texts, normalize_embeddings=True)
        return [vector.tolist() for vector in vectors]


class StubEmbedderAdapter(EmbedderAdapter):
    """Deterministic low-dim vectors for tests without loading the model."""

    def embed(self, text: str) -> list[float]:
        seed = sum(ord(char) for char in text) % 997
        return [((seed + index) % 100) / 100.0 for index in range(8)]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]


@lru_cache
def build_embedder() -> EmbedderAdapter:
    settings = get_settings()
    if not settings.embedding_model:
        return StubEmbedderAdapter()
    return SentenceTransformerEmbedder(settings.embedding_model)
