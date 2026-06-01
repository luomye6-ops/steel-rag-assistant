from pathlib import Path


def clean_text(text: str) -> str:
    """对教材文本做简单清洗：去掉首尾空格，并压缩多余空行。"""
    # 统一不同系统的换行符，便于后续按行处理。
    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned_lines: list[str] = []

    for line in normalized_text.split("\n"):
        stripped_line = line.strip()

        # 空行只保留一个，用来表示段落分隔。
        if not stripped_line:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue

        cleaned_lines.append(stripped_line)

    return "\n".join(cleaned_lines).strip()


def load_text(file_path: str | Path = "data/steel_chapter.txt") -> str:
    """读取单个本地 txt 教材文件，并返回清洗后的文本。"""
    # 将传入路径转换为 Path，便于后续读取文件。
    path = Path(file_path)

    # 使用 UTF-8 编码读取中文教材文本。
    return clean_text(path.read_text(encoding="utf-8"))


def load_texts_from_data(data_dir: str | Path = "data") -> str:
    """读取 data 文件夹下所有 txt 教材文件，并合并为一段文本。"""
    # 按文件名排序，保证每次读取顺序稳定。
    paths = sorted(Path(data_dir).glob("*.txt"))
    texts = []

    for path in paths:
        # 跳过清洗后为空的文件。
        text = load_text(path)
        if text:
            texts.append(text)

    # 多个教材文件之间用空行分隔，方便后续切分段落。
    return "\n\n".join(texts)
