from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    """教材段落片段，包含正文和来源信息。"""

    text: str
    source_file: str
    paragraph_number: int
    page: int | None = None
    chunk_id: int | None = None

    def display_text(self) -> str:
        """返回给用户和大模型看的带编号段落正文。"""
        return f"{self.paragraph_number}. {self.text}"

    def source_text(self) -> str:
        """返回参考来源显示文本。"""
        # PDF 导入的片段优先显示页码和全局片段编号，方便定位教材原文。
        if self.page is not None and self.chunk_id is not None:
            return f"{self.source_file}，第 {self.page} 页，片段 {self.chunk_id}"

        return f"{self.source_file}，第 {self.paragraph_number} 段"
