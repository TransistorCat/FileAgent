from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
import os
from logger import logger
from config import FILE_OPERATIONS
from dotenv import load_dotenv
import os
# 加载 .env 文件
load_dotenv()
class CommandType(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    SEARCH = "search"
    SUMMARIZE = "summarize"

class FileCommand(BaseModel):
    """文件操作命令的结构"""
    type: str = Field(description="操作类型: file_ops 或 search")
    command: CommandType = Field(description="具体的命令类型")
    path: str = Field(description="文件或目录路径")
    content: Optional[str] = Field(None, description="文件内容")
    pattern: Optional[str] = Field(None, description="搜索模式")
    
# 指令模板
INSTRUCTION_TEMPLATE = """你是一个文件操作助手，负责将用户的自然语言指令转换为具体的文件操作命令。

可用的命令类型包括：
- create: 创建新文件
- read: 读取文件内容
- update: 更新文件内容
- delete: 删除文件
- search: 搜索文件

用户指令: {instruction}

请将上述指令解析为结构化的命令。只返回JSON格式的命令，不要包含其他解释。

{format_instructions}
"""

class InstructionParser:
    def __init__(self):
        # 初始化 ChatOpenAI
        self.llm = ChatOpenAI(model=os.environ["LLM_MODELEND"], temperature=0) 
        
        # 创建输出解析器
        self.output_parser = PydanticOutputParser(pydantic_object=FileCommand)
        
        # 创建提示模板
        self.prompt = ChatPromptTemplate.from_template(
            template=INSTRUCTION_TEMPLATE,
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )

    def parse_instruction(self, instruction: str) -> dict:
        """解析自然语言指令"""
        try:
            # 格式化提示
            messages = self.prompt.format_messages(instruction=instruction)
            
            # 获取 LLM 响应
            response = self.llm.invoke(messages)
            
            # 解析响应
            command = self.output_parser.parse(response.content)
            
            # 验证命令
            self._validate_command(command)
            
            return command.model_dump()
            
        except Exception as e:
            logger.error(f"指令解析错误: {str(e)}")
            raise ValueError(f"无法解析指令: {str(e)}")
    
    def _validate_command(self, command: FileCommand):
        """验证命令的合法性"""
        # 检查文件扩展名
        if command.command in [CommandType.CREATE, CommandType.UPDATE]:
            ext = os.path.splitext(command.path)[1].lower()
            if ext not in FILE_OPERATIONS["allowed_extensions"]:
                raise ValueError(f"不支持的文件类型: {ext}")
        
        # 检查路径安全性
        abs_path = os.path.abspath(command.path)
        if ".." in command.path or not abs_path.startswith(os.getcwd()):
            raise ValueError("不允许访问工作目录之外的文件") 