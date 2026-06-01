# steel-rag-assistant

## 项目简介

`steel-rag-assistant` 是一个面向《钢铁冶金学》教材检索问答的最小可运行 RAG 项目骨架。当前阶段只使用 `data` 文件夹下的本地 txt 教材文本，通过命令行完成简单问答流程。

当前版本支持 OpenAI 或 DeepSeek API 生成基于教材片段的回答，支持命令行和 Streamlit 网页两种运行方式，不处理 PDF，不包含用户登录或数据库。

## 当前版本功能

- 读取 `data` 文件夹下的所有 `.txt` 教材文件。
- 对教材文本进行简单清洗，去掉首尾空格并压缩多余空行。
- 按空行将教材文本切分为多个段落。
- 给每个段落添加编号，并保留来源文件名。
- 使用 Chroma 作为本地向量库，将教材段落写入 `vector_store` 文件夹。
- 使用 Chroma 为教材段落和用户问题生成 embedding。
- 用户输入问题后，使用向量检索返回最相关的 3 个教材片段。
- 将用户问题和检索到的教材片段一起发送给大模型。
- 大模型回答必须基于教材片段。
- 如果教材片段中没有明确答案，提示“当前教材内容中没有找到明确答案”。
- 回答中保留“参考教材片段”。
- 回答末尾显示“参考来源”，格式为 `steel_chapter.txt，第 3 段`。
- 支持在命令行中循环提问。
- 支持 Streamlit 网页界面，包含问题输入框、提交按钮、回答内容、参考教材片段和来源显示。
- 输入 `exit` 或 `quit` 退出程序。

## 文件结构说明

```text
steel-rag-assistant/
├── data/
│   └── steel_chapter.txt
├── src/
│   ├── __init__.py
│   ├── load_text.py
│   ├── split_text.py
│   ├── retrieve.py
│   ├── vector_store.py
│   ├── text_chunk.py
│   ├── config.py
│   └── chat.py
├── tests/
│   ├── test_llm_answer.py
│   ├── test_text_pipeline.py
│   └── test_vector_store.py
├── vector_store/
├── .env.example
├── app.py
├── requirements.txt
├── README.md
└── main.py
```

各文件作用：

- `data/steel_chapter.txt`：模拟《钢铁冶金学》教材片段。
- `src/load_text.py`：读取并清洗本地 txt 教材文件。
- `src/split_text.py`：按空行切分教材段落，并为段落添加编号和来源文件名。
- `src/text_chunk.py`：定义教材片段的数据结构，保存正文、来源文件名和段落编号。
- `src/retrieve.py`：保留第一版关键词模拟检索代码。
- `src/vector_store.py`：构建 Chroma 本地向量库，并执行向量检索。
- `src/config.py`：从 `.env` 文件读取 OpenAI API Key 和模型配置。
- `src/chat.py`：调用 OpenAI 大模型，根据参考片段生成回答。
- `tests/test_llm_answer.py`：验证大模型调用输入、无片段提示和 `.env` 配置读取。
- `tests/test_text_pipeline.py`：验证教材读取、清洗、切分和编号行为。
- `tests/test_vector_store.py`：验证 Chroma 写入和查询流程的封装逻辑。
- `vector_store/`：运行程序后生成的 Chroma 本地向量索引目录。
- `main.py`：命令行程序入口。
- `app.py`：Streamlit 网页入口。
- `.env.example`：OpenAI API Key 和模型名称配置示例。
- `requirements.txt`：项目依赖，目前包含 Chroma、OpenAI SDK、python-dotenv 和 Streamlit。

## 如何运行

进入项目目录：

```bash
cd steel-rag-assistant
```

安装依赖：

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

创建 `.env` 文件：

```bash
copy .env.example .env
```

如果使用 OpenAI，编辑 `.env`：

```text
LLM_PROVIDER=openai
OPENAI_API_KEY=你的_API_Key
OPENAI_MODEL=gpt-4.1-mini
```

如果使用 DeepSeek，编辑 `.env`：

```text
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的_DeepSeek_API_Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

运行命令行程序：

```bash
python main.py
```

运行网页版本：

```bash
streamlit run app.py
```

也可以使用 Python 模块方式运行：

```bash
python -m streamlit run app.py
```

## 如何测试

运行标准库单元测试：

```bash
python -m unittest discover -s tests
```

## 运行成功后应该看到什么

程序启动后会显示：

```text
《钢铁冶金学》教材 RAG 问答助手已启动
请输入问题，输入 exit 或 quit 退出。
```

然后可以输入问题，例如：

```text
请输入问题：焦炭在高炉中有什么作用？
```

程序会先用 Chroma 检索教材片段，再调用大模型生成基于教材片段的回答，并显示“参考教材片段”和“参考来源”。

参考来源示例：

```text
参考来源：
- steel_chapter.txt，第 3 段
```

网页版本启动后，在浏览器中打开 Streamlit 提供的本地地址，通常是：

```text
http://localhost:8501
```

## 后续计划

- 根据需要评估更多向量检索工具或 embedding 模型。
- 支持 PDF 教材解析和文本清洗。
- 增加更完整的问答评估与测试。
- 根据需要扩展为 Web 前端或后端服务。
