#!/bin/bash

# 远程服务器信息
SERVER_IP="101.37.118.6"
PROJECT_DIR="/home/ubuntu/touchlink"
USERNAME="ubuntu"
PASSWORD="your_password_here"
LOCAL_DIR="/Users/construct/CodeRepo/touchlink_clean"

# 显示帮助信息
show_help() {
  echo "用法: $0 [命令]"
  echo "可用命令:"
  echo "  pull        - 拉取最新代码"
  echo "  build       - 在服务器上构建前端"
  echo "  local-build - 在本地构建前端并发送到服务器"
  echo "  restart     - 重启服务"
  echo "  status      - 查看服务状态"
  echo "  logs        - 查看日志"
  echo "  all         - 执行所有操作（拉取、构建、重启）"
  echo "  local-all   - 在本地构建并发送到服务器，然后重启服务"
  echo "  custom '命令' - 执行自定义命令"
  echo "  check       - 检查API路由"
}

# 检查参数
if [ $# -eq 0 ]; then
  show_help
  exit 1
fi

# 使用expect执行SSH命令
run_ssh_command() {
  local cmd="$1"
  expect << EOF
  set timeout 300
  spawn ssh $USERNAME@$SERVER_IP "$cmd"
  expect {
    "yes/no" { send "yes\r"; exp_continue }
    "password:" { send "$PASSWORD\r" }
  }
  expect eof
EOF
}

# 使用expect执行SCP命令
run_scp_command() {
  local src="$1"
  local dest="$2"
  expect << EOF
  set timeout 300
  spawn scp -r "$src" $USERNAME@$SERVER_IP:"$dest"
  expect {
    "yes/no" { send "yes\r"; exp_continue }
    "password:" { send "$PASSWORD\r" }
  }
  expect eof
EOF
}

# 在本地构建前端
build_frontend_locally() {
  echo "在本地构建前端..."
  cd "$LOCAL_DIR/frontend"
  npm run build
  
  if [ $? -ne 0 ]; then
    echo "前端构建失败"
    exit 1
  fi
  
  echo "前端构建成功"
}

# 发送构建文件到服务器
send_build_to_server() {
  echo "发送构建文件到服务器..."
  run_scp_command "$LOCAL_DIR/frontend/dist" "$PROJECT_DIR/frontend/"
  echo "文件发送完成"
}

# 根据命令执行相应操作
case "$1" in
  "pull")
    echo "正在拉取最新代码..."
    run_ssh_command "cd $PROJECT_DIR && git pull"
    ;;
  "build")
    echo "正在服务器上构建前端..."
    run_ssh_command "cd $PROJECT_DIR/frontend && npm run build"
    ;;
  "local-build")
    build_frontend_locally
    send_build_to_server
    ;;
  "restart")
    echo "正在重启服务..."
    run_ssh_command "cd $PROJECT_DIR && ./start.sh restart"
    ;;
  "status")
    echo "查看服务状态..."
    run_ssh_command "cd $PROJECT_DIR && ps aux | grep -E 'python|node' | grep -v grep"
    ;;
  "logs")
    echo "查看日志..."
    run_ssh_command "cd $PROJECT_DIR && tail -n 50 logs/backend.log"
    ;;
  "check")
    echo "检查API路由..."
    run_ssh_command "cd $PROJECT_DIR && curl -v http://localhost:3000/api/v1/user-tables"
    ;;
  "all")
    echo "执行所有操作（拉取、服务器构建、重启）..."
    run_ssh_command "cd $PROJECT_DIR && git pull && cd frontend && npm run build && cd .. && ./start.sh restart"
    ;;
  "local-all")
    echo "执行本地构建并发送到服务器，然后重启服务..."
    run_ssh_command "cd $PROJECT_DIR && git pull"
    build_frontend_locally
    send_build_to_server
    run_ssh_command "cd $PROJECT_DIR && ./start.sh restart"
    ;;
  "custom")
    if [ -z "$2" ]; then
      echo "错误: 缺少自定义命令"
      show_help
      exit 1
    fi
    echo "执行自定义命令: $2"
    run_ssh_command "cd $PROJECT_DIR && $2"
    ;;
  *)
    echo "错误: 未知命令 '$1'"
    show_help
    exit 1
    ;;
esac 