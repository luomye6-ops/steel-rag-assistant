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

    # 同时支持用户输入用空格或标点分开的关键词。
    tokens = re.split(r"[\s，。！？、；：,.!?;:]+", question)
    keywords.extend(token.strip() for token in tokens if len(token.strip()) >= 2)

    # 去重并保留原始顺序。
    return list(dict.fromkeys(keywords))


def retrieve(paragraphs: list[str], question: str, max_results: int = 3) -> list[str]:
    """根据用户问题，从段落中返回最相关的 2 到 3 个教材片段。"""
    keywords = _extract_keywords(question)

    # 问题中没有可用关键词时，返回空列表，由回答层提示未找到内容。
    if not keywords:
        return []

    scored_results: list[tuple[int, int, str]] = []

    for index, paragraph in enumerate(paragraphs):
        # 简单关键词匹配：命中关键词越多，相关性分数越高。
        score = sum(1 for keyword in keywords if keyword in paragraph)
        if score > 0:
            scored_results.append((score, index, paragraph))

    if not scored_results:
        return []

    # 分数高的排前面；分数相同则保持教材原始顺序。
    scored_results.sort(key=lambda item: (-item[0], item[1]))

    return [paragraph for _, _, paragraph in scored_results[:max_results]]
