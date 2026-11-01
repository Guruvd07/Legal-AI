
import json
import os
from pathlib import Path

import faiss
import numpy as np

from app.services.embeddings import generate_embeddings


# Store persistent data inside the backend/data directory.
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "vector_store"
INDEX_PATH = DATA_DIR / "legalai.faiss"
METADATA_PATH = DATA_DIR / "chunks.json"

_index = None
_chunks = []


def _save_index() -> None:
    """Persist the FAISS index and its matching chunk metadata."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    index_tmp = DATA_DIR / "legalai.faiss.tmp"
    metadata_tmp = DATA_DIR / "chunks.json.tmp"

    try:
        if _index is None:
            if index_tmp.exists():
                index_tmp.unlink()
            if metadata_tmp.exists():
                metadata_tmp.unlink()
            return

        faiss.write_index(_index, str(index_tmp))

        with metadata_tmp.open("w", encoding="utf-8") as file:
            json.dump(_chunks, file, ensure_ascii=False, indent=2)

        os.replace(index_tmp, INDEX_PATH)
        os.replace(metadata_tmp, METADATA_PATH)

    finally:
        for temporary_file in (index_tmp, metadata_tmp):
            if temporary_file.exists():
                temporary_file.unlink()


def _load_index() -> None:
    """Load the saved index when the service starts."""
    global _index, _chunks

    index_exists = INDEX_PATH.is_file()
    metadata_exists = METADATA_PATH.is_file()

    if not index_exists and not metadata_exists:
        return

    if index_exists != metadata_exists:
        raise RuntimeError(
            "FAISS index and metadata are inconsistent. "
            "Restore both files or rebuild the index."
        )

    loaded_index = faiss.read_index(str(INDEX_PATH))

    with METADATA_PATH.open("r", encoding="utf-8") as file:
        loaded_chunks = json.load(file)

    if not isinstance(loaded_chunks, list):
        raise RuntimeError("Invalid chunk metadata format")

    if loaded_index.ntotal != len(loaded_chunks):
        raise RuntimeError(
            "FAISS vector count does not match metadata count"
        )

    for position, chunk in enumerate(loaded_chunks):
        if not isinstance(chunk, dict):
            raise RuntimeError("Invalid chunk metadata entry")

        chunk["vector_position"] = position

    _index = loaded_index
    _chunks = loaded_chunks


def _rebuild_without_documents(document_ids: set[str]) -> None:
    """Remove old vectors for documents that are being re-indexed."""
    global _index, _chunks

    if _index is None or not document_ids:
        return

    retained_vectors = []
    retained_chunks = []

    for position, chunk in enumerate(_chunks):
        if chunk.get("document_id") in document_ids:
            continue

        retained_vectors.append(_index.reconstruct(position))
        retained_chunks.append(chunk)

    if retained_vectors:
        vectors = np.asarray(retained_vectors, dtype=np.float32)
        new_index = faiss.IndexFlatIP(vectors.shape[1])
        new_index.add(vectors)
    else:
        new_index = None

    for position, chunk in enumerate(retained_chunks):
        chunk["vector_position"] = position

    _index = new_index
    _chunks = retained_chunks


def add_chunks(chunks: list[dict]) -> int:
    """Embed chunks, replace previously indexed documents, and persist."""
    global _index, _chunks

    if not chunks:
        return 0

    texts = [chunk["text"] for chunk in chunks]
    vectors = np.asarray(
        generate_embeddings(texts),
        dtype=np.float32,
    )

    if vectors.ndim != 2 or vectors.shape[0] != len(chunks):
        raise ValueError("Invalid embedding dimensions")

    dimension = vectors.shape[1]

    if _index is not None and _index.d != dimension:
        raise ValueError("Embedding dimensions do not match the index")

    document_ids = {
        chunk.get("document_id")
        for chunk in chunks
        if chunk.get("document_id") is not None
    }

    # Prevent duplicate chunks when re-indexing an existing document.
    _rebuild_without_documents(document_ids)

    if _index is None:
        _index = faiss.IndexFlatIP(dimension)

    start_position = len(_chunks)
    _index.add(vectors)

    _chunks.extend(
        {
            **chunk,
            "vector_position": start_position + i,
        }
        for i, chunk in enumerate(chunks)
    )

    _save_index()
    return len(chunks)


def search_chunks(
    query: str,
    top_k: int = 3,
    document_id: str | None = None,
) -> list[dict]:
    """Search all indexed chunks or restrict results to one document."""
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")

    if _index is None or _index.ntotal == 0:
        return []

    query_vector = np.asarray(
        generate_embeddings([query]),
        dtype=np.float32,
    )

    search_k = (
        _index.ntotal
        if document_id is not None
        else min(top_k, _index.ntotal)
    )

    scores, indices = _index.search(query_vector, search_k)
    results = []

    for score, index_position in zip(scores[0], indices[0]):
        if index_position < 0:
            continue

        chunk = _chunks[int(index_position)]

        if (
            document_id is not None
            and chunk.get("document_id") != document_id
        ):
            continue

        results.append({
            **chunk,
            "similarity_score": float(score),
        })

        if len(results) >= top_k:
            break

    return results


# Restore previously indexed documents on application startup.
_load_index()
