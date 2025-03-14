#!/usr/bin/env python
import os
import re

def fix_imports(directory):
    """修复目录中所有Python文件的导入路径"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                fix_file_imports(file_path)

def fix_file_imports(file_path):
    """修复单个文件的导入路径"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # 定义需要修复的导入模式
    patterns = [
        (r'from (api|config|core|schemas|utils)\.', r'from src.\1.'),
        (r'import (api|config|core|schemas|utils)\.', r'import src.\1.'),
    ]
    
    # 应用修复
    modified = False
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
    
    # 如果文件被修改，则写回
    if modified:
        print(f"修复文件: {file_path}")
        with open(file_path, 'w') as f:
            f.write(content)

if __name__ == "__main__":
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
    fix_imports(src_dir)
    print("导入路径修复完成!") 