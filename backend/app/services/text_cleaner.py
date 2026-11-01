
import re


def clean_extracted_text(text: str) -> str:
    """Clean extraction artifacts without removing legal details."""

    text = text.replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove repeated sample-document page headers.
    text = re.sub(
        r"(?m)^LEGALAI TEST DOCUMENT - FICTIONAL SAMPLE\s*$",
        "",
        text,
    )

    # Remove standalone page labels, but preserve clause numbers.
    text = re.sub(r"(?m)^Page \d+\s*$", "", text)

    # Normalize horizontal whitespace without merging words.
    text = re.sub(r"[ \t]+", " ", text)

    # Keep paragraph boundaries while removing excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
