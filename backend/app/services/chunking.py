
import re

from app.services.text_cleaner import clean_extracted_text


def chunk_document_pages(
    pages: list[dict],
    max_chars: int = 1200,
    overlap_chars: int = 150,
) -> list[dict]:
    """Split page text into word-safe chunks with overlap and source metadata."""

    if max_chars <= 0:
        raise ValueError("max_chars must be greater than zero")

    if overlap_chars < 0 or overlap_chars >= max_chars:
        raise ValueError(
            "overlap_chars must be non-negative and less than max_chars"
        )

    chunks = []
    chunk_number = 1

    for page in pages:
        page_number = page["page_number"]
        text = clean_extracted_text(page.get("text", ""))

        if not text:
            continue

        # Keep complete words; normalize whitespace.
        words = re.findall(r"\S+", text)
        current_words = []

        for word in words:
            candidate = " ".join(current_words + [word])

            if len(candidate) <= max_chars:
                current_words.append(word)
                continue

            # Emit the current chunk before adding the next word.
            if current_words:
                chunks.append({
                    "chunk_id": chunk_number,
                    "page_number": page_number,
                    "text": " ".join(current_words),
                })
                chunk_number += 1

            # Build overlap from complete words at the end of the last chunk.
            overlap_words = []
            overlap_length = 0

            for previous_word in reversed(current_words):
                added_length = len(previous_word) + (
                    1 if overlap_words else 0
                )

                if overlap_length + added_length > overlap_chars:
                    break

                overlap_words.insert(0, previous_word)
                overlap_length += added_length

            current_words = overlap_words

            # Ensure overlap plus the new word fits within max_chars.
            while current_words and len(
                " ".join(current_words + [word])
            ) > max_chars:
                current_words.pop(0)

            if len(word) > max_chars:
                # Preserve the word rather than silently cutting it.
                # An individual word exceeding max_chars is exceptional.
                current_words = [word]
            else:
                current_words.append(word)

        if current_words:
            chunks.append({
                "chunk_id": chunk_number,
                "page_number": page_number,
                "text": " ".join(current_words),
            })
            chunk_number += 1

    return chunks
