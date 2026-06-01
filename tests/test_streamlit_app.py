import importlib
import sys
import unittest
from unittest.mock import patch


class FakeStreamlit:
    def cache_resource(self, **_kwargs):
        def decorator(func):
            return func

        return decorator


class FakeResponse:
    output_text = "焦炭在高炉中主要作为燃料、还原剂来源，并支撑料柱。"


class FakeResponses:
    def create(self, **_kwargs):
        return FakeResponse()


class FakeClient:
    responses = FakeResponses()


class FakeCollection:
    def count(self):
        return 1

    def query(self, query_texts, n_results):
        return {
            "documents": [["2. 焦炭在高炉中具有燃料、还原剂来源和支撑料柱的作用。"]],
            "metadatas": [[{"source_file": "steel_chapter.txt", "paragraph_number": 2}]],
        }


class StreamlitAppTest(unittest.TestCase):
    def test_answer_question_returns_answer_with_reference_source(self):
        with patch.dict(sys.modules, {"streamlit": FakeStreamlit()}):
            app = importlib.import_module("app")

        answer = app.answer_question(
            question="焦炭在高炉中有什么作用？",
            collection=FakeCollection(),
            client=FakeClient(),
            model="test-model",
            provider="openai",
        )

        self.assertIn("大模型回答", answer)
        self.assertIn("参考教材片段", answer)
        self.assertIn("参考来源", answer)
        self.assertIn("steel_chapter.txt，第 2 段", answer)


if __name__ == "__main__":
    unittest.main()
