from pathlib import Path
import sys

# 允许从项目根目录直接运行 python scripts/import_pdf.py。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pdf_loader import extract_text_from_pdf
from src.text_cleaner import clean_pdf_text


def import_pdf_to_text(
    pdf_path: str | Path,
    output_dir: str | Path = "data/texts",
    opener=None,
    use_ocr: bool = False,
    ocr_extractor=None,
) -> Path:
    """把单个 PDF 导入为清洗后的 txt 文件，并返回输出路径。"""
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    # 确保文本输出目录存在，便于第一次导入时直接运行脚本。
    output_dir.mkdir(parents=True, exist_ok=True)

    if use_ocr:
        # 只有用户显式启用 OCR 时才加载 OCR 模块，避免影响普通 PDF 导入。
        if ocr_extractor is None:
            from src.ocr_loader import extract_text_from_scanned_pdf

            ocr_extractor = extract_text_from_scanned_pdf

        extracted_text = ocr_extractor(pdf_path)
    else:
        extracted_text = extract_text_from_pdf(pdf_path, opener=opener)

    cleaned_text = clean_pdf_text(extracted_text)
    output_path = output_dir / f"{pdf_path.stem}.txt"

    # 使用 UTF-8 保存中文教材文本，避免后续读取时出现编码问题。
    output_path.write_text(cleaned_text, encoding="utf-8")
    return output_path


def main(argv: list[str] | None = None) -> int:
    """命令行入口：接收 PDF 路径并导入到 data/texts。"""
    argv = argv if argv is not None else sys.argv[1:]

    if len(argv) not in {1, 2} or (len(argv) == 2 and argv[1] != "--ocr"):
        print("用法：python scripts/import_pdf.py data/pdfs/钢铁冶金学教程.pdf [--ocr]")
        return 1

    use_ocr = len(argv) == 2 and argv[1] == "--ocr"
    output_path = import_pdf_to_text(argv[0], use_ocr=use_ocr)
    print(f"PDF 导入完成，文本文件保存为 {output_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
