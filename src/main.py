from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import json
import os
from datetime import datetime
from instruction_parser import InstructionParser
from dotenv import load_dotenv
import re

load_dotenv()

# 定义状态类型
class State(TypedDict):
    input: dict  # 输入参数
    output: dict  # 输出结果
    messages: List[str]  # 操作日志
    error: str | None  # 错误信息
    instruction: str | None  # 原始自然语言指令

# 文件操作模块
def file_operations(state: State) -> State:
    """处理文件基础操作：创建、读取、更新、删除"""
    command = state["input"].get("command")
    path = state["input"].get("path")
    content = state["input"].get("content", "")
    
    try:
        if command == "create":
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            state["messages"].append(f"创建文件: {path}")
            
        elif command == "read":
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                state["output"]["content"] = content
                state["messages"].append(f"读取文件: {path}")
            else:
                raise FileNotFoundError(f"文件不存在: {path}")
                
        elif command == "update":
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            state["messages"].append(f"更新文件: {path}")
            
        elif command == "delete":
            if os.path.exists(path):
                os.remove(path)
                state["messages"].append(f"删除文件: {path}")
            else:
                raise FileNotFoundError(f"文件不存在: {path}")
                
        state["output"]["status"] = "success"
        
    except Exception as e:
        state["error"] = str(e)
        state["output"]["status"] = "error"
        
    return state

# 文件搜索模块
def file_search(state: State) -> State:
    """按文件名、类型等进行搜索"""
    search_path = state["input"].get("path", ".")
    pattern = state["input"].get("pattern", "*")
    
    try:
        results = []
        # 将通配符模式转换为正则表达式
        regex_pattern = pattern.replace(".", "\\.").replace("*", ".*")
        # 确保是完整匹配
        regex_pattern = f"^{regex_pattern}$"
        # 编译正则表达式
        regex = re.compile(regex_pattern)
        
        for root, dirs, files in os.walk(search_path):
            for file in files:
                # 使用正则表达式匹配
                if regex.search(file):
                    file_path = os.path.join(root, file)
                    file_stat = os.stat(file_path)
                    results.append({
                        "name": file,
                        "path": file_path,
                        "size": file_stat.st_size,
                        "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                    })
        
        state["output"]["results"] = results
        state["messages"].append(f"搜索完成，找到 {len(results)} 个文件")
        state["output"]["status"] = "success"
        
    except re.error as e:
        state["error"] = f"无效的正则表达式: {str(e)}"
        state["output"]["status"] = "error"
    except Exception as e:
        state["error"] = str(e)
        state["output"]["status"] = "error"
        
    return state

# 初始化状态
def init_state(state: State) -> State:
    """初始化状态"""
    if "messages" not in state:
        state["messages"] = []
    if "output" not in state:
        state["output"] = {}
    if "error" not in state:
        state["error"] = None
    if "input" not in state:
        state["input"] = {}
    return state

# 添加指令解析节点
def parse_instruction(state: State) -> State:
    """解析自然语言指令"""
    try:
        parser = InstructionParser()
        instruction = state["instruction"]
        
        if not instruction:
            raise ValueError("未提供指令")
            
        # 解析指令
        command = parser.parse_instruction(instruction)
        
        # 更新状态
        state["input"] = command
        state["messages"].append(f"解析指令: {instruction}")
        
    except Exception as e:
        state["error"] = str(e)
        state["messages"].append(f"指令解析失败: {str(e)}")
        
    return state

# 创建工作流图
workflow = StateGraph(State)

# 添加节点
workflow.add_node("init", init_state)
workflow.add_node("file_ops", file_operations)
workflow.add_node("search", file_search)
workflow.add_node("parse", parse_instruction)

# 设置条件路由
def route_to_operation(state: State):
    command_type = state["input"].get("type", "file_ops")
    if command_type == "search":
        return "search"
    return "file_ops"

# 设置节点间的关系 - 修改这部分
workflow.add_conditional_edges(
    "init",
    lambda state: "parse" if state.get("instruction") else route_to_operation(state),
    {
        "parse": "parse"
    }
)

# 从解析节点到操作节点的路由
workflow.add_conditional_edges(
    "parse",
    route_to_operation,
    {
        "search": "search",
        "file_ops": "file_ops"
    }
)

# 添加到终止节点的边
workflow.add_edge("file_ops", END)
workflow.add_edge("search", END)

# 设置入口节点
workflow.set_entry_point("init")

# 编译图
app = workflow.compile()
from IPython.display import Image, display


# 示例运行
if __name__ == "__main__":
    # 创建初始状态
    initial_state = {
        "instruction": "创建一个名为 notes.txt 的文件，内容是'这是一个测试文件'",
        "input": {},
        "output": {},
        "messages": [],
        "error": None
    }
    
    # 运行工作流
    result = app.invoke(initial_state)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 搜索文件示例
    search_state = {
        "instruction": "查找src目录下所有py文件",
        "input": {},
        "output": {},
        "messages": [],
        "error": None
    }
    
    result = app.invoke(search_state)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    try:
        display(Image(app.get_graph().draw_mermaid_png()))
    except Exception:
    # This requires some extra dependencies and is optional
        pass