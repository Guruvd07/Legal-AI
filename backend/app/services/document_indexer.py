
import json
from pathlib import Path

from app.services.pdf_extractor import extract_pdf_text
from app.services.chunking import chunk_document_pages
from app.services.vector_store import add_chunks


UPLOAD_DIR = Path("data/uploads")
TABLE_EXTRACTIONS_DIR = Path("data/table_extractions")
CHART_EXTRACTIONS_DIR = Path("data/chart_extractions")


def merge_table_text_into_pages(
    pages: list[dict],
    document_id: str,
) -> int:
    """Append saved table OCR text to its corresponding PDF page."""
    extraction_path = TABLE_EXTRACTIONS_DIR / f"{document_id}.json"

    if not extraction_path.is_file():
        return 0

    with extraction_path.open("r", encoding="utf-8") as file:
        extraction_data = json.load(file)

    pages_by_number = {
        page["page_number"]: page
        for page in pages
    }

    merged_count = 0

    for table in extraction_data.get("tables", []):
        page_number = table.get("page_number")
        table_text = table.get("text", "").strip()

        if not table_text or page_number not in pages_by_number:
            continue

        page = pages_by_number[page_number]
        page["text"] = (
            page.get("text", "").rstrip()
            + "\n\n[Extracted table content]\n"
            + table_text
        )
        merged_count += 1

    return merged_count


def merge_chart_text_into_pages(
    pages: list[dict],
    document_id: str,
) -> int:
    """Append saved chart OCR text and labelled estimates to PDF pages."""
    extraction_path = CHART_EXTRACTIONS_DIR / f"{document_id}.json"

    if not extraction_path.is_file():
        return 0

    with extraction_path.open("r", encoding="utf-8") as file:
        extraction_data = json.load(file)

    pages_by_number = {
        page["page_number"]: page
        for page in pages
    }

    merged_count = 0

    for chart in extraction_data.get("charts", []):
        page_number = chart.get("page_number")

        if page_number not in pages_by_number:
            continue

        chart_parts = []

        chart_text = chart.get("text", "").strip()
        if chart_text:
            chart_parts.append(
                "[Extracted chart text]\n" + chart_text
            )

        bar_analysis = chart.get("bar_analysis", {})
        if bar_analysis.get("status") == "estimated":
            bars = bar_analysis.get("bars", [])

            if bars:
                estimate_lines = [
                    "[Approximate chart measurements — "
                    "not verified exact source values]"
                ]

                for bar in bars:
                    estimate_lines.append(
                        f"Bar {bar['bar_index']}: approximately "
                        f"{bar['estimated_value']} "
                        f"(chart-image height estimate)"
                    )

                chart_parts.append("\n".join(estimate_lines))

        if not chart_parts:
            continue

        page = pages_by_number[page_number]
        page["text"] = (
            page.get("text", "").rstrip()
            + "\n\n"
            + "\n\n".join(chart_parts)
        )

        merged_count += 1

    return merged_count


def index_document(document_id: str) -> dict:
    pdf_path = UPLOAD_DIR / f"{document_id}.pdf"
    metadata_path = UPLOAD_DIR / f"{document_id}.json"

    if not pdf_path.is_file():
        raise FileNotFoundError("Uploaded PDF not found")

    original_filename = pdf_path.name

    if metadata_path.is_file():
        try:
            with metadata_path.open("r", encoding="utf-8") as metadata_file:
                metadata = json.load(metadata_file)

            if metadata.get("document_id") == document_id:
                original_filename = metadata.get("filename") or pdf_path.name

        except (json.JSONDecodeError, OSError):
            original_filename = pdf_path.name

    extracted = extract_pdf_text(str(pdf_path))

    merged_table_count = merge_table_text_into_pages(
        extracted["pages"],
        document_id,
    )

    merged_chart_count = merge_chart_text_into_pages(
        extracted["pages"],
        document_id,
    )

    chunks = chunk_document_pages(extracted["pages"])

    if not chunks:
        raise ValueError("No text available to index")

    for chunk in chunks:
        chunk["document_id"] = document_id
        chunk["filename"] = original_filename

    indexed_count = add_chunks(chunks)

    return {
        "document_id": document_id,
        "filename": original_filename,
        "page_count": extracted["page_count"],
        "chunk_count": len(chunks),
        "indexed_count": indexed_count,
        "status": "indexed",
        "table_count_merged": merged_table_count,
        "chart_count_merged": merged_chart_count,
    }
