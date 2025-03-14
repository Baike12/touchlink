# TouchLink 数据分析平台

TouchLink是一个用户数据分析的平台软件，用户可以从多种数据源加载数据到TouchLink中，在TouchLink中进行分析后导出。

## 功能特点

- **多数据源支持**：支持MySQL、MongoDB、Excel等多种数据源
- **强大的分析能力**：支持多表合并、列数据处理等分析功能
- **可视化展示**：提供多种图表类型，支持自定义看板布局
- **灵活导出**：支持导出为Excel等多种格式

## 技术栈

### 后端

- **Python**：主要开发语言
- **FastAPI**：高性能Web框架
- **SQLAlchemy**：ORM框架
- **Pandas**：数据处理库
- **Celery**：异步任务队列

### 前端

- **Vue3**：前端框架
- **TypeScript**：类型安全的JavaScript超集
- **Element Plus**：UI组件库
- **ECharts**：图表库
- **Pinia**：状态管理

## 项目结构

```
touchlink/
├── backend/               # Python 后端
│   ├── src/
│   │   ├── core/          # 核心逻辑
│   │   │   ├── data_sources/  # 数据源插件
│   │   │   ├── analytics/     # 分析引擎
│   │   │   ├── tasks/         # 异步任务处理
│   │   │   ├── models/        # 数据模型
│   │   │   └── visualization/ # 可视化处理
│   │   ├── api/           # FastAPI 路由
│   │   ├── config/        # 配置文件
│   │   ├── utils/         # 工具类
│   │   └── main.py        # 入口文件
│   └── requirements.txt
│
├── frontend/              # Vue3 前端
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 通用组件
│   │   │   └── dashboard/ # 看板组件
│   │   ├── stores/        # 状态管理
│   │   ├── api/           # API请求
│   │   └── assets/        # 静态资源
│   └── package.json
│
├── infrastructure/        # 基础设施配置
│   ├── docker-compose.yml
│   └── nginx/
│
└── scripts/               # 部署脚本
```

## 快速开始

### 数据库设置

1. 确保已安装MySQL服务器

```bash
# Ubuntu/Debian
sudo apt install mysql-server

# CentOS/RHEL
sudo yum install mysql-server
sudo systemctl start mysqld
```

2. 配置数据库连接

编辑`backend/.env`文件，设置MySQL连接信息：

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=touchlink
USER_DB_NAME=user_database
```

3. 初始化数据库

使用提供的脚本自动创建数据库和表：

```bash
# 给脚本添加执行权限
chmod +x backend/setup_database.sh

# 运行脚本
./backend/setup_database.sh
```

或者手动初始化：

```bash
cd backend
python init_database.py
```

### 后端

1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

2. 创建.env文件（如果尚未创建）

```bash
cp backend/.env.example backend/.env
# 编辑.env文件，配置数据库等信息
```

3. 启动后端服务

```bash
cd backend
uvicorn src.main:app --reload
```

### 前端

1. 安装依赖

```bash
cd frontend
npm install
```

2. 启动开发服务器

```bash
npm run dev
```

## 开发计划

请参考[TODO.md](TODO.md)文件查看开发计划和进度。

## 贡献指南

欢迎贡献代码或提出建议！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。 