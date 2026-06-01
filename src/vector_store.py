from pathlib import Path
import shutil
from typing import Any

from src.text_chunk import TextChunk


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
    paragraphs: list[str] | list[TextChunk],
    persist_dir: str | Path = VECTOR_STORE_DIR,
    collection_name: str = COLLECTION_NAME,
    client: Any | None = None,
) -> Any:
    """将教材段落写入 Chroma，本地生成 embedding 并保存向量索引。"""
    if client is None:
        reset_vector_store_dir(persist_dir)

    chroma_client = client or get_chroma_client(persist_dir)
    collection = _reset_collection(chroma_client, collection_name)

    documents: list[str] = []
    metadatas: list[dict[str, Any]] = []

    for index, paragraph in enumerate(paragraphs, 1):
        if isinstance(paragraph, TextChunk):
            documents.append(paragraph.display_text())
            metadatas.append(
                {
                    "source_file": paragraph.source_file,
                    "paragraph_number": paragraph.paragraph_number,
                }
            )
            continue

        text = paragraph.strip()
        if text:
            documents.append(text)
            metadatas.append({"source_file": "", "paragraph_number": index})

    if not documents:
        return collection

    # Chroma 会使用 collection 的 embedding function 为 documents 生成 embedding。
    collection.add(
        ids=[f"paragraph-{index:04d}" for index in range(1, len(documents) + 1)],
        documents=documents,
        metadatas=metadatas,
    )

    return collection


def _document_to_chunk(document: str, metadata: dict[str, Any]) -> TextChunk:
    """将 Chroma 查询结果还原为带来源信息的教材片段。"""
    paragraph_number = int(metadata.get("paragraph_number") or 0)
    prefix = f"{paragraph_number}. "
    text = document[len(prefix):] if paragraph_number and document.startswith(prefix) else document

    return TextChunk(
        text=text,
        source_file=str(metadata.get("source_file") or ""),
        paragraph_number=paragraph_number,
    )


def query_collection(collection: Any, question: str, top_k: int = 3) -> list[TextChunk]:
    """使用 Chroma 向量检索返回最相关的教材片段。"""
    if collection.count() == 0:
        return []

    n_results = min(top_k, collection.count())
    results = collection.query(query_texts=[question], n_results=n_results)

    documents = results.get("documents") or [[]]
    metadatas = results.get("metadatas") or [[]]

    return [
        _document_to_chunk(document, metadata)
        for document, metadata in zip(documents[0], metadatas[0])
    ]
