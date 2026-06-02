from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# 允许从项目根目录直接运行 python scripts/rebuild_index.py。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.chunk_store import chunks_to_dicts, save_chunks
from src.text_chunk import TextChunk
from src.split_text import split_pdf_text_files
from src.vector_store import build_vector_store


def build_chunks_from_text_files(texts_dir: str | Path = "data/texts") -> list[dict[str, Any]]:
    """读取 data/texts 下所有 txt，并生成包含来源、页码、编号和正文的 chunks。"""
    texts_dir = Path(texts_dir)
    text_files = [
        (path.name, path.read_text(encoding="utf-8"))
        for path in sorted(texts_dir.glob("*.txt"))
    ]

    # 复用 src.split_text 中的 PDF 切分逻辑，保证脚本和测试使用同一套规则。
    return chunks_to_dicts(split_pdf_text_files(text_files))


def save_chunks_json(
    chunks: list[dict[str, Any]],
    output_dir: str | Path = "data/processed",
) -> Path:
    """把 chunks 保存为 data/processed/chunks.json。"""
    output_dir = Path(output_dir)
    return save_chunks(
        [
            TextChunk(
                text=str(chunk["content"]),
                source_file=str(chunk["source_file"]),
                paragraph_number=int(chunk["chunk_id"]),
                page=int(chunk["page"]),
                chunk_id=int(chunk["chunk_id"]),
            )
            for chunk in chunks
        ],
        output_dir / "chunks.json",
    )


def rebuild_vector_index(chunks: list[dict[str, Any]], persist_dir: str | Path = "vector_store") -> None:
    """如果项目中使用 Chroma，则用现有封装重建本地向量索引。"""
    text_chunks = [
        TextChunk(
            text=str(chunk["content"]),
            source_file=str(chunk["source_file"]),
            paragraph_number=int(chunk["chunk_id"]),
            page=int(chunk["page"]),
            chunk_id=int(chunk["chunk_id"]),
        )
        for chunk in chunks
    ]
    build_vector_store(text_chunks, persist_dir=persist_dir)


def main(argv: list[str] | None = None) -> int:
    """命令行入口：重建 chunks.json 和本地向量索引。"""
    argv = argv if argv is not None else sys.argv[1:]
    if argv:
        print("用法：python scripts/rebuild_index.py")
        return 1

    chunks = build_chunks_from_text_files("data/texts")
    output_path = save_chunks_json(chunks, "data/processed")
    rebuild_vector_index(chunks, "vector_store")

    print(f"索引重建完成，chunks 文件保存为 {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
