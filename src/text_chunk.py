from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    """教材段落片段，包含正文和来源信息。"""

    text: str
    source_file: str
    paragraph_number: int

    def display_text(self) -> str:
        """返回给用户和大模型看的带编号段落正文。"""
        return f"{self.paragraph_number}. {self.text}"

    def source_text(self) -> str:
        """返回参考来源显示文本。"""
        return f"{self.source_file}，第 {self.paragraph_number} 段"
