import re


DOMAIN_KEYWORDS = [
    "高炉炼铁",
    "高炉",
    "炼铁",
    "焦炭",
    "炉渣",
    "转炉炼钢",
    "转炉",
    "炼钢",
    "氧气",
    "铁水",
    "还原",
    "一氧化碳",
    "作用",
    "原理",
    "过程",
]


def _extract_keywords(question: str) -> list[str]:
    """从用户问题中提取简单关键词。"""
    # 优先匹配教材领域内常见词，适合第一版关键词检索。
    keywords = [word for word in DOMAIN_KEYWORDS if word in question]

    # 同时支持用户输入用空格分开的关键词。
    tokens = re.split(r"[\s，。！？、；：,.!?;:]+", question)
    keywords.extend(token for token in tokens if len(token) >= 2)

    # 去重并保留原始顺序。
    return list(dict.fromkeys(keywords))


def retrieve(paragraphs: list[str], question: str, default_count: int = 2) -> list[str]:
    """根据用户问题，从段落中查找包含关键词的内容。"""
    keywords = _extract_keywords(question)

    # 如果问题中没有可用关键词，直接返回默认参考段落。
    if not keywords:
        return paragraphs[:default_count]

    # 查找包含任意关键词的段落，作为模拟检索结果。
    results = [
        paragraph
        for paragraph in paragraphs
        if any(keyword in paragraph for keyword in keywords)
    ]

    # 没有匹配结果时，返回前 1 到 2 个段落作为默认参考内容。
    if not results:
        return paragraphs[:default_count]

    return results
