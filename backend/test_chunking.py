
from app.services.chunking import chunk_document_pages


def test_chunking_preserves_page_metadata():
    pages = [
        {
            "page_number": 1,
            "text": "Clause 1. Payment is due in 15 days. " * 50,
        },
        {
            "page_number": 2,
            "text": "Clause 2. Termination requires written notice. " * 50,
        },
    ]

    chunks = chunk_document_pages(
        pages,
        max_chars=300,
        overlap_chars=40,
    )

    assert chunks
    assert all(len(chunk["text"]) <= 300 for chunk in chunks)
    assert any(chunk["page_number"] == 1 for chunk in chunks)
    assert any(chunk["page_number"] == 2 for chunk in chunks)
    assert all(chunk["text"].strip() for chunk in chunks)

    print(f"Chunking successful: {len(chunks)} chunks generated")


if __name__ == "__main__":
    test_chunking_preserves_page_metadata()
