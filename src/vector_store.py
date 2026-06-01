from pathlib import Path
import shutil
from typing import Any


COLLECTION_NAME = "steel_textbook"
VECTOR_STORE_DIR = "vector_store"


def get_chroma_client(persist_dir: str | Path = VECTOR_STORE_DIR) -> Any:
    """创建 Chroma 持久化客户端，数据会保存到本地 vector_store 文件夹。"""
    # 延迟导入，便于不依赖 Chroma 的单元测试仍可运行。
    import chromadb

    return chromadb.PersistentClient(path=str(persist_dir))


def reset_vector_store_dir(persist_dir: str | Path = VECTOR_STORE_DIR) -> None:
    """清空并重建本地向量库目录，避免旧索引文件残留。"""
    path = Path(persist_dir)

    if path.exists():
        shutil.rmtree(path)

    path.mkdir(parents=True, exist_ok=True)


def _reset_collection(client: Any, collection_name: str) -> Any:
    """重建教材 collection，避免重复运行时写入重复段落。"""
    try:
        client.delete_collection(collection_name)
    except Exception:
        # collection 不存在时 Chroma 会报错，首次运行可安全忽略。
        pass

    return client.get_or_create_collection(name=collection_name)


def build_vector_store(
    paragraphs: list[str],
    persist_dir: str | Path = VECTOR_STORE_DIR,
    collection_name: str = COLLECTION_NAME,
    client: Any | None = None,
) -> Any:
    """将教材段落写入 Chroma，本地生成 embedding 并保存向量索引。"""
    if client is None:
        reset_vector_store_dir(persist_dir)

    chroma_client = client or get_chroma_client(persist_dir)
    collection = _reset_collection(chroma_client, collection_name)

    documents = [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]
    if not documents:
        return collection

    # Chroma 会使用 collection 的 embedding function 为 documents 生成 embedding。
    collection.add(
        ids=[f"paragraph-{index:04d}" for index in range(1, len(documents) + 1)],
        documents=documents,
        metadatas=[
            {"paragraph_index": index}
            for index in range(1, len(documents) + 1)
        ],
    )

    return collection


def query_collection(collection: Any, question: str, top_k: int = 3) -> list[str]:
    """使用 Chroma 向量检索返回最相关的教材片段。"""
    if collection.count() == 0:
        return []

    n_results = min(top_k, collection.count())
    results = collection.query(query_texts=[question], n_results=n_results)

    documents = results.get("documents") or [[]]
    return documents[0] if documents else []
