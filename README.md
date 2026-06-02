# steel-rag-assistant

## 项目简介

`steel-rag-assistant` 是一个面向《钢铁冶金学》教材内容的本地 RAG 问答项目。项目可以读取本地教材文本，构建 Chroma 向量索引，并通过命令行或 Streamlit 页面进行基于教材片段的问答。

当前版本支持 PDF 教材导入，但仅提取 PDF 自带文字层，暂时不支持 OCR。因此，扫描版或图片型 PDF 的解析效果取决于原文件是否包含可提取文本。

## 项目截图

截图位置预留：

```text
docs/screenshots/
```

后续可放置：

- `docs/screenshots/streamlit-home.png`
- `docs/screenshots/answer-example.png`
- `docs/screenshots/chunks-json.png`

## 功能列表

- 读取本地 `.txt` 教材文本。
- 导入 PDF 教材并提取为 `.txt` 文本。
- 在 PDF 提取文本中保留页码标记，例如 `【第 1 页】`。
- 清洗教材文本中的多余空行和首尾空格。
- 将教材文本切分为 chunks。
- 为 chunk 保存来源文件、页码、片段编号和正文内容。
- 生成 `data/processed/chunks.json`，便于检查切分结果。
- 使用 Chroma 构建本地向量索引。
- 支持命令行问答入口 `main.py`。
- 支持 Streamlit 网页问答入口 `app.py`。
- 支持 OpenAI 或 DeepSeek 作为大模型服务。

## 技术栈

- Python
- PyMuPDF：PDF 文本提取
- Chroma：本地向量数据库
- OpenAI Python SDK：调用 OpenAI / DeepSeek 兼容接口
- Streamlit：网页问答界面
- python-dotenv：读取 `.env` 配置
- unittest：单元测试

## 项目结构

```text
steel-rag-assistant/
├── app.py                     # Streamlit 网页入口
├── main.py                    # 命令行问答入口
├── requirements.txt           # Python 依赖
├── README.md
├── .env.example               # 环境变量示例
├── data/
│   ├── pdfs/                  # 存放 PDF 教材
│   ├── texts/                 # 存放 PDF 提取后的 txt 文本
│   ├── processed/             # 存放 chunks.json
│   └── steel_chapter.txt      # 示例教材文本
├── scripts/
│   ├── import_pdf.py          # PDF 导入脚本
│   └── rebuild_index.py       # 重建 chunks 和向量索引脚本
├── src/
│   ├── chat.py                # 大模型问答逻辑
│   ├── chunk_store.py         # chunks.json 读写
│   ├── config.py              # 配置读取
│   ├── load_text.py           # txt 教材读取
│   ├── pdf_loader.py          # PDF 文本提取
│   ├── retrieve.py            # 简单检索逻辑
│   ├── split_text.py          # 文本切分
│   ├── text_chunk.py          # chunk 数据结构
│   ├── text_cleaner.py        # PDF 文本清洗
│   └── vector_store.py        # Chroma 索引构建和查询
├── tests/                     # 单元测试
├── vector_store/              # Chroma 本地索引目录
└── docs/
    └── screenshots/           # 项目截图位置预留
```

## 安装方法

进入项目目录：

```bash
cd steel-rag-assistant
```

创建并激活虚拟环境：

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

安装依赖：

```bash
python -m pip install -r requirements.txt
```

复制环境变量文件：

```bash
copy .env.example .env
```

根据使用的服务商编辑 `.env`。

OpenAI 示例：

```text
LLM_PROVIDER=openai
OPENAI_API_KEY=你的_API_Key
OPENAI_MODEL=gpt-4.1-mini
```

DeepSeek 示例：

```text
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的_DeepSeek_API_Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

## 运行方法

命令行版本：

```bash
python main.py
```

网页版本：

```bash
streamlit run app.py
```

如果 Streamlit 命令不可用，可以使用：

```bash
python -m streamlit run app.py
```

运行测试：

```bash
python -m unittest discover -s tests
```

## 使用说明

### 导入 PDF 教材

将 PDF 放入：

```text
data/pdfs/
```

示例：

```text
data/pdfs/钢铁冶金学教程.pdf
```

运行导入脚本：

```bash
python scripts/import_pdf.py data/pdfs/钢铁冶金学教程.pdf
```

导入后会生成：

```text
data/texts/钢铁冶金学教程.txt
```

### 重建索引

导入 PDF 后，运行：

```bash
python scripts/rebuild_index.py
```

脚本会读取 `data/texts/` 下的所有 `.txt` 文件，生成：

```text
data/processed/chunks.json
```

同时会刷新本地 Chroma 索引目录：

```text
vector_store/
```

### 开始问答

索引建立后，可以运行命令行或网页版本进行提问。回答会基于检索到的教材片段生成，并显示参考来源。

### 导入其他教材

后续新增教材时，重复以下流程：

```bash
python scripts/import_pdf.py data/pdfs/新教材.pdf
python scripts/rebuild_index.py
```

## 后续计划

- 增加 OCR 支持，用于处理扫描版 PDF。
- 改进 PDF 文本清洗规则，过滤固定水印、页眉和页脚。
- 优化 chunk 切分策略，减少过短或噪声片段。
- 增加更完整的检索与问答效果评估。
- 补充 Streamlit 页面截图和使用示例。
- 根据需要扩展为更完整的 Web 服务。

## 当前限制

- 不支持 OCR。
- PDF 解析质量依赖原 PDF 的文字层质量。
- 当前项目主要用于本地教材问答实验，不包含用户登录、权限管理或在线部署配置。
