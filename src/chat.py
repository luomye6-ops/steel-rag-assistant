from typing import Any

from src.config import DEFAULT_MODEL


NO_CLEAR_ANSWER_MESSAGE = "当前教材内容中没有找到明确答案"


def create_openai_client(api_key: str) -> Any:
    """创建 OpenAI 客户端。"""
    from openai import OpenAI

    return OpenAI(api_key=api_key)


def _build_model_input(question: str, references: list[str]) -> str:
    """把用户问题和检索片段组织成发送给大模型的输入。"""
    reference_text = "\n\n".join(references)
    return (
        f"用户问题：{question}\n\n"
        "检索到的教材片段：\n"
        f"{reference_text}\n\n"
        "请根据上述教材片段回答用户问题。"
    )


def generate_answer(
    question: str,
    references: list[str],
    client: Any | None = None,
    model: str = DEFAULT_MODEL,
) -> str:
    """根据检索片段调用大模型生成回答，并保留参考教材片段。"""
    if not references:
        return (
            f"大模型回答：\n{NO_CLEAR_ANSWER_MESSAGE}\n\n"
            "参考教材片段：\n"
            f"{NO_CLEAR_ANSWER_MESSAGE}"
        )

    if client is None:
        raise ValueError("调用大模型前需要提供 OpenAI client。")

    instructions = (
        "你是《钢铁冶金学》教材问答助手。"
        "回答必须基于教材片段，不要使用教材片段之外的知识。"
        f"如果教材片段无法支持明确回答，直接回答“{NO_CLEAR_ANSWER_MESSAGE}”。"
    )

    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=_build_model_input(question, references),
    )

    reference_text = "\n\n".join(references)
    return (
        f"大模型回答：\n{response.output_text}\n\n"
        "参考教材片段：\n"
        f"{reference_text}"
    )
