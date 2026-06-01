import tempfile
import unittest
from pathlib import Path

from src.chat import generate_answer
from src.load_text import load_text, load_texts_from_data
from src.retrieve import retrieve
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

    def test_retrieve_returns_top_three_matching_paragraphs(self):
        paragraphs = [
            "1. 高炉炼铁依靠焦炭提供热量并生成还原气体。",
            "2. 焦炭在高炉中具有燃料、还原剂和支撑料柱的作用。",
            "3. 炉渣具有吸收杂质和保护铁水的作用。",
            "4. 转炉炼钢通过吹入氧气降低铁水中的碳含量。",
            "5. 焦炭质量会影响高炉透气性和冶炼过程。",
        ]

        results = retrieve(paragraphs, "焦炭在高炉中有什么作用？")

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0], paragraphs[1])
        self.assertIn(paragraphs[0], results)
        self.assertIn(paragraphs[4], results)

    def test_retrieve_returns_empty_list_when_no_match(self):
        paragraphs = [
            "1. 高炉炼铁依靠焦炭提供热量。",
            "2. 转炉炼钢通过吹入氧气降低碳含量。",
        ]

        results = retrieve(paragraphs, "连铸结晶器振动参数")

        self.assertEqual(results, [])

    def test_generate_answer_shows_message_when_no_references(self):
        answer = generate_answer("连铸结晶器振动参数", [])

        self.assertIn("参考教材片段", answer)
        self.assertIn("当前教材内容中没有找到明确答案", answer)


if __name__ == "__main__":
    unittest.main()
