import streamlit as st

from src.chat import create_llm_client, generate_answer
from src.config import load_settings
from src.load_text import load_text_files
from src.split_text import split_text_files
from src.vector_store import build_vector_store, query_collection


@st.cache_resource(show_spinner="正在加载教材并构建向量索引...")
def load_rag_resources():
    """加载教材、构建向量库，并创建大模型客户端。"""
    settings = load_settings(".env")
    client = create_llm_client(settings.api_key, settings.base_url) if settings.api_key else None

    text_files = load_text_files("data")
    paragraphs = split_text_files(text_files)
    collection = build_vector_store(paragraphs, persist_dir="vector_store")

    return settings, client, collection


def answer_question(question: str, collection, client, model: str, provider: str = "openai") -> str:
    """执行向量检索并生成回答。"""
    references = query_collection(collection, question, top_k=3)
    return generate_answer(question, references, client=client, model=model, provider=provider)


def render_app() -> None:
    """渲染 Streamlit 网页界面。"""
    st.title("《钢铁冶金学》教材 RAG 问答助手")

    settings, client, collection = load_rag_resources()

    if client is None:
        st.warning("未检测到大模型 API Key，请在 .env 文件中配置后再提问。")

    question = st.text_area("请输入问题", height=120)
    submitted = st.button("提交")

    if submitted:
        if not question.strip():
            st.warning("请输入问题后再提交。")
            return

        if client is None:
            st.error("当前无法调用大模型：请先在 .env 文件中配置 API Key。")
            return

        with st.spinner("正在检索教材并生成回答..."):
            answer = answer_question(
                question=question.strip(),
                collection=collection,
                client=client,
                model=settings.model,
                provider=settings.provider,
            )

        st.markdown(answer)


if __name__ == "__main__":
    render_app()
