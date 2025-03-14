#!/bin/bash

# TouchLink 主启动脚本
# 用于同时启动TouchLink前端和后端服务

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 设置目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
LOG_DIR="$SCRIPT_DIR/logs"

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 函数：启动后端
start_backend() {
    echo -e "${GREEN}启动TouchLink后端服务...${NC}"
    
    # 检查后端启动脚本是否存在
    if [ ! -f "$BACKEND_DIR/start.sh" ]; then
        echo -e "${RED}错误: 未找到后端启动脚本 $BACKEND_DIR/start.sh${NC}"
        return 1
    fi
    
    # 给脚本添加执行权限
    chmod +x "$BACKEND_DIR/start.sh"
    
    # 启动后端
    "$BACKEND_DIR/start.sh" &
    
    # 等待后端启动
    echo -e "${YELLOW}等待后端服务启动...${NC}"
    sleep 3
    
    # 检查后端是否成功启动
    if curl -s "http://localhost:8000/api/v1/datasources/" > /dev/null; then
        echo -e "${GREEN}后端服务已成功启动${NC}"
        return 0
    else
        echo -e "${YELLOW}后端服务可能需要更长时间启动，继续等待...${NC}"
        sleep 5
        if curl -s "http://localhost:8000/api/v1/datasources/" > /dev/null; then
            echo -e "${GREEN}后端服务已成功启动（延迟）${NC}"
            return 0
        else
            echo -e "${RED}后端服务启动可能失败，请检查日志${NC}"
            return 1
        fi
    fi
}

# 函数：启动前端
start_frontend() {
    echo -e "${GREEN}启动TouchLink前端服务...${NC}"
    
    # 检查前端启动脚本是否存在
    if [ ! -f "$FRONTEND_DIR/start.sh" ]; then
        echo -e "${RED}错误: 未找到前端启动脚本 $FRONTEND_DIR/start.sh${NC}"
        return 1
    fi
    
    # 给脚本添加执行权限
    chmod +x "$FRONTEND_DIR/start.sh"
    
    # 启动前端
    "$FRONTEND_DIR/start.sh" &
    
    # 等待前端启动
    echo -e "${YELLOW}等待前端服务启动...${NC}"
    sleep 5
    
    # 检查前端是否成功启动
    if curl -s "http://localhost:3000/" > /dev/null; then
        echo -e "${GREEN}前端服务已成功启动${NC}"
        return 0
    else
        echo -e "${YELLOW}前端服务可能需要更长时间启动，继续等待...${NC}"
        sleep 5
        if curl -s "http://localhost:3000/" > /dev/null; then
            echo -e "${GREEN}前端服务已成功启动（延迟）${NC}"
            return 0
        else
            echo -e "${RED}前端服务启动可能失败，请检查日志${NC}"
            return 1
        fi
    fi
}

# 函数：打开浏览器
open_browser() {
    echo -e "${GREEN}正在打开浏览器...${NC}"
    
    # 检查操作系统类型
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open "http://localhost:3000/"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v xdg-open &> /dev/null; then
            xdg-open "http://localhost:3000/"
        elif command -v gnome-open &> /dev/null; then
            gnome-open "http://localhost:3000/"
        else
            echo -e "${YELLOW}无法自动打开浏览器，请手动访问 http://localhost:3000/${NC}"
        fi
    else
        echo -e "${YELLOW}不支持的操作系统，无法自动打开浏览器${NC}"
        echo -e "${YELLOW}请手动访问 http://localhost:3000/${NC}"
    fi
}

# 主函数
main() {
    echo -e "${GREEN}===== TouchLink 启动脚本 =====${NC}"
    
    # 启动后端
    start_backend
    BACKEND_STATUS=$?
    
    # 启动前端
    start_frontend
    FRONTEND_STATUS=$?
    
    # 如果前端和后端都启动成功，打开浏览器
    if [ $BACKEND_STATUS -eq 0 ] && [ $FRONTEND_STATUS -eq 0 ]; then
        if [ "$1" = "--open" ]; then
            sleep 2
            open_browser
        fi
    fi
    
    echo -e "${GREEN}所有服务已启动！${NC}"
    echo -e "${GREEN}后端地址: http://localhost:8000${NC}"
    echo -e "${GREEN}前端地址: http://localhost:3000${NC}"
    echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"
    echo -e "${YELLOW}使用 --open 参数可以自动打开浏览器，例如: $0 --open${NC}"
    
    # 等待用户中断
    wait
}

# 执行主函数
main "$@" 