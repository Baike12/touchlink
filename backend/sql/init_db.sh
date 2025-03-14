#!/bin/bash

# 加载环境变量
source backend/.env

# 显示配置信息
echo "===== 初始化元数据库 ====="
echo "数据库: $DB_NAME"
echo "主机: $DB_HOST"
echo "端口: $DB_PORT"
echo "用户: $DB_USER"
echo "=========================="

# 执行SQL文件
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD $DB_NAME < backend/sql/init_tables.sql

# 检查执行结果
if [ $? -eq 0 ]; then
    echo "元数据库初始化成功！"
else
    echo "元数据库初始化失败！"
    exit 1
fi 