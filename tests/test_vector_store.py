import unittest
import tempfile
from pathlib import Path

from src.vector_store import build_vector_store, query_collection, reset_vector_store_dir


class FakeCollection:
    def __init__(self) -> None:
        self.add_calls = []
        self.documents = []
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

    def count(self):
        return len(self.documents)

    def query(self, query_texts, n_results):
        self.query_calls.append(
            {
                "query_texts": query_texts,
                "n_results": n_results,
            }
        )
        return {"documents": [self.documents[:n_results]]}


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
        paragraphs = ["1. 高炉炼铁", "2. 焦炭作用", "  "]

        collection = build_vector_store(paragraphs, client=client)

        self.assertIs(collection, client.collection)
        self.assertEqual(client.deleted_collections, ["steel_textbook"])
        self.assertEqual(
            client.collection.add_calls[0],
            {
                "ids": ["paragraph-0001", "paragraph-0002"],
                "documents": ["1. 高炉炼铁", "2. 焦炭作用"],
                "metadatas": [
                    {"paragraph_index": 1},
                    {"paragraph_index": 2},
                ],
            },
        )

    def test_query_collection_returns_top_three_documents(self):
        collection = FakeCollection()
        collection.documents = ["1. 高炉炼铁", "2. 焦炭作用", "3. 炉渣作用", "4. 转炉炼钢"]

        results = query_collection(collection, "高炉中焦炭的作用是什么？")

        self.assertEqual(results, ["1. 高炉炼铁", "2. 焦炭作用", "3. 炉渣作用"])
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
