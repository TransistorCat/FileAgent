from typing import Dict, Any
from tools.file_tools import FileTools

class FileAgent:
    @staticmethod
    def parse_command(state: Dict[str, Any]) -> Dict[str, Any]:
        """解析用户命令"""
        command = state["command"]
        # TODO: 使用 LLM 解析命令，确定要使用的工具和参数
        parsed_command = {
            "tool": "create_file",
            "params": {"filename": "test.txt"}
        }
        
        return {
            **state,
            "parsed_command": parsed_command
        }
    
    @staticmethod
    def execute_command(state: Dict[str, Any]) -> Dict[str, Any]:
        """执行解析后的命令"""
        parsed_command = state["parsed_command"]
        tool_name = parsed_command["tool"]
        params = parsed_command["params"]
        
        # 执行工具调用
        result = getattr(FileTools, tool_name)(**params)
        
        return {
            **state,
            "tools_output": result
        } 