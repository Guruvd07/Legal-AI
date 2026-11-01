MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None


def get_embedding_model():
    """Load the embedding model only when required."""
    global _model

    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(MODEL_NAME)

    return _model


def generate_embeddings(texts: list[str]):
    """Convert text chunks into normalized numerical vectors."""

    if not texts:
        return []

    model = get_embedding_model()

    return model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )