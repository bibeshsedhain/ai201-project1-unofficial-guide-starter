"""Persistent semantic search with reproducible corpus and model versioning."""
import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from .ingest import Chunk, load_chunks

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
TOP_K = 5
INDEX_PATH = Path(__file__).resolve().parents[1] / "chroma_db"


@dataclass(frozen=True)
class Match:
    chunk: Chunk
    distance: float


class Index:
    def __init__(self, chunks=None, path=INDEX_PATH, model=None):
        chunks = load_chunks() if chunks is None else chunks
        self.chunks = {chunk.id: chunk for chunk in chunks}
        rows = [asdict(chunk) for chunk in chunks]
        fingerprint = json.dumps([MODEL_ID, MODEL_REVISION, rows], sort_keys=True)
        name = "guide-" + hashlib.sha256(fingerprint.encode()).hexdigest()[:24]
        self.model = model if model is not None else SentenceTransformer(MODEL_ID, revision=MODEL_REVISION, device="cpu")
        client = chromadb.PersistentClient(path=str(path), settings=Settings(anonymized_telemetry=False))
        self.collection = client.get_or_create_collection(name, configuration={"hnsw": {"space": "cosine"}})
        if self.collection.count() != len(chunks):
            vectors = self.model.encode([chunk.text for chunk in chunks], normalize_embeddings=True)
            self.collection.upsert(
                ids=list(self.chunks),
                documents=[chunk.text for chunk in chunks],
                embeddings=vectors.tolist(),
                metadatas=[
                    {"source_id": chunk.source_id, "title": chunk.title, "url": chunk.url,
                     "section": chunk.section, "position": chunk.position}
                    for chunk in chunks
                ],
            )

    def search(self, query, limit=TOP_K):
        vector = self.model.encode([query], normalize_embeddings=True)[0].tolist()
        results = self.collection.query(query_embeddings=[vector], n_results=limit, include=["distances"])
        return [
            Match(self.chunks[chunk_id], distance)
            for chunk_id, distance in zip(results["ids"][0], results["distances"][0], strict=True)
        ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="+", help="One or more quoted queries")
    args = parser.parse_args()
    index = Index()
    for query in args.query:
        print(f"\n{query}")
        for match in index.search(query):
            print(f"  {match.distance:.3f}  {match.chunk.title} [{match.chunk.id}]")
            print(f"         {match.chunk.text}")
