import unittest
import tempfile
from pathlib import Path

from src.text_chunk import TextChunk
from src.vector_store import build_vector_store, query_collection, reset_vector_store_dir


class FakeCollection:
    def __init__(self) -> None:
        self.add_calls = []
        self.documents = []
        self.metadatas = []
        self.query_calls = []

    def add(self, ids, documents, metadatas):
        self.add_calls.append(
            {
                "ids": ids,
                "documents": documents,
                "metadatas": metadatas,
            }
        )
        self.documents = documents
        self.metadatas = metadatas

    def count(self):
        return len(self.documents)

    def query(self, query_texts, n_results):
        self.query_calls.append(
            {
                "query_texts": query_texts,
                "n_results": n_results,
            }
        )
        return {
            "documents": [self.documents[:n_results]],
            "metadatas": [self.metadatas[:n_results]],
        }


class FakeClient:
    def __init__(self) -> None:
        self.deleted_collections = []
        self.collection = FakeCollection()

    def delete_collection(self, name):
        self.deleted_collections.append(name)

    def get_or_create_collection(self, name):
        self.collection_name = name
        return self.collection


class VectorStoreTest(unittest.TestCase):
    def test_reset_vector_store_dir_removes_old_files_and_recreates_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store_dir = Path(temp_dir) / "vector_store"
            store_dir.mkdir()
            (store_dir / "old.index").write_text("old", encoding="utf-8")

            reset_vector_store_dir(store_dir)

            self.assertTrue(store_dir.exists())
            self.assertEqual(list(store_dir.iterdir()), [])

    def test_build_vector_store_resets_collection_and_adds_paragraphs(self):
        client = FakeClient()
        paragraphs = [
            TextChunk("高炉炼铁", "steel_chapter.txt", 1),
            TextChunk("焦炭作用", "steel_chapter.txt", 2),
        ]

        collection = build_vector_store(paragraphs, client=client)

        self.assertIs(collection, client.collection)
        self.assertEqual(client.deleted_collections, ["steel_textbook"])
        self.assertEqual(
            client.collection.add_calls[0],
            {
                "ids": ["paragraph-0001", "paragraph-0002"],
                "documents": ["1. 高炉炼铁", "2. 焦炭作用"],
                "metadatas": [
                    {"source_file": "steel_chapter.txt", "paragraph_number": 1},
                    {"source_file": "steel_chapter.txt", "paragraph_number": 2},
                ],
            },
        )

    def test_build_vector_store_adds_documents_in_batches(self):
        client = FakeClient()
        paragraphs = [
            TextChunk(f"片段 {index}", "ocr_book.txt", index)
            for index in range(1, 6)
        ]

        build_vector_store(paragraphs, client=client, batch_size=2)

        self.assertEqual(len(client.collection.add_calls), 3)
        self.assertEqual(client.collection.add_calls[0]["ids"], ["paragraph-0001", "paragraph-0002"])
        self.assertEqual(client.collection.add_calls[1]["ids"], ["paragraph-0003", "paragraph-0004"])
        self.assertEqual(client.collection.add_calls[2]["ids"], ["paragraph-0005"])

    def test_query_collection_returns_top_three_chunks_with_sources(self):
        collection = FakeCollection()
        collection.documents = ["1. 高炉炼铁", "2. 焦炭作用", "3. 炉渣作用", "4. 转炉炼钢"]
        collection.metadatas = [
            {"source_file": "steel_chapter.txt", "paragraph_number": 1},
            {"source_file": "steel_chapter.txt", "paragraph_number": 2},
            {"source_file": "steel_chapter.txt", "paragraph_number": 3},
            {"source_file": "steel_chapter.txt", "paragraph_number": 4},
        ]

        results = query_collection(collection, "高炉中焦炭的作用是什么？")

        self.assertEqual([chunk.display_text() for chunk in results], ["1. 高炉炼铁", "2. 焦炭作用", "3. 炉渣作用"])
        self.assertEqual(results[1].source_text(), "steel_chapter.txt，第 2 段")
        self.assertEqual(
            collection.query_calls[0],
            {
                "query_texts": ["高炉中焦炭的作用是什么？"],
                "n_results": 3,
            },
        )

    def test_query_collection_returns_empty_list_for_empty_collection(self):
        collection = FakeCollection()

        results = query_collection(collection, "高炉炼铁")

        self.assertEqual(results, [])
        self.assertEqual(collection.query_calls, [])


if __name__ == "__main__":
    unittest.main()
