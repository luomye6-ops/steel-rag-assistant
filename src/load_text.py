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


def _collect_txt_paths(data_dir: str | Path = "data") -> list[Path]:
    """收集根目录 txt 和 data/texts 下导入生成的 txt 文件。"""
    data_path = Path(data_dir)

    # 先读取旧版 data/*.txt，再读取新版 data/texts/*.txt，保持兼容和顺序稳定。
    root_paths = sorted(data_path.glob("*.txt"))
    imported_paths = sorted((data_path / "texts").glob("*.txt"))

    return root_paths + imported_paths


def load_texts_from_data(data_dir: str | Path = "data") -> str:
    """读取 data 文件夹下所有 txt 教材文件，并合并为一段文本。"""
    # 同时读取 data/*.txt 和 data/texts/*.txt，兼容旧教材和新导入教材。
    paths = _collect_txt_paths(data_dir)
    texts = []

    for path in paths:
        # 跳过清洗后为空的文件。
        text = load_text(path)
        if text:
            texts.append(text)

    # 多个教材文件之间用空行分隔，方便后续切分段落。
    return "\n\n".join(texts)


def load_text_files(data_dir: str | Path = "data") -> list[tuple[str, str]]:
    """读取 data 文件夹下所有 txt 教材文件，并保留文件名。"""
    # 同时读取 data/*.txt 和 data/texts/*.txt，供 main.py 和 app.py 构建索引。
    paths = _collect_txt_paths(data_dir)
    text_files: list[tuple[str, str]] = []

    for path in paths:
        text = load_text(path)
        if text:
            text_files.append((path.name, text))

    return text_files
