import os
import shutil
from typing import Dict, Any, Optional
from langchain_core.tools import tool

class FileTools:
    @tool("create_file")
    def create_file(file_name: str, content: str = "") -> str:
        """创建一个新文件。
        
        Args:
            file_name: 要创建的文件名
            content: 文件内容，默认为空
        Returns:
            str: 操作结果信息
        """
        try:
            # 确保父目录存在
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"文件 {file_name} 创建成功"
        except Exception as e:
            return f"创建文件失败: {str(e)}"
    
    @tool("create_directory")
    def create_directory(directory_path: str) -> str:
        """创建一个新文件夹。
        
        Args:
            directory_path: 要创建的文件夹路径
        Returns:
            str: 操作结果信息
        """
        try:
            os.makedirs(directory_path, exist_ok=True)
            return f"文件夹 {directory_path} 创建成功"
        except Exception as e:
            return f"创建文件夹失败: {str(e)}"
    
    @tool("delete_file")
    def delete_file(file_path: str) -> str:
        """删除文件。
        
        Args:
            file_path: 要删除的文件路径
        Returns:
            str: 操作结果信息
        """
        try:
            if not os.path.exists(file_path):
                return f"错误：文件 {file_path} 不存在"
            if os.path.isdir(file_path):
                return f"错误：{file_path} 是一个文件夹，请使用 delete_directory"
            
            os.remove(file_path)
            return f"文件 {file_path} 删除成功"
        except Exception as e:
            return f"删除文件失败: {str(e)}"
    
    @tool("delete_directory")
    def delete_directory(directory_path: str, recursive: bool = True) -> str:
        """删除文件夹。
        
        Args:
            directory_path: 要删除的文件夹路径
            recursive: 是否递归删除所有内容，默认为True
        Returns:
            str: 操作结果信息
        """
        try:
            if not os.path.exists(directory_path):
                return f"错误：文件夹 {directory_path} 不存在"
            if not os.path.isdir(directory_path):
                return f"错误：{directory_path} 不是一个文件夹"
            
            if recursive:
                shutil.rmtree(directory_path)
            else:
                os.rmdir(directory_path)
            return f"文件夹 {directory_path} 删除成功"
        except Exception as e:
            return f"删除文件夹失败: {str(e)}"
    
    @tool("rename_file")
    def rename_file(old_path: str, new_path: str) -> str:
        """重命名文件或文件夹。
        
        Args:
            old_path: 原路径
            new_path: 新路径
        Returns:
            str: 操作结果信息
        """
        try:
            if not os.path.exists(old_path):
                return f"错误：{old_path} 不存在"
            if os.path.exists(new_path):
                return f"错误：{new_path} 已存在"
            
            os.rename(old_path, new_path)
            type_str = "文件夹" if os.path.isdir(new_path) else "文件"
            return f"{type_str}从 {old_path} 重命名为 {new_path} 成功"
        except Exception as e:
            return f"重命名失败: {str(e)}"
    
    @tool("move_item")
    def move_item(source_path: str, destination_path: str) -> str:
        """移动文件或文件夹到新位置。
        
        Args:
            source_path: 源路径
            destination_path: 目标路径
        Returns:
            str: 操作结果信息
        """
        try:
            if not os.path.exists(source_path):
                return f"错误：{source_path} 不存在"
            
            # 确保目标父目录存在
            destination_dir = os.path.dirname(destination_path)
            if destination_dir:
                os.makedirs(destination_dir, exist_ok=True)
            
            if os.path.exists(destination_path):
                return f"错误：目标路径 {destination_path} 已存在"
            
            shutil.move(source_path, destination_path)
            type_str = "文件夹" if os.path.isdir(destination_path) else "文件"
            return f"{type_str}从 {source_path} 移动到 {destination_path} 成功"
        except Exception as e:
            return f"移动失败: {str(e)}"
    
    @tool("read_file")
    def read_file(file_name: str) -> str:
        """读取文件内容。
        
        Args:
            file_name: 要读取的文件名
        Returns:
            str: 文件内容或错误信息
        """
        try:
            if not os.path.exists(file_name):
                return f"错误：文件 {file_name} 不存在"
            if os.path.isdir(file_name):
                return f"错误：{file_name} 是一个文件夹"
                
            with open(file_name, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"读取文件失败: {str(e)}"
    
    @tool("list_directory")
    def list_directory(directory_path: str = ".") -> str:
        """列出指定目录下的所有文件和文件夹。
        
        Args:
            directory_path: 要列出内容的目录路径，默认为当前目录
        Returns:
            str: 目录内容列表
        """
        try:
            if not os.path.exists(directory_path):
                return f"错误：目录 {directory_path} 不存在"
            if not os.path.isdir(directory_path):
                return f"错误：{directory_path} 不是一个目录"
            
            items = os.listdir(directory_path)
            files = []
            directories = []
            
            for item in items:
                full_path = os.path.join(directory_path, item)
                if os.path.isdir(full_path):
                    directories.append(f"📁 {item}/")
                else:
                    files.append(f"📄 {item}")
            
            result = f"目录 {directory_path} 的内容：\n"
            if directories:
                result += "\n文件夹:\n" + "\n".join(sorted(directories))
            if files:
                result += "\n\n文件:\n" + "\n".join(sorted(files))
            return result
        except Exception as e:
            return f"列出目录内容失败: {str(e)}"
    
    @tool("count_files")
    def count_files(directory_path: str = ".") -> str:
        """统计指定目录中的文件和文件夹数量。
        
        Args:
            directory_path: 要统计的目录路径，默认为当前目录
        Returns:
            str: 包含文件和文件夹数量的信息
        """
        try:
            if not os.path.exists(directory_path):
                return f"错误：目录 {directory_path} 不存在"
            if not os.path.isdir(directory_path):
                return f"错误：{directory_path} 不是一个目录"
            
            items = os.listdir(directory_path)
            files = []
            directories = []
            
            for item in items:
                full_path = os.path.join(directory_path, item)
                if os.path.isdir(full_path):
                    directories.append(item)
                else:
                    files.append(item)
            
            return f"目录 {directory_path} 中包含 {len(files)} 个文件和 {len(directories)} 个文件夹"
        except Exception as e:
            return f"统计目录内容失败: {str(e)}" 