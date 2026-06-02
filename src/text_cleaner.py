def clean_pdf_text(text: str) -> str:
    """清洗 PDF 提取文本，去掉多余空行和首尾空格。"""
    # 统一换行符，方便在 Windows 和其他系统上得到一致结果。
    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned_lines: list[str] = []

    for line in normalized_text.split("\n"):
        stripped_line = line.strip()

        # 空行最多保留一行，用来维持章节标题和正文段落之间的分隔。
        if not stripped_line:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue

        # 非空行只去掉首尾空格，不改动行内文字，尽量保留章节标题格式。
        cleaned_lines.append(stripped_line)

    return "\n".join(cleaned_lines).strip()
