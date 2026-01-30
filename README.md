# 学者评估系统

## 介绍

这是一个基于 RAG（检索增强生成）技术的智能学术辅助系统，集成智能问答、研究向导和论文搜索三大功能。



faiss数据索引链接通过网盘分享的文件：schloar数据
链接: https://pan.baidu.com/s/18PS2NAz6Jlq9xNQR5sKMyg?pwd=yvsm 提取码: yvsm 
--来自百度网盘超级会员v5的分享

### 主要功能

- **智能问答**：基于私有知识库的 AI 问答系统，支持自然语言交互
- **研究向导**：根据研究主题生成个性化学习路径，推荐经典文献和核心学者
- **论文搜索**：基于 MongoDB 的智能论文检索，支持自然语言查询

## 软件架构

### 技术栈

**后端**：
- FastAPI - 高性能 Web 框架
- MySQL - 用户数据存储
- MongoDB - 论文数据存储
- SQLAlchemy - ORM 框架
- 智谱 GLM-4 - 大语言模型
- FAISS - 向量数据库
- 智谱 embedding-3 - 文本嵌入模型

**前端**：
- Vue 3 - 渐进式前端框架
- Vite - 快速构建工具
- Pinia - 状态管理
- Axios - HTTP 客户端

### 架构图

```
┌─────────────┐
│   Vue 3 前端   │
│  (Port: 5173) │
└──────┬──────┘
       │ HTTP/JSON
       ▼
┌─────────────┐
│  FastAPI 后端  │
│  (Port: 8000) │
└──────┬──────┘
       │
       ├─────────────┬─────────────┐
       ▼             ▼             ▼
  ┌─────────┐  ┌─────────┐  ┌─────────┐
  │  MySQL  │  │ MongoDB │  │ 智谱AI  │
  │ (用户)  │  │ (论文)  │  │  (LLM)  │
  └─────────┘  └─────────┘  └─────────┘
```

## 安装教程

### 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+
- MongoDB 4.0+

### 后端安装

1. **克隆仓库**

```bash
git clone <repository-url>
cd scholar_evaluatin/my_fastapi_project
```

2. **创建虚拟环境**

```bash
python -m venv venv
```

3. **激活虚拟环境**

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. **安装依赖**

```bash
pip install -r requirements.txt
```

5. **配置环境变量**

编辑 `.env` 文件：

```env
# MySQL数据库配置
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/scholar_eval

# MongoDB配置
MONGODB_URL=mongodb://root:password@localhost:27017
MONGODB_DB_NAME=scholar_papers

# JWT配置
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 智谱AI配置
DASHSCOPE_API_KEY=your-zhipu-api-key

# CORS配置
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

6. **创建数据库**

MySQL:
```sql
CREATE DATABASE scholar_eval CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

确保 MongoDB 已启动且有论文数据（如果需要使用论文搜索功能）。

7. **启动后端服务**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端安装

1. **进入前端目录**

```bash
cd frontend
```

2. **安装依赖**

```bash
npm install
```

3. **启动开发服务器**

```bash
npm run dev
```

前端服务将运行在 `http://localhost:5173`

## 使用说明

### 1. 访问系统

打开浏览器访问 `http://localhost:5173`

### 2. 用户注册/登录

- 首次使用需要注册账号
- 注册后使用用户名和密码登录
- 登录后可以访问智能问答功能

### 3. 使用智能问答

- 登录后在问答页面输入问题
- 系统会基于知识库生成答案
- 可以点击"知识来源"查看参考文档

### 4. 使用研究向导

- 点击顶部导航的"研究向导"
- 输入研究方向（如"图神经网络"）
- 系统生成三阶段学习路径：
  - 入门必读：经典奠基性论文
  - 进阶核心：近3年顶会论文
  - 前沿探索：最新预印本
- 推荐核心学者信息

### 5. 使用论文搜索

- 点击顶部导航的"论文搜索"
- 支持自然语言查询：
  - "2023年CVPR论文"
  - "关于图像分割的论文"
  - "机器学习相关的期刊论文"
- 系统会自动将自然语言转换为查询条件并检索

### 6. API 文档

后端 API 文档：`http://localhost:8000/docs`

## 目录结构

```
scholar_evaluatin/
├── my_fastapi_project/      # 后端项目
│   ├── app/                # 应用代码
│   │   ├── api/           # API路由
│   │   ├── models/        # 数据模型
│   │   └── db/           # 数据库配置
│   ├── knowledge.txt       # RAG知识库
│   └── requirements.txt    # Python依赖
└── frontend/              # 前端项目
    ├── src/
    │   ├── views/        # 页面组件
    │   ├── stores/       # 状态管理
    │   └── router.js     # 路由配置
    └── package.json      # Node依赖
```

## 参与贡献

1. Fork 本仓库
2. 新建 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请提交 Issue。

