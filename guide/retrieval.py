"""Persistent semantic search with reproducible corpus and model versioning."""
import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import chromadb
from chromadb.config import Settings
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

from .ingest import Chunk, load_chunks

MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
TOP_K = 5
RRF_OFFSET = 10
TERMS = re.compile(r"\d+(?:\.\d+)+[a-z]*|[a-z0-9]+")
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

    @property
    def source_ids(self):
        return sorted({chunk.source_id for chunk in self.chunks.values()})

    def search(self, query, limit=TOP_K, *, mode="semantic", source=None):
        candidates = [chunk for chunk in self.chunks.values() if source is None or chunk.source_id == source]
        if not candidates:
            return []
        vector = self.model.encode([query], normalize_embeddings=True)[0].tolist()
        results = self.collection.query(
            query_embeddings=[vector],
            n_results=min(len(candidates), limit) if mode == "semantic" else len(candidates),
            where={"source_id": source} if source is not None else None,
            include=["distances"],
        )
        semantic = [
            Match(self.chunks[chunk_id], distance)
            for chunk_id, distance in zip(results["ids"][0], results["distances"][0], strict=True)
        ]
        if mode == "semantic":
            return semantic

        corpus = [TERMS.findall(chunk.text.lower()) for chunk in candidates]
        scores = BM25Okapi(corpus).get_scores(TERMS.findall(query.lower()))
        keyword = sorted(
            ((score, chunk.id) for score, chunk in zip(scores, candidates, strict=True) if score > 0),
            key=lambda pair: (-pair[0], pair[1]),
        )
        keyword_ranks = {chunk_id: rank for rank, (_, chunk_id) in enumerate(keyword, 1)}
        fused = []
        for rank, match in enumerate(semantic, 1):
            sparse_rank = keyword_ranks.get(match.chunk.id)
            score = 1 / (RRF_OFFSET + rank)
            if sparse_rank is not None:
                score += 1 / (RRF_OFFSET + sparse_rank)
            fused.append((score, match))
        fused.sort(key=lambda pair: (-pair[0], pair[1].distance, pair[1].chunk.id))
        return [match for _, match in fused[:limit]]


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
