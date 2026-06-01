import re

from src.load_text import clean_text
from src.text_chunk import TextChunk


def split_text(text: str) -> list[str]:
    """按空行把教材文本切分成多个段落，并给每个段落添加编号。"""
    # 先清洗文本，保证多余空行和首尾空格不会影响切分结果。
    cleaned_text = clean_text(text)

    # 按一个或多个空行切分段落。
    raw_paragraphs = re.split(r"\n\s*\n", cleaned_text)
    paragraphs = [paragraph.strip() for paragraph in raw_paragraphs if paragraph.strip()]

    # 给每个段落添加从 1 开始的编号。
    return [f"{index}. {paragraph}" for index, paragraph in enumerate(paragraphs, 1)]


def split_text_files(text_files: list[tuple[str, str]]) -> list[TextChunk]:
    """按文件切分教材文本，并为每段保留来源文件名和段落编号。"""
    chunks: list[TextChunk] = []

    for source_file, text in text_files:
        cleaned_text = clean_text(text)
        raw_paragraphs = re.split(r"\n\s*\n", cleaned_text)
        paragraphs = [paragraph.strip() for paragraph in raw_paragraphs if paragraph.strip()]

        for index, paragraph in enumerate(paragraphs, 1):
            chunks.append(
                TextChunk(
                    text=paragraph,
                    source_file=source_file,
                    paragraph_number=index,
                )
            )

    return chunks
