import json
import tempfile
import unittest
from pathlib import Path

from scripts.import_pdf import import_pdf_to_text
from scripts.rebuild_index import build_chunks_from_text_files, save_chunks_json
from src.ocr_loader import extract_text_from_scanned_pdf
from src.pdf_loader import extract_text_from_pdf
from src.text_cleaner import clean_pdf_text


class FakePage:
    def __init__(self, text: str) -> None:
        self.text = text

    def get_text(self, mode: str = "text") -> str:
        self.mode = mode
        return self.text

    def get_pixmap(self, matrix=None, alpha: bool = False):
        self.matrix = matrix
        self.alpha = alpha
        return f"image:{self.text}"


class FakeDocument:
    def __init__(self, pages: list[FakePage]) -> None:
        self.pages = pages
        self.closed = False

    def __iter__(self):
        return iter(self.pages)

    def close(self) -> None:
        self.closed = True


class PdfImportPipelineTest(unittest.TestCase):
    def test_extract_text_from_pdf_adds_page_markers(self):
        document = FakeDocument([FakePage("第一页内容"), FakePage("第二页内容")])

        text = extract_text_from_pdf("book.pdf", opener=lambda _: document)

        self.assertEqual(text, "【第 1 页】\n第一页内容\n\n【第 2 页】\n第二页内容")
        self.assertTrue(document.closed)

    def test_clean_pdf_text_removes_extra_blank_lines_and_keeps_page_markers(self):
        raw_text = "  【第 1 页】  \n\n\n 第一章  绪论 \n\n\n\n 高炉炼铁  \n"

        cleaned_text = clean_pdf_text(raw_text)

        self.assertEqual(cleaned_text, "【第 1 页】\n\n第一章  绪论\n\n高炉炼铁")

    def test_import_pdf_to_text_saves_cleaned_txt_with_pdf_name(self):
        document = FakeDocument([FakePage("  高炉炼铁  \n\n\n 焦炭作用 ")])

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "texts"
            output_path = import_pdf_to_text(
                "钢铁冶金学教程.pdf",
                output_dir=output_dir,
                opener=lambda _: document,
            )

            self.assertEqual(output_path.name, "钢铁冶金学教程.txt")
            self.assertEqual(
                output_path.read_text(encoding="utf-8"),
                "【第 1 页】\n高炉炼铁\n\n焦炭作用",
            )

    def test_extract_text_from_scanned_pdf_uses_ocr_and_adds_page_markers(self):
        document = FakeDocument([FakePage("第一页图片"), FakePage("第二页图片")])

        text = extract_text_from_scanned_pdf(
            "scan.pdf",
            opener=lambda _: document,
            ocr_function=lambda image, lang: f"{image} -> {lang}",
            image_converter=lambda pixmap: pixmap,
        )

        self.assertEqual(
            text,
            "【第 1 页】\nimage:第一页图片 -> chi_sim+eng\n\n【第 2 页】\nimage:第二页图片 -> chi_sim+eng",
        )
        self.assertTrue(document.closed)

    def test_import_pdf_to_text_can_use_ocr_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "texts"
            output_path = import_pdf_to_text(
                "扫描版教材.pdf",
                output_dir=output_dir,
                use_ocr=True,
                ocr_extractor=lambda path: "【第 1 页】\n OCR 识别内容  ",
            )

            self.assertEqual(output_path.name, "扫描版教材.txt")
            self.assertEqual(output_path.read_text(encoding="utf-8"), "【第 1 页】\nOCR 识别内容")

    def test_build_chunks_from_text_files_keeps_source_page_and_chunk_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            texts_dir = Path(temp_dir) / "texts"
            texts_dir.mkdir()
            (texts_dir / "book.txt").write_text(
                "【第 1 页】\n\n第一章 绪论\n\n高炉炼铁\n\n【第 2 页】\n\n转炉炼钢",
                encoding="utf-8",
            )

            chunks = build_chunks_from_text_files(texts_dir)

            self.assertEqual(
                chunks,
                [
                    {
                        "source_file": "book.txt",
                        "page": 1,
                        "chunk_id": 1,
                        "content": "第一章 绪论",
                    },
                    {
                        "source_file": "book.txt",
                        "page": 1,
                        "chunk_id": 2,
                        "content": "高炉炼铁",
                    },
                    {
                        "source_file": "book.txt",
                        "page": 2,
                        "chunk_id": 3,
                        "content": "转炉炼钢",
                    },
                ],
            )

    def test_save_chunks_json_writes_processed_output(self):
        chunks = [
            {"source_file": "book.txt", "page": 1, "chunk_id": 1, "content": "高炉炼铁"}
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = save_chunks_json(chunks, Path(temp_dir) / "processed")

            self.assertEqual(output_path.name, "chunks.json")
            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8")),
                chunks,
            )


if __name__ == "__main__":
    unittest.main()
