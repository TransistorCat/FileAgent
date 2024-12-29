from typing import Dict, Any
import os
from dotenv import load_dotenv
# 加载 .env 文件
load_dotenv()

def load_config() -> Dict[str, Any]:

    """加载配置"""
    return {
        "llm": {
            "model": os.environ.get("LLM_MODELEND"),
            "temperature": float(os.environ.get("LLM_TEMPERATURE", "0.7"))
        },
        "file_operations": {
            "allowed_extensions": [".txt", ".md", ".pdf"],
            "max_file_size": 10 * 1024 * 1024  # 10MB
        }
    } 