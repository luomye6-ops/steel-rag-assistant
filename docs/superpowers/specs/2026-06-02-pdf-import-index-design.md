# PDF Import And Index Design

## Goal

Add a non-OCR PDF import workflow for the Steel Metallurgy RAG project so PDF教材 can be converted to text, chunked with page metadata, and indexed for retrieval.

## Architecture

The feature is split into focused modules:

- `src/pdf_loader.py` reads PDF pages with PyMuPDF and emits plain text with `【第 N 页】` markers.
- `src/text_cleaner.py` normalizes extracted text while preserving page markers and likely headings.
- `scripts/import_pdf.py` converts one PDF into `data/texts/<pdf-name>.txt`.
- `scripts/rebuild_index.py` reads all text files in `data/texts/`, creates chunk metadata, writes `data/processed/chunks.json`, and rebuilds the existing Chroma index when available.

## Data Flow

1. Put PDF files under `data/pdfs/`.
2. Run `python scripts/import_pdf.py data/pdfs/钢铁冶金学教程.pdf`.
3. The script extracts and cleans text, then writes `data/texts/钢铁冶金学教程.txt`.
4. Run `python scripts/rebuild_index.py`.
5. The script writes `data/processed/chunks.json` and refreshes `vector_store/`.

## Constraints

- OCR is out of scope.
- Existing `main.py` and `app.py` remain runnable.
- Each new Python file includes Chinese comments.
- Existing dependencies are preserved and `pymupdf` is added.
