#!/bin/bash

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 加载环境变量
if [ -f "$SCRIPT_DIR/../.env" ]; then
    source "$SCRIPT_DIR/../.env"
fi

# 设置默认值
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-3306}
DB_USER=${DB_USER:-root}
DB_PASSWORD=${DB_PASSWORD:-""}

# 执行SQL脚本
echo "正在初始化用户数据库..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" ${DB_PASSWORD:+-p"$DB_PASSWORD"} < "$SCRIPT_DIR/init_user_db.sql"

# 检查执行结果
if [ $? -eq 0 ]; then
    echo "用户数据库初始化成功"
else
    echo "用户数据库初始化失败"
    exit 1
fi 