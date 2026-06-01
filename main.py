from src.chat import generate_answer
from src.load_text import load_texts_from_data
from src.retrieve import retrieve
from src.split_text import split_text


def main() -> None:
    """命令行入口函数。"""
    print("《钢铁冶金学》教材 RAG 问答助手已启动")
    print("请输入问题，输入 exit 或 quit 退出。")

    # 启动时读取 data 文件夹下所有 txt 教材，并切分为带编号的段落。
    text = load_texts_from_data("data")
    paragraphs = split_text(text)

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

        # 执行模拟检索并生成模拟回答。
        references = retrieve(paragraphs, question)
        answer = generate_answer(question, references)
        print("\n" + answer)


if __name__ == "__main__":
    main()
