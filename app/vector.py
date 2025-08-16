import numpy as np
import pydantic
from sklearn.neighbors import NearestNeighbors

from app.app_logging import logger
from app.snippets import Snippet


class _SearchResult(pydantic.BaseModel):
    score: float
    metadata: Snippet


class _SearchResults(pydantic.BaseModel):
    data: list[_SearchResult] = []


class SklearnVectorStore:
    vectors: list[np.ndarray]
    metadata: list[Snippet]
    nn: NearestNeighbors | None

    def __init__(self):
        self.vectors = []
        self.metadata = []
        self.nn = None

    def add(self, vector: np.ndarray, snippet: Snippet):
        # logger.debug(("Vector: ", vector))
        self.vectors.append(vector)
        self.metadata.append(snippet)
        # logger.debug(self.vectors)
        # logger.debug(self.metadata)
        # logger.debug(self.nn)

    def fit(self):
        self.nn = NearestNeighbors(metric="cosine")
        self.nn.fit(np.asarray(self.vectors))

    def search(self, query_vector: np.ndarray, k: int = 2) -> _SearchResults:
        # logger.debug(id(self))
        if not self.nn:
            logger.debug(f"self.nn == {self.nn}")
            return _SearchResults()

        # logger.debug({"Searhc query": query_vector})
        distances, indicies = self.nn.kneighbors(
            np.array([query_vector]), n_neighbors=min(k, len(self.vectors))
        )
        logger.debug(f"{distances=} {indicies=}")

        for dist, idx in zip(distances[0], indicies[0]):
            similarity = 1 - dist
            logger.debug(
                f"Similarity: {similarity:.3f} | Snippet: {self.metadata[idx]}"
            )

        return _SearchResults(
            data=[
                _SearchResult(score=1 - dist, metadata=self.metadata[idx])
                for dist, idx in zip(distances[0], indicies[0])
            ]
        )
