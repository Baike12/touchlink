#!/bin/bash

# 数据库初始化脚本
# 用于在Linux环境中初始化TouchLink数据库

# 设置颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到Python3，请先安装Python3${NC}"
    exit 1
fi

# 检查pip是否安装
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}错误: 未找到pip3，请先安装pip3${NC}"
    exit 1
fi

# 检查MySQL客户端是否安装
if ! command -v mysql &> /dev/null; then
    echo -e "${YELLOW}警告: 未找到MySQL客户端，可能无法连接到MySQL服务器${NC}"
    echo -e "${YELLOW}请安装MySQL客户端: sudo apt install mysql-client (Ubuntu/Debian) 或 sudo yum install mysql (CentOS/RHEL)${NC}"
fi

# 检查.env文件是否存在
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}警告: 未找到.env文件，将使用.env.example创建${NC}"
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo -e "${GREEN}已创建.env文件，请根据需要修改配置${NC}"
    else
        echo -e "${RED}错误: 未找到.env.example文件${NC}"
        exit 1
    fi
fi

# 安装必要的Python包
echo -e "${GREEN}正在安装必要的Python包...${NC}"
pip3 install -r backend/requirements.txt

# 运行数据库初始化脚本
echo -e "${GREEN}正在初始化数据库...${NC}"
cd backend && python3 init_database.py

# 检查执行结果
if [ $? -eq 0 ]; then
    echo -e "${GREEN}数据库初始化成功！${NC}"
    echo -e "${GREEN}现在可以启动TouchLink应用了${NC}"
else
    echo -e "${RED}数据库初始化失败！请检查错误信息${NC}"
    exit 1
fi 