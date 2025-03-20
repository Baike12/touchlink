#!/bin/bash

# TouchLink 统一启动脚本
# 用于同时启动TouchLink前端和后端服务，并管理日志输出

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 设置目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
LOG_DIR="$SCRIPT_DIR/logs"
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

# 确保日志目录存在
mkdir -p "$LOG_DIR"

# 清理旧的日志文件
clean_logs() {
    echo -e "${BLUE}清理旧的日志文件...${NC}"
    
    # 清理根目录下的日志
    if [ -f "$BACKEND_LOG" ]; then
        echo "" > "$BACKEND_LOG"
    fi
    
    if [ -f "$FRONTEND_LOG" ]; then
        echo "" > "$FRONTEND_LOG"
    fi
    
    echo -e "${GREEN}日志文件已清理${NC}"
}

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

# 函数：启动后端
start_backend() {
    echo -e "${GREEN}启动TouchLink后端服务...${NC}"
    echo -e "${GREEN}日志将写入: $BACKEND_LOG${NC}"
    
    # 切换到后端目录
    cd "$BACKEND_DIR"
    
    # 检查Python命令
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}错误: 未找到Python命令${NC}"
        return 1
    fi
    
    # 检查conda环境
    if command -v conda &> /dev/null; then
        # 使用touchlink环境
        echo -e "${GREEN}使用conda环境: touchlink${NC}"
        
        # 创建启动脚本
        TEMP_SCRIPT="$LOG_DIR/start_backend_temp.sh"
        echo "#!/bin/bash" > "$TEMP_SCRIPT"
        echo "source \$(conda info --base)/etc/profile.d/conda.sh" >> "$TEMP_SCRIPT"
        echo "conda activate touchlink" >> "$TEMP_SCRIPT"
        echo "cd $SCRIPT_DIR" >> "$TEMP_SCRIPT"
        echo "$PYTHON_CMD -m backend.src.main > $BACKEND_LOG 2>&1" >> "$TEMP_SCRIPT"
        chmod +x "$TEMP_SCRIPT"
        
        # 启动后端应用
        echo -e "${GREEN}执行命令: $PYTHON_CMD -m backend.src.main${NC}"
        "$TEMP_SCRIPT" &
        
        # 保存PID
        BACKEND_PID=$!
        echo $BACKEND_PID > "$LOG_DIR/backend.pid"
    else
        echo -e "${YELLOW}未找到conda命令，将使用系统Python${NC}"
        
        # 启动后端应用
        echo -e "${GREEN}执行命令: $PYTHON_CMD -m backend.src.main${NC}"
        cd "$SCRIPT_DIR"
        $PYTHON_CMD -m backend.src.main > "$BACKEND_LOG" 2>&1 &
        
        # 保存PID
        BACKEND_PID=$!
        echo $BACKEND_PID > "$LOG_DIR/backend.pid"
    fi
    
    echo -e "${GREEN}TouchLink后端服务已启动，PID: $BACKEND_PID${NC}"
    
    # 等待后端启动
    echo -e "${YELLOW}等待后端服务启动...${NC}"
    sleep 5
    
    # 检查后端是否成功启动
    if curl -s "http://localhost:8000/health" > /dev/null; then
        echo -e "${GREEN}后端服务已成功启动${NC}"
        return 0
    else
        echo -e "${YELLOW}后端服务可能需要更长时间启动，继续等待...${NC}"
        sleep 5
        if curl -s "http://localhost:8000/health" > /dev/null; then
            echo -e "${GREEN}后端服务已成功启动（延迟）${NC}"
            return 0
        fi
        return 1
    fi
}

# 函数：启动前端
start_frontend() {
    echo -e "${GREEN}启动TouchLink前端服务...${NC}"
    echo -e "${GREEN}日志将写入: $FRONTEND_LOG${NC}"
    
    # 切换到前端目录
    cd "$FRONTEND_DIR"
    
    # 检查npm命令
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}错误: 未找到npm命令，请先安装Node.js${NC}"
        return 1
    fi
    
    # 启动前端应用
    npm run dev > "$FRONTEND_LOG" 2>&1 &
    
    # 保存PID
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$LOG_DIR/frontend.pid"
    
    echo -e "${GREEN}TouchLink前端服务已启动，PID: $FRONTEND_PID${NC}"
    
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
        fi
        return 1
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

# 函数：停止所有服务
stop_services() {
    echo -e "${YELLOW}正在停止所有服务...${NC}"
    
    # 停止前端
    if [ -f "$LOG_DIR/frontend.pid" ]; then
        FRONTEND_PID=$(cat "$LOG_DIR/frontend.pid")
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo -e "${YELLOW}停止前端服务 (PID: $FRONTEND_PID)${NC}"
            kill -9 $FRONTEND_PID
        fi
        rm -f "$LOG_DIR/frontend.pid"
    fi
    
    # 停止后端
    if [ -f "$LOG_DIR/backend.pid" ]; then
        BACKEND_PID=$(cat "$LOG_DIR/backend.pid")
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo -e "${YELLOW}停止后端服务 (PID: $BACKEND_PID)${NC}"
            kill -9 $BACKEND_PID
        fi
        rm -f "$LOG_DIR/backend.pid"
    fi
    
    # 杀死占用端口的进程
    kill_process_on_port 3000
    kill_process_on_port 8000
    
    echo -e "${GREEN}所有服务已停止${NC}"
}

# 函数：显示日志
show_logs() {
    local log_type=$1
    
    if [ "$log_type" = "backend" ]; then
        echo -e "${GREEN}显示后端日志:${NC}"
        tail -f "$BACKEND_LOG"
    elif [ "$log_type" = "frontend" ]; then
        echo -e "${GREEN}显示前端日志:${NC}"
        tail -f "$FRONTEND_LOG"
    else
        echo -e "${RED}未知的日志类型: $log_type${NC}"
        echo -e "${YELLOW}可用选项: backend, frontend${NC}"
    fi
}

# 函数：显示帮助
show_help() {
    echo -e "${GREEN}TouchLink 统一启动脚本${NC}"
    echo -e "${YELLOW}用法: $0 [选项]${NC}"
    echo -e "${YELLOW}选项:${NC}"
    echo -e "  ${GREEN}start${NC}       启动前端和后端服务"
    echo -e "  ${GREEN}stop${NC}        停止所有服务"
    echo -e "  ${GREEN}restart${NC}     重启所有服务"
    echo -e "  ${GREEN}logs${NC}        显示所有日志"
    echo -e "  ${GREEN}logs:backend${NC} 显示后端日志"
    echo -e "  ${GREEN}logs:frontend${NC} 显示前端日志"
    echo -e "  ${GREEN}--open${NC}      启动后自动打开浏览器"
    echo -e "  ${GREEN}--help${NC}      显示帮助信息"
}

# 主函数
main() {
    # 处理特殊选项
    if [ "$1" = "--help" ]; then
        show_help
        exit 0
    fi
    
    # 如果没有参数，显示帮助
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    # 处理命令行参数
    COMMAND=$1
    shift
    
    # 解析选项
    OPEN_BROWSER=false
    
    for arg in "$@"; do
        case $arg in
            --open)
                OPEN_BROWSER=true
                ;;
            --help)
                show_help
                exit 0
                ;;
        esac
    done
    
    # 执行命令
    case $COMMAND in
        start)
            echo -e "${GREEN}===== TouchLink 启动脚本 =====${NC}"
            
            # 清理日志
            clean_logs
            
            # 杀死占用端口的进程
            kill_process_on_port 3000
            kill_process_on_port 8000
            
            # 启动后端
            start_backend
            BACKEND_STATUS=$?
            
            # 启动前端
            start_frontend
            FRONTEND_STATUS=$?
            
            # 如果前端和后端都启动成功，打开浏览器
            if [ $BACKEND_STATUS -eq 0 ] && [ $FRONTEND_STATUS -eq 0 ]; then
                if [ "$OPEN_BROWSER" = true ]; then
                    sleep 2
                    open_browser
                fi
            fi
            
            echo -e "${GREEN}所有服务已启动！${NC}"
            echo -e "${GREEN}后端地址: http://localhost:8000${NC}"
            echo -e "${GREEN}前端地址: http://localhost:3000${NC}"
            echo -e "${YELLOW}使用 '$0 logs' 查看日志${NC}"
            echo -e "${YELLOW}使用 '$0 stop' 停止所有服务${NC}"
            ;;
            
        stop)
            stop_services
            ;;
            
        restart)
            stop_services
            sleep 2
            $0 start "$@"
            ;;
            
        logs)
            echo -e "${GREEN}显示所有日志:${NC}"
            echo -e "${YELLOW}按 Ctrl+C 停止查看日志${NC}"
            tail -f "$BACKEND_LOG" "$FRONTEND_LOG"
            ;;
            
        logs:backend)
            show_logs backend
            ;;
            
        logs:frontend)
            show_logs frontend
            ;;
            
        *)
            echo -e "${RED}未知命令: $COMMAND${NC}"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 