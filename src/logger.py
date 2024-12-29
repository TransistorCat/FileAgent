import logging
from logging.handlers import RotatingFileHandler
from config import LOG_CONFIG
import os

def setup_logger():
    logger = logging.getLogger('FileAgent')
    logger.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 文件处理器
    file_handler = RotatingFileHandler(
        LOG_CONFIG["log_file"],
        maxBytes=LOG_CONFIG["max_log_size"],
        backupCount=LOG_CONFIG["backup_count"]
    )
    file_handler.setFormatter(formatter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger() 