from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph, MessagesState, END
from langgraph.prebuilt import tools_condition, ToolNode
from dotenv import load_dotenv
from config.settings import load_config
from tools.file_tools import FileTools
import os

# 加载环境变量

def create_workflow():
    """创建文件操作工作流"""
    # 初始化 LLM
    llm = ChatOpenAI(
        model=load_config()["llm"]["model"],
        temperature=0.7
    )
    
    # 准备文件操作工具
    tools = [
        FileTools.create_file,
        FileTools.create_directory,
        FileTools.read_file,
        FileTools.delete_file,
        FileTools.delete_directory,
        FileTools.rename_file,
        FileTools.move_item,
        FileTools.list_directory,
    ]
    
    # 绑定工具到 LLM
    llm_with_tools = llm.bind_tools(tools)
    
    # 系统提示信息
    sys_msg = SystemMessage(
        content="""你是一个文件操作助手，可以执行创建、读取、编辑等文件操作。

    可用的工具：
    - create_file: 创建文件
    - create_directory: 创建文件夹
    - read_file: 读取文件内容
    - delete_file: 删除文件
    - delete_directory: 删除文件夹
    - rename_file: 重命名文件或文件夹
    - move_item: 移动文件或文件夹
    - list_directory: 列出目录内容

    当需要了解目录中的文件数量时，使用 list_directory 工具，它会返回目录中的所有内容。
    你可以直接从返回的结果中计算文件数量，无需多次调用。

    请记住：
    1. list_directory 的结果中包含了完整的文件列表
    2. 文件前有 📄 标记，文件夹前有 📁 标记
    3. 统计文件数量时只需查看一次目录内容即可
"""
    )
    
    # 定义助手节点
    def assistant(state: MessagesState):
        messages = [sys_msg] + state["messages"]
        response = llm_with_tools.invoke(messages)
        
        # 如果响应中包含工具调用结果，将其作为系统消息添加到上下文
        # if hasattr(response, 'additional_kwargs') and 'tool_calls' in response.additional_kwargs:
        #     tool_calls = response.additional_kwargs['tool_calls']
        #     for tool_call in tool_calls:
        #         if tool_call.get('function', {}).get('name') == 'list_directory':
        #             context_msg = SystemMessage(content=f"目录内容上下文：\n{tool_call.get('function', {}).get('output', '')}")
        #             messages.append(context_msg)
        print(messages)
        return {"messages": messages + [response]}
    
    # 构建工作流图
    builder = StateGraph(MessagesState)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))
    
    # 添加边
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
    )
    builder.add_edge("tools", "assistant")
    builder.add_edge("assistant", END)
    
    return builder.compile()

def main():
    # 创建工作流
    workflow = create_workflow()
    
    # 存储对话历史
    conversation_history = []
    
    while True:
        # 获取用户输入
        content = input("\n请输入指令（输入 'exit' 退出）：").strip()
        
        if content.lower() == 'exit':
            print("再见！")
            break
            
        if not content:
            continue
        
        # 添加用户消息到历史记录
        conversation_history.append(HumanMessage(content=content))
        
        try:
            # 执行工作流
            result = workflow.invoke({"messages": conversation_history})
            
            # 更新对话历史
            conversation_history = result["messages"]
            
            # 打印结果
            for message in result["messages"]:
                if isinstance(message, (AIMessage, SystemMessage)):
                    print(f"\n{message.type}: {message.content}")
        except Exception as e:
            print(f"\n发生错误: {str(e)}")

if __name__ == "__main__":
    main() 