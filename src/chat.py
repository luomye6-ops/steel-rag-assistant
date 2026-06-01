def generate_answer(question: str, references: list[str]) -> str:
    """根据检索到的教材片段拼接一个模拟回答。"""
    # 没有检索结果时，给出明确提示，而不是编造答案。
    reference_text = "\n\n".join(references) if references else "暂未找到明显相关内容"

    # 第一版不调用大模型，只返回结构化的模拟回答。
    return (
        "模拟回答\n"
        f"用户问题：{question}\n\n"
        "参考教材片段：\n"
        f"{reference_text}\n\n"
        "提示：后续版本会接入真正的 RAG 和大模型回答。"
    )
