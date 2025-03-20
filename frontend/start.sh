#!/bin/bash

# TouchLink 前端启动脚本
# 用于启动TouchLink前端服务

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 设置目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/frontend.log"

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 函数：杀死占用端口的进程
kill_process_on_port() {
    local port=$1
    echo -e "${YELLOW}检查端口 $port 是否被占用...${NC}"
    
    # 检查操作系统类型
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        local pid=$(lsof -ti:$port)
        if [ -n "$pid" ]; then
            echo -e "${YELLOW}正在杀死占用端口 $port 的进程 $pid${NC}"
            kill -9 $pid
            sleep 1
        else
            echo -e "${GREEN}没有进程占用端口 $port${NC}"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        local pid=$(netstat -tulpn 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1)
        if [ -n "$pid" ] && [ "$pid" != "" ]; then
            echo -e "${YELLOW}正在杀死占用端口 $port 的进程 $pid${NC}"
            kill -9 $pid
            sleep 1
        else
            echo -e "${GREEN}没有进程占用端口 $port${NC}"
        fi
    else
        echo -e "${YELLOW}不支持的操作系统，无法检查端口占用${NC}"
    fi
}

# 函数：启动应用
start_app() {
    echo -e "${GREEN}启动TouchLink前端服务...${NC}"
    echo -e "${GREEN}日志将写入: $LOG_FILE${NC}"
    
    # 切换到前端目录
    cd "$SCRIPT_DIR"
    
    # 检查npm命令
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}错误: 未找到npm命令，请先安装Node.js${NC}"
        exit 1
    fi
    
    # 启动应用
    npm run dev > "$LOG_FILE" 2>&1 &
    
    # 保存PID
    APP_PID=$!
    echo $APP_PID > "$LOG_DIR/app.pid"
    
    echo -e "${GREEN}TouchLink前端服务已启动，PID: $APP_PID${NC}"
    echo -e "${GREEN}前端地址: http://localhost:8000${NC}"
    echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
    
    # 等待用户中断
    wait $APP_PID
}

# 主函数
main() {
    echo -e "${GREEN}===== TouchLink 前端服务 =====${NC}"
    
    # 杀死占用3000端口的进程
    kill_process_on_port 3000
    
    # 启动应用
    start_app
    
    echo -e "${GREEN}TouchLink前端服务已停止${NC}"
}

# 执行主函数
main 