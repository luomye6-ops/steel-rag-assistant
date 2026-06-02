# steel-rag-assistant

## 项目简介

`steel-rag-assistant` 是一个面向《钢铁冶金学》教材检索问答的最小可运行 RAG 项目。项目支持把 PDF 教材导入为文本，切分为 chunks，并使用 Chroma 构建本地向量索引。

当前版本支持命令行和 Streamlit 网页两种问答方式。PDF 导入暂时只读取 PDF 自带文字层，不做 OCR；扫描版或图片型 PDF 需要后续单独增加 OCR 流程。

## 目录结构

```text
steel-rag-assistant/
├── data/
│   ├── pdfs/          # 存放 PDF 教材，例如：钢铁冶金学教程.pdf
│   ├── texts/         # 存放 PDF 提取并清洗后的 txt 文本
│   ├── processed/     # 存放切分后的 chunks.json
│   └── steel_chapter.txt
├── scripts/
│   ├── import_pdf.py
│   └── rebuild_index.py
├── src/
│   ├── pdf_loader.py
│   ├── text_cleaner.py
│   ├── load_text.py
│   ├── split_text.py
│   ├── text_chunk.py
│   ├── vector_store.py
│   ├── retrieve.py
│   ├── config.py
│   └── chat.py
├── tests/
├── vector_store/
├── app.py
├── main.py
├── requirements.txt
└── README.md
```

## 安装依赖

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

复制环境变量示例：

```bash
copy .env.example .env
```

在 `.env` 中配置 OpenAI 或 DeepSeek 的 API Key 和模型名称。

## PDF 导入与索引建立

### 1. 放置 PDF

把 PDF 教材放到：

```text
data/pdfs/
```

例如：

```text
data/pdfs/钢铁冶金学教程.pdf
```

### 2. 导入 PDF 为 txt

```bash
python scripts/import_pdf.py data/pdfs/钢铁冶金学教程.pdf
```

导入完成后会生成：

```text
data/texts/钢铁冶金学教程.txt
```

脚本会输出类似提示：

```text
PDF 导入完成，文本文件保存为 钢铁冶金学教程.txt
```

### 3. 重建 chunks 和向量索引

```bash
python scripts/rebuild_index.py
```

脚本会读取 `data/texts/` 下所有 txt 文件，生成：

```text
data/processed/chunks.json
```

每个 chunk 包含：

```json
{
  "source_file": "钢铁冶金学教程.txt",
  "page": 1,
  "chunk_id": 1,
  "content": "文本片段内容"
}
```

如果项目依赖中的 Chroma 可用，脚本会同时刷新 `vector_store/` 下的本地向量索引。

### 4. 以后导入其他教材

后续导入新教材时按同样流程操作：

```bash
python scripts/import_pdf.py data/pdfs/新教材.pdf
python scripts/rebuild_index.py
```

`main.py` 和 `app.py` 会读取 `data/*.txt` 以及 `data/texts/*.txt`，因此旧的示例文本和新导入教材都可以参与检索。

## 运行问答程序

命令行版本：

```bash
python main.py
```

网页版本：

```bash
streamlit run app.py
```

也可以使用模块方式运行 Streamlit：

```bash
python -m streamlit run app.py
```

## 测试

```bash
python -m unittest discover -s tests
```

## 当前限制

- 暂时不做 OCR，只能提取 PDF 中已有的文字层。
- PDF 提取文本质量取决于原 PDF 的排版和文字层质量。
- `chunks.json` 用于人工检查和后续扩展；问答入口仍使用现有 Chroma 检索流程。
