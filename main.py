from src.chat import create_llm_client, generate_answer
from src.config import load_settings
from src.load_text import load_text_files
from src.split_text import split_text_files
from src.vector_store import build_vector_store, query_collection


def main() -> None:
    """命令行入口函数。"""
    print("《钢铁冶金学》教材 RAG 问答助手已启动")
    print("请输入问题，输入 exit 或 quit 退出。")

    # 从 .env 文件读取大模型 API Key、服务商和模型名称。
    settings = load_settings(".env")
    client = create_llm_client(settings.api_key, settings.base_url) if settings.api_key else None

    if client is None:
        print("提示：未检测到大模型 API Key，请在 .env 文件中配置后再提问。")

    # 启动时读取 data 文件夹下所有 txt 教材，并切分为带来源信息的段落。
    text_files = load_text_files("data")
    paragraphs = split_text_files(text_files)

    # 将教材段落写入 Chroma，本地向量索引会保存到 vector_store 文件夹。
    collection = build_vector_store(paragraphs, persist_dir="vector_store")

    while True:
        # 获取用户输入的问题。
        question = input("\n请输入问题：").strip()

        # 用户输入 exit 或 quit 时退出程序。
        if question.lower() in {"exit", "quit"}:
            print("程序已退出。")
            break

        # 空问题不处理，提示用户重新输入。
        if not question:
            print("问题不能为空，请重新输入。")
            continue

        if client is None:
            print("当前无法调用大模型：请先在 .env 文件中配置 API Key。")
            continue

        # 使用 Chroma 向量检索最相关的 3 个教材片段。
        references = query_collection(collection, question, top_k=3)
        answer = generate_answer(
            question,
            references,
            client=client,
            model=settings.model,
            provider=settings.provider,
        )
        print("\n" + answer)


if __name__ == "__main__":
    main()
