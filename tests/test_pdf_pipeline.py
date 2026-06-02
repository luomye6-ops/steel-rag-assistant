import json
import tempfile
import unittest
from pathlib import Path

from src.chunk_store import (
    chunks_to_dicts,
    load_chunks,
    load_or_build_chunks,
    save_chunks,
)
from src.split_text import split_pdf_text_files
from src.text_cleaner import clean_pdf_text
from src.text_chunk import TextChunk


class PdfPipelineTest(unittest.TestCase):
    def test_clean_pdf_text_removes_extra_blank_lines_and_keeps_page_markers(self):
        raw_text = "  【第 1 页】  \n\n\n  第一段  \n\n  第二段  "

        cleaned_text = clean_pdf_text(raw_text)

        self.assertEqual(cleaned_text, "【第 1 页】\n\n第一段\n\n第二段")

    def test_split_pdf_text_files_keeps_source_page_and_chunk_id(self):
        chunks = split_pdf_text_files(
            [
                (
                    "steel_metallurgy.txt",
                    "【第 35 页】\n\n高炉炼铁内容\n\n焦炭作用\n\n【第 36 页】\n\n炉渣作用",
                )
            ]
        )

        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0].source_file, "steel_metallurgy.txt")
        self.assertEqual(chunks[0].page, 35)
        self.assertEqual(chunks[0].chunk_id, 1)
        self.assertEqual(chunks[1].source_text(), "steel_metallurgy.txt，第 35 页，片段 2")
        self.assertEqual(chunks[2].source_text(), "steel_metallurgy.txt，第 36 页，片段 3")

    def test_save_and_load_chunks_json(self):
        chunks = [
            TextChunk("高炉炼铁内容", "steel_metallurgy.txt", paragraph_number=1, page=35, chunk_id=1),
            TextChunk("焦炭作用", "steel_metallurgy.txt", paragraph_number=2, page=35, chunk_id=2),
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "chunks.json"
            save_chunks(chunks, output_path)
            data = json.loads(output_path.read_text(encoding="utf-8"))
            loaded_chunks = load_chunks(output_path)

        self.assertEqual(data[0]["source_file"], "steel_metallurgy.txt")
        self.assertEqual(data[0]["page"], 35)
        self.assertEqual(data[0]["chunk_id"], 1)
        self.assertEqual(data[0]["content"], "高炉炼铁内容")
        self.assertEqual(loaded_chunks, chunks)

    def test_load_or_build_chunks_prefers_processed_chunks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            processed_dir = root / "data" / "processed"
            processed_dir.mkdir(parents=True)
            chunks_path = processed_dir / "chunks.json"
            chunks_path.write_text(
                json.dumps(
                    [
                        {
                            "source_file": "from_processed.txt",
                            "page": 1,
                            "chunk_id": 1,
                            "content": "来自 processed 的内容",
                        }
                    ],
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            chunks = load_or_build_chunks(
                processed_path=chunks_path,
                data_dir=root / "data",
                texts_dir=root / "data" / "texts",
            )

        self.assertEqual(chunks[0].source_file, "from_processed.txt")
        self.assertEqual(chunks[0].source_text(), "from_processed.txt，第 1 页，片段 1")

    def test_chunks_to_dicts_uses_required_keys(self):
        chunks = [
            TextChunk("高炉炼铁内容", "steel_metallurgy.txt", paragraph_number=1, page=35, chunk_id=12)
        ]

        self.assertEqual(
            chunks_to_dicts(chunks),
            [
                {
                    "source_file": "steel_metallurgy.txt",
                    "page": 35,
                    "chunk_id": 12,
                    "content": "高炉炼铁内容",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
