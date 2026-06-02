from pathlib import Path
from typing import Any, Callable


def extract_text_from_pdf(
    pdf_path: str | Path,
    opener: Callable[[str | Path], Any] | None = None,
) -> str:
    """使用 PyMuPDF 按页读取 PDF，并在每页文本前添加页码标记。"""
    # 允许测试注入假的 opener，避免单元测试依赖真实 PDF 文件。
    if opener is None:
        import fitz

        opener = fitz.open

    document = opener(pdf_path)
    page_texts: list[str] = []

    try:
        for page_index, page in enumerate(document, 1):
            # get_text("text") 会提取 PDF 中已有的文字层；扫描版图片不会被 OCR。
            text = page.get_text("text").strip()
            page_texts.append(f"【第 {page_index} 页】\n{text}")
    finally:
        # PyMuPDF 文档对象需要显式关闭，释放文件句柄。
        close = getattr(document, "close", None)
        if callable(close):
            close()

    return "\n\n".join(page_texts).strip()
