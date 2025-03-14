#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import time
import signal
import re

def kill_process_on_port(port):
    """杀掉占用指定端口的进程"""
    try:
        # 查找占用端口的进程
        cmd = ['lsof', '-i', ':{0}'.format(port)]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print("没有进程占用端口 {0}".format(port))
            return
        
        # 解析输出，提取PID
        lines = stdout.decode('utf-8').strip().split('\n')
        if len(lines) <= 1:  # 只有标题行，没有实际进程
            print("没有进程占用端口 {0}".format(port))
            return
        
        # 从第二行开始解析（第一行是标题）
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 2:
                pid = parts[1]
                try:
                    pid = int(pid)
                    print("正在杀掉进程 {0}，它占用了端口 {1}".format(pid, port))
                    os.kill(pid, signal.SIGKILL)
                    time.sleep(0.5)  # 等待进程被杀掉
                except (ValueError, OSError) as e:
                    print("无法杀掉进程 {0}: {1}".format(pid, str(e)))
    except Exception as e:
        print("检查端口占用时出错: {0}".format(str(e)))

def start_app():
    """启动应用程序"""
    # 设置Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, "src")
    
    # 确保日志目录存在
    log_dir = os.path.join(current_dir, "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 使用固定的日志文件名
    log_file = os.path.join(log_dir, "startup.log")
    
    print("启动应用程序，日志将写入: {0}".format(log_file))
    
    # 设置环境变量
    env = os.environ.copy()
    env["PYTHONPATH"] = "{0}:{1}".format(current_dir, env.get('PYTHONPATH', ''))
    
    # 启动应用程序，将输出重定向到日志文件
    with open(log_file, "w") as f:
        # 使用subprocess运行应用程序
        cmd = ["/Users/construct/miniconda3/envs/touchlink/bin/python", "-m", "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
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
            
    print("应用程序已退出，请查看日志文件: {0}".format(log_file))

if __name__ == "__main__":
    # 先杀掉占用8000端口的进程
    kill_process_on_port(8000)
    
    # 然后启动应用程序
    start_app()