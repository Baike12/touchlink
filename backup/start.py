#!/usr/bin/env python
import os
import sys
import subprocess

# 设置Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")

# 确保日志目录存在
log_dir = os.path.join(current_dir, "logs")
os.makedirs(log_dir, exist_ok=True)

# 使用固定的日志文件名
log_file = os.path.join(log_dir, "startup.log")

print(f"启动应用程序，日志将写入: {log_file}")

# 设置环境变量
env = os.environ.copy()
env["PYTHONPATH"] = f"{current_dir}:{env.get('PYTHONPATH', '')}"

# 启动应用程序，将输出重定向到日志文件
with open(log_file, "w") as f:
    # 使用subprocess运行应用程序
    cmd = ["python", "-m", "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    process = subprocess.Popen(
        cmd,
        stdout=f,
        stderr=subprocess.STDOUT,
        cwd=current_dir,
        env=env
    )
    
    try:
        # 等待进程完成
        process.wait()
    except KeyboardInterrupt:
        print("接收到中断信号，正在关闭应用程序...")
        process.terminate()
        process.wait()
        
print(f"应用程序已退出，请查看日志文件: {log_file}") 