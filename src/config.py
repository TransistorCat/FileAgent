import os
from pathlib import Path

# 基础配置
BASE_DIR = Path(__file__).parent.parent
WORKSPACE_DIR = BASE_DIR / "workspace"

# 创建工作目录
os.makedirs(WORKSPACE_DIR, exist_ok=True)

# 文件操作配置
FILE_OPERATIONS = {
    "max_file_size": 100 * 1024 * 1024,  # 最大文件大小限制：100MB
    "allowed_extensions": [".txt", ".md", ".pdf", ".doc", ".docx"],  # 允许的文件类型
}

# 搜索配置
SEARCH_CONFIG = {
    "max_depth": 5,  # 最大搜索深度
    "exclude_dirs": [".git", "__pycache__", "node_modules"],  # 排除的目录
}

# 日志配置
LOG_CONFIG = {
    "log_file": BASE_DIR / "logs" / "file_agent.log",
    "max_log_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5,
}

# 创建日志目录
os.makedirs(BASE_DIR / "logs", exist_ok=True) 