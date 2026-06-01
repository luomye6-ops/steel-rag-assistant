import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


DEFAULT_MODEL = "gpt-4.1-mini"


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str = DEFAULT_MODEL


def load_settings(env_path: str | Path = ".env") -> Settings:
    """从 .env 文件读取 OpenAI API 配置。"""
    # dotenv 会把 .env 中的配置加载到环境变量，OpenAI SDK 会读取 OPENAI_API_KEY。
    load_dotenv(dotenv_path=env_path)

    return Settings(
        api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        model=os.getenv("OPENAI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL,
    )
