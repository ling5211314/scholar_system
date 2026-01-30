# 学者评估系统 - FastAPI 后端

基于 FastAPI + MySQL + MongoDB + RAG 技术的智能问答与学术搜索系统后端。

## 项目结构

```
my_fastapi_project/
├── app/
│   ├── __init__.py
│   ├── main.py              # 应用入口
│   ├── api/                # API路由
│   │   ├── __init__.py
│   │   ├── chat.py         # 问答相关接口
│   │   ├── users.py        # 用户认证相关接口
│   │   ├── navigator.py    # 研究向导接口
│   │   └── papers.py       # 论文搜索接口
│   ├── models/             # 数据库模型
│   │   ├── __init__.py
│   │   ├── user.py         # 用户模型（SQLAlchemy）
│   │   └── paper.py        # 论文模型（Pydantic）
│   ├── db/                 # 数据库相关
│   │   ├── __init__.py
│   │   ├── session.py      # MySQL会话管理
│   │   └── mongodb.py      # MongoDB连接管理
├── tests/                 # 测试代码
│   ├── __init__.py
│   └── test_api.py        # API测试
├── knowledge.txt          # RAG知识库
├── requirements.txt       # 依赖列表
├── .env                 # 环境变量配置
└── README.md            # 本文件
```

## 安装步骤

### 1. 创建虚拟环境

```bash
python -m venv venv
```

### 2. 激活虚拟环境

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

编辑 `.env` 文件，配置以下内容：

```env
# MySQL数据库配置
DATABASE_URL=mysql+pymysql://用户名:密码@localhost:3306/数据库名

# MongoDB配置
MONGODB_URL=mongodb://用户名:密码@localhost:27017
MONGODB_DB_NAME=scholar_papers

# JWT配置
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 智谱AI配置
DASHSCOPE_API_KEY=your-zhipu-api-key

# CORS配置
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

### 5. 创建数据库

MySQL数据库：
```sql
CREATE DATABASE scholar_eval CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

MongoDB数据库（如果有论文数据需要导入）：
```bash
# 确保 MongoDB 已启动，数据库名为 scholar_papers
```

### 6. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，访问以下地址：
- API文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc

## API接口

### 用户认证 (`/api/users`)

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/users/register` | 用户注册  
| POST | `/api/users/login` | 用户登录 
| GET | `/api/users/me` | 获取当前用户信息 
| GET | `/api/users/{user_id}` | 获取指定用户信息 

### 智能问答 (`/api/chat`)

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/chat/ask` | 向AI提问（基于RAG） 

**功能说明**：
- 使用 RAG 技术从知识库检索相关信息
- 基于智谱 GLM-4 模型生成答案
- 返回答案和相关文档来源

### 研究向导 (`/api/navigator`)

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/navigator/generate` | 生成研究学习路径 

**功能说明**：
- 根据输入的研究主题生成学习路径
- 分为三阶段：入门必读、进阶核心、前沿探索
- 推荐核心学者

### 论文搜索 (`/api/papers`)

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/papers/search` | 自然语言搜索论文 
| GET | `/api/papers/` | 获取所有论文（分页） 
| POST | `/api/papers/execute` | 直接执行MongoDB查询 

**功能说明**：
- 使用 GLM-4 将自然语言转换为 MongoDB 查询
- 支持按年份、关键词、会议/期刊等搜索
- 返回匹配的论文列表

## 示例

### 用户注册

```bash
curl -X POST "http://localhost:8000/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### 用户登录

```bash
curl -X POST "http://localhost:8000/api/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

### 智能问答

```bash
curl -X POST "http://localhost:8000/api/chat/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是图神经网络？"
  }'
```

### 生成研究路径

```bash
curl -X POST "http://localhost:8000/api/navigator/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "图神经网络",
    "language": "zh"
  }'
```

### 搜索论文

```bash
curl -X POST "http://localhost:8000/api/papers/search" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "2023年CVPR论文"
  }'
```

### 直接执行查询

```bash
curl -X POST "http://localhost:8000/api/papers/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "发表时间": "2023",
    "关键词": {"$regex": "图像分割", "$options": "i"}
  }'
```

## 技术栈

- **Web框架**: FastAPI
- **数据库**: 
  - MySQL + SQLAlchemy（用户数据）
  - MongoDB（论文数据）
- **认证**: JWT + Bcrypt
- **向量数据库**: FAISS
- **大模型**: 智谱GLM-4
- **嵌入模型**: 智谱 embedding-3

## 前端服务

前端使用 Vue 3 + Vite 开发，位于 `frontend/` 目录：

- 开发服务器: `http://localhost:5173`
- 主要功能页面：
  - 智能问答
  - 研究向导
  - 论文搜索
