# steel-rag-assistant

## 项目简介

`steel-rag-assistant` 是一个面向《钢铁冶金学》教材检索问答的最小可运行 RAG 项目骨架。当前阶段只使用 `data` 文件夹下的本地 txt 教材文本，通过命令行完成简单问答流程。

当前版本不接入 OpenAI API，不处理 PDF，不包含前端、后端或数据库。

## 当前版本功能

- 读取 `data` 文件夹下的所有 `.txt` 教材文件。
- 对教材文本进行简单清洗，去掉首尾空格并压缩多余空行。
- 按空行将教材文本切分为多个段落。
- 给每个段落添加编号。
- 使用 Chroma 作为本地向量库，将教材段落写入 `vector_store` 文件夹。
- 使用 Chroma 为教材段落和用户问题生成 embedding。
- 用户输入问题后，使用向量检索返回最相关的 3 个教材片段。
- 如果没有明显匹配结果，提示“暂未找到明显相关内容”。
- 根据检索结果拼接模拟回答。
- 支持在命令行中循环提问。
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
│   └── chat.py
├── tests/
│   ├── test_text_pipeline.py
│   └── test_vector_store.py
├── vector_store/
├── .env.example
├── requirements.txt
├── README.md
└── main.py
```

各文件作用：

- `data/steel_chapter.txt`：模拟《钢铁冶金学》教材片段。
- `src/load_text.py`：读取并清洗本地 txt 教材文件。
- `src/split_text.py`：按空行切分教材段落，并为段落添加编号。
- `src/retrieve.py`：保留第一版关键词模拟检索代码。
- `src/vector_store.py`：构建 Chroma 本地向量库，并执行向量检索。
- `src/chat.py`：根据参考片段生成模拟回答。
- `tests/test_text_pipeline.py`：验证教材读取、清洗、切分和编号行为。
- `tests/test_vector_store.py`：验证 Chroma 写入和查询流程的封装逻辑。
- `vector_store/`：运行程序后生成的 Chroma 本地向量索引目录。
- `main.py`：命令行程序入口。
- `.env.example`：后续接入 API 时使用的环境变量示例。
- `requirements.txt`：项目依赖，目前包含 Chroma。

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

运行命令行程序：

```bash
python main.py
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

程序会打印包含“模拟回答”、用户问题、参考教材片段和后续版本提示的回答。

## 后续计划

- 接入真实大模型 API，生成更自然的回答。
- 根据需要评估更多向量检索工具或 embedding 模型。
- 支持 PDF 教材解析和文本清洗。
- 增加更完整的问答评估与测试。
- 根据需要扩展为 Web 前端或后端服务。
