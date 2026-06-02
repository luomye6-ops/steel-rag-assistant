# PDF Import And Index Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add PDF import, text cleaning, chunk export, and index rebuilding for the Steel Metallurgy RAG project.

**Architecture:** Keep PDF parsing, text cleanup, import CLI, and index rebuild CLI in separate files. Reuse the existing `TextChunk` and `build_vector_store()` APIs so `main.py` and `app.py` remain unchanged.

**Tech Stack:** Python, PyMuPDF (`pymupdf`), `unittest`, existing Chroma wrapper in `src/vector_store.py`.

---

### Task 1: PDF Loader And Cleaner Tests

**Files:**
- Create: `tests/test_pdf_import_pipeline.py`
- Create: `src/pdf_loader.py`
- Create: `src/text_cleaner.py`

- [ ] **Step 1: Write failing tests**

Create tests that call `extract_text_from_pdf()` with an injected fake opener and `clean_pdf_text()` with text containing extra blank lines.

- [ ] **Step 2: Run tests and verify red**

Run: `python -m unittest tests.test_pdf_import_pipeline`

Expected: import failure for missing modules.

- [ ] **Step 3: Implement minimal modules**

Implement PyMuPDF page extraction with page markers and line cleanup.

- [ ] **Step 4: Run tests and verify green**

Run: `python -m unittest tests.test_pdf_import_pipeline`

Expected: tests pass.

### Task 2: Import And Rebuild Scripts

**Files:**
- Create: `scripts/import_pdf.py`
- Create: `scripts/rebuild_index.py`
- Modify: `tests/test_pdf_import_pipeline.py`

- [ ] **Step 1: Write failing tests**

Add tests for saving converted PDF text and writing `chunks.json` with `source_file`, `page`, `chunk_id`, and `content`.

- [ ] **Step 2: Run tests and verify red**

Run: `python -m unittest tests.test_pdf_import_pipeline`

Expected: import failure for missing scripts.

- [ ] **Step 3: Implement scripts**

Implement CLI-compatible functions plus `main()` wrappers.

- [ ] **Step 4: Run tests and verify green**

Run: `python -m unittest tests.test_pdf_import_pipeline`

Expected: tests pass.

### Task 3: Project Files And Verification

**Files:**
- Modify: `requirements.txt`
- Modify: `README.md`
- Create: `data/pdfs/.gitkeep`
- Create: `data/texts/.gitkeep`
- Create: `data/processed/.gitkeep`

- [ ] **Step 1: Update dependency and docs**

Add `pymupdf` and document PDF placement, import, rebuild, and future教材流程.

- [ ] **Step 2: Run focused tests**

Run: `python -m unittest tests.test_pdf_import_pipeline`

Expected: tests pass.

- [ ] **Step 3: Run full tests**

Run: `python -m unittest discover -s tests`

Expected: all tests pass or report dependency/environment blockers clearly.
