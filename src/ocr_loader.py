from pathlib import Path
from typing import Any, Callable


def _pixmap_to_image(pixmap: Any) -> Any:
    """把 PyMuPDF 的 pixmap 转成 pytesseract 可以识别的 PIL 图片。"""
    from PIL import Image

    mode = "RGBA" if pixmap.alpha else "RGB"
    return Image.frombytes(mode, [pixmap.width, pixmap.height], pixmap.samples)


def extract_text_from_scanned_pdf(
    pdf_path: str | Path,
    opener: Callable[[str | Path], Any] | None = None,
    ocr_function: Callable[[Any, str], str] | None = None,
    image_converter: Callable[[Any], Any] | None = None,
    lang: str = "chi_sim+eng",
    zoom: float = 2.0,
) -> str:
    """使用 OCR 识别扫描版 PDF，并在每页文本前添加页码标记。"""
    # 延迟导入第三方库，避免普通 PDF 导入时强制加载 OCR 依赖。
    if opener is None:
        import fitz

        opener = fitz.open

    if ocr_function is None:
        import pytesseract

        def ocr_function(image: Any, lang: str) -> str:
            # Windows 安装器有时不会立刻刷新 PATH，这里兼容默认安装路径。
            tesseract_cmd = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
            if tesseract_cmd.exists():
                pytesseract.pytesseract.tesseract_cmd = str(tesseract_cmd)

            # 项目本地 tessdata 可放中文语言包，避免必须写入 Program Files。
            tessdata_dir = Path(__file__).resolve().parents[1] / "tessdata"
            config = f'--tessdata-dir "{tessdata_dir}"' if tessdata_dir.exists() else ""

            return pytesseract.image_to_string(image, lang=lang, config=config)

    if image_converter is None:
        image_converter = _pixmap_to_image

    document = opener(pdf_path)
    page_texts: list[str] = []

    try:
        import fitz

        matrix = fitz.Matrix(zoom, zoom)

        for page_index, page in enumerate(document, 1):
            # 扫描版 PDF 没有文字层，需要先把页面渲染成图片再做 OCR。
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            image = image_converter(pixmap)
            text = ocr_function(image, lang).strip()
            page_texts.append(f"【第 {page_index} 页】\n{text}")
    finally:
        # 关闭文档，释放 PDF 文件句柄。
        close = getattr(document, "close", None)
        if callable(close):
            close()

    return "\n\n".join(page_texts).strip()
