#!/usr/bin/env python
import os
import re

def fix_imports(directory):
    """
    修复指定目录下所有Python文件中的导入语句
    将 'from backend.src' 替换为 'from src'
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 替换导入语句
                new_content = re.sub(
                    r'from backend\.src\.', 
                    'from src.',
                    content
                )
                
                # 如果内容有变化，写回文件
                if new_content != content:
                    print(f"Fixing imports in {file_path}")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

if __name__ == '__main__':
    # 修复src目录下的所有Python文件
    fix_imports('src')
    print("导入路径修复完成!") 