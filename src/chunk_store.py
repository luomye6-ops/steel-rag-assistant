from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.load_text import load_text_files
from src.split_text import split_pdf_text_files, split_text_files
from src.text_chunk import TextChunk


def chunks_to_dicts(chunks: list[TextChunk]) -> list[dict[str, Any]]:
    """把 TextChunk 转成 chunks.json 需要的字典结构。"""
    result: list[dict[str, Any]] = []

    for chunk in chunks:
        result.append(
            {
                "source_file": chunk.source_file,
                "page": chunk.page if chunk.page is not None else 0,
                "chunk_id": chunk.chunk_id if chunk.chunk_id is not None else chunk.paragraph_number,
                "content": chunk.text,
            }
        )

    return result


def dicts_to_chunks(items: list[dict[str, Any]]) -> list[TextChunk]:
    """把 chunks.json 中的字典还原为 TextChunk 对象。"""
    chunks: list[TextChunk] = []

    for item in items:
        chunk_id = int(item["chunk_id"])
        chunks.append(
            TextChunk(
                text=str(item["content"]),
                source_file=str(item["source_file"]),
                paragraph_number=chunk_id,
                page=int(item["page"]),
                chunk_id=chunk_id,
            )
        )

    return chunks


def save_chunks(chunks: list[TextChunk], output_path: str | Path) -> Path:
    """保存切分后的 chunks 到 JSON 文件。"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ensure_ascii=False 保留中文，便于人工检查教材片段。
    output_path.write_text(
        json.dumps(chunks_to_dicts(chunks), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path


def load_chunks(input_path: str | Path) -> list[TextChunk]:
    """从 chunks.json 读取 TextChunk 列表。"""
    input_path = Path(input_path)
    data = json.loads(input_path.read_text(encoding="utf-8"))
    return dicts_to_chunks(data)


def load_or_build_chunks(
    processed_path: str | Path = "data/processed/chunks.json",
    data_dir: str | Path = "data",
    texts_dir: str | Path = "data/texts",
) -> list[TextChunk]:
    """优先读取 processed/chunks.json；不存在时从文本文件重新切分。"""
    processed_path = Path(processed_path)
    data_dir = Path(data_dir)
    texts_dir = Path(texts_dir)

    if processed_path.exists():
        return load_chunks(processed_path)

    if texts_dir.exists():
        text_files = [
            (path.name, path.read_text(encoding="utf-8"))
            for path in sorted(texts_dir.glob("*.txt"))
        ]
        return split_pdf_text_files(text_files)

    # 兼容旧版 data/*.txt 教材。
    return split_text_files(load_text_files(data_dir))
