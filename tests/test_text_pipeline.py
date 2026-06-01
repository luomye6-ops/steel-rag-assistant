import tempfile
import unittest
from pathlib import Path

from src.load_text import load_text, load_texts_from_data
from src.split_text import split_text


class TextPipelineTest(unittest.TestCase):
    def test_load_texts_from_data_reads_all_txt_files_and_cleans_text(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            (data_dir / "a.txt").write_text("  第一段  \n\n\n第二段\n", encoding="utf-8")
            (data_dir / "b.txt").write_text("\n  第三段  \n", encoding="utf-8")
            (data_dir / "skip.md").write_text("不应读取", encoding="utf-8")

            text = load_texts_from_data(data_dir)

        self.assertEqual(text, "第一段\n\n第二段\n\n第三段")

    def test_load_text_keeps_backward_compatible_single_file_reading(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "book.txt"
            file_path.write_text("  高炉炼铁  \n\n\n  焦炭作用  ", encoding="utf-8")

            text = load_text(file_path)

        self.assertEqual(text, "高炉炼铁\n\n焦炭作用")

    def test_split_text_cleans_paragraphs_and_adds_numbers(self):
        text = "  高炉炼铁  \n\n\n  焦炭作用  \n\n 炉渣作用 "

        paragraphs = split_text(text)

        self.assertEqual(
            paragraphs,
            [
                "1. 高炉炼铁",
                "2. 焦炭作用",
                "3. 炉渣作用",
            ],
        )


if __name__ == "__main__":
    unittest.main()
