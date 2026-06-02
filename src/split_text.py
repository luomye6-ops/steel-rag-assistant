import re

from src.load_text import clean_text
from src.text_chunk import TextChunk


PAGE_MARKER_RE = re.compile(r"^【第\s*(\d+)\s*页】$")


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


def _split_pdf_text_by_page(text: str) -> list[tuple[int, str]]:
    """根据【第 N 页】标记把 PDF 文本拆成页面。"""
    pages: list[tuple[int, list[str]]] = []
    current_page = 0
    current_lines: list[str] = []

    for line in text.splitlines():
        marker = PAGE_MARKER_RE.match(line.strip())
        if marker:
            if current_page:
                pages.append((current_page, current_lines))
            current_page = int(marker.group(1))
            current_lines = []
            continue

        current_lines.append(line)

    if current_page:
        pages.append((current_page, current_lines))
    elif text.strip():
        # 兼容没有页码标记的文本，页码记为 0。
        pages.append((0, text.splitlines()))

    return [(page, "\n".join(lines).strip()) for page, lines in pages]


def split_pdf_text_files(text_files: list[tuple[str, str]]) -> list[TextChunk]:
    """切分 PDF 导入文本，并保留来源文件、页码和全局片段编号。"""
    chunks: list[TextChunk] = []
    chunk_id = 1

    for source_file, text in text_files:
        cleaned_text = clean_text(text)

        for page, page_text in _split_pdf_text_by_page(cleaned_text):
            # PDF 文本按空行切成自然段，章节标题会作为独立片段保留。
            raw_paragraphs = re.split(r"\n\s*\n", page_text)
            paragraphs = [paragraph.strip() for paragraph in raw_paragraphs if paragraph.strip()]

            for paragraph in paragraphs:
                chunks.append(
                    TextChunk(
                        text=paragraph,
                        source_file=source_file,
                        paragraph_number=chunk_id,
                        page=page,
                        chunk_id=chunk_id,
                    )
                )
                chunk_id += 1

    return chunks
