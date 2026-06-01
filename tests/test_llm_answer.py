import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.chat import NO_CLEAR_ANSWER_MESSAGE, generate_answer
from src.config import load_settings
from src.text_chunk import TextChunk


class FakeResponse:
    output_text = "焦炭在高炉中主要起燃料、还原剂来源和支撑料柱的作用。"


class FakeResponses:
    def __init__(self) -> None:
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return FakeResponse()


class FakeClient:
    def __init__(self) -> None:
        self.responses = FakeResponses()


class LlmAnswerTest(unittest.TestCase):
    def test_generate_answer_sends_question_and_references_to_model(self):
        client = FakeClient()
        references = [
            TextChunk("高炉炼铁的基本原理是利用焦炭燃烧产生一氧化碳。", "steel_chapter.txt", 1),
            TextChunk("焦炭在高炉中具有燃料、还原剂来源和支撑料柱的作用。", "steel_chapter.txt", 2),
        ]

        answer = generate_answer(
            "焦炭在高炉中有什么作用？",
            references,
            client=client,
            model="test-model",
        )

        self.assertIn("大模型回答", answer)
        self.assertIn(FakeResponse.output_text, answer)
        self.assertIn("参考教材片段", answer)
        self.assertIn("1. 高炉炼铁的基本原理", answer)
        self.assertIn("参考来源", answer)
        self.assertIn("steel_chapter.txt，第 2 段", answer)
        self.assertEqual(client.responses.calls[0]["model"], "test-model")
        self.assertIn("焦炭在高炉中有什么作用？", client.responses.calls[0]["input"])
        self.assertIn(references[1].display_text(), client.responses.calls[0]["input"])
        self.assertIn("必须基于教材片段", client.responses.calls[0]["instructions"])

    def test_generate_answer_does_not_call_model_without_references(self):
        client = FakeClient()

        answer = generate_answer("连铸结晶器振动参数", [], client=client)

        self.assertIn(NO_CLEAR_ANSWER_MESSAGE, answer)
        self.assertIn("参考教材片段", answer)
        self.assertEqual(client.responses.calls, [])

    def test_load_settings_reads_env_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "OPENAI_API_KEY=test-key\nOPENAI_MODEL=test-model\n",
                encoding="utf-8",
            )

            with patch.dict(os.environ, {}, clear=True):
                settings = load_settings(env_path)

        self.assertEqual(settings.api_key, "test-key")
        self.assertEqual(settings.model, "test-model")


if __name__ == "__main__":
    unittest.main()
