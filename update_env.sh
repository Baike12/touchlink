#!/bin/bash

# 远程服务器信息
SERVER="101.37.118.6"
USER="root"
PASSWORD="your_password_here"
PROJECT_DIR="/root/tl"

# 使用expect执行SSH命令
run_ssh_command() {
  local cmd="$1"
  expect << EOF
  set timeout 300
  spawn ssh $USER@$SERVER "$cmd"
  expect {
    "yes/no" { send "yes\r"; exp_continue }
    "password:" { send "$PASSWORD\r" }
  }
  expect eof
EOF
}

# 更新.env文件内容
ENV_CONTENT='# 应用配置
DEBUG=True

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=touchlink

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# 安全配置
SECRET_KEY=781nC1ZkBS1SXR2Xd6_BS9j-q1p6DyuN_-PU825Q9TQ=
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS配置
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000", "http://101.37.118.6:3000", "http://101.37.118.6", "http://101.37.118.6:8000"]

# 文件存储配置
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=104857600'

# 创建临时文件
echo "$ENV_CONTENT" > temp_env

# 使用SCP上传临时文件
expect << EOF
set timeout 300
spawn scp temp_env $USER@$SERVER:$PROJECT_DIR/backend/.env
expect {
  "yes/no" { send "yes\r"; exp_continue }
  "password:" { send "$PASSWORD\r" }
}
expect eof
EOF

# 删除临时文件
rm temp_env

# 重启服务
run_ssh_command "cd $PROJECT_DIR && ./start.sh restart"

echo "环境文件已更新，服务已重启" 