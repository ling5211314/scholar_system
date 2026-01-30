# RAG 系统搭建指南

## 功能说明

本系统使用 RAG（Retrieval-Augmented Generation）技术，将 MongoDB 中的论文数据作为知识库，结合智谱 GLM-4 模型，实现基于真实论文内容的智能问答。

## 系统架构

```
用户查询
    ↓
向量检索（FAISS）
    ↓
检索相关论文（Top 5）
    ↓
构建 Prompt（包含检索内容）
    ↓
LLM 生成答案（GLM-4）
    ↓
返回答案 + 来源
```

## 目录结构

```
my_fastapi_project/
├── app/
│   ├── rag/
│   │   ├── __init__.py           # RAG 模块初始化
│   │   └── vector_store.py       # 向量存储管理
│   ├── api/
│   │   ├── chat.py              # 原 API（使用简单知识库）
│   │   └── chat_rag.py          # 新 API（使用 RAG）
│   └── db/
│       └── mongodb.py            # MongoDB 连接
├── faiss_index/                 # 向量库存储位置（构建后生成）
├── build_vector_store.py         # 向量库构建脚本
└── RAG_SETUP.md                # 本文档
```

## 安装依赖

```bash
pip install langchain langchain-community faiss-cpu tqdm
```

## 使用步骤

### 1. 配置环境变量

在 `.env` 文件中添加：
```
DASHSCOPE_API_KEY=你的智谱API密钥
MONGODB_URL=mongodb://localhost:27017
```

### 2. 确保 MongoDB 正在运行

```bash
# 检查 MongoDB 服务状态
# Windows
net start MongoDB

# 或使用 Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 3. 构建向量库

运行构建脚本：

```bash
# 在项目根目录下执行
python build_vector_store.py
```

**构建过程说明：**

1. **初始化嵌入模型**: 使用智谱 AI 的 `embedding-3` 模型
2. **加载论文数据**: 从 MongoDB `scholar_db.papers` 集合加载所有论文
3. **格式化文档**: 将论文的题目、摘要、关键词等信息组合成文本
4. **文本切分**: 将长文本切分成小块（500字符，重叠50字符）
5. **生成向量**: 为每个文本块生成嵌入向量
6. **构建索引**: 使用 FAISS 构建向量索引
7. **保存索引**: 保存到 `./faiss_index/` 目录

**构建时间估算：**
- 100 篇论文：约 2-5 分钟
- 500 篇论文：约 10-20 分钟
- 1000 篇论文：约 20-40 分钟

### 4. 启动 FastAPI 服务器

```bash
cd my_fastapi_project
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 测试 RAG 问答

#### 方式一：直接调用 API

```bash
curl -X POST "http://localhost:8000/api/chat/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "什么是牙齿分割技术？"}'
```

#### 方式二：使用前端界面

1. 访问 `http://localhost:5173/`（或你的前端地址）
2. 进入"问答"页面
3. 输入问题，例如：
   - "MICCAI 2023 STS Challenge 的研究内容是什么？"
   - "有哪些关于半监督学习在牙齿分割中应用的论文？"
   - "CBCT 和全景 X 射线在牙齿分割中的区别？"

## API 接口

### 1. 问答接口

```http
POST /api/chat/ask
Content-Type: application/json

{
  "query": "用户的问题"
}
```

**响应示例：**

```json
{
  "answer": "根据检索到的论文信息，MICCAI 2023 STS Challenge 专注于...",
  "sources": [
    "论文题目: MICCAI 2023 STS Challenge: A retrospective study...\n摘要: Computer-aided diagnosis...",
    "论文题目: Deep Learning for Tooth Segmentation\n摘要: ..."
  ],
  "retrieval_count": 5
}
```

### 2. 检查系统状态

```http
GET /api/chat/status
```

**响应示例：**

```json
{
  "system_initialized": true,
  "faiss_index_exists": true,
  "faiss_index_path": "faiss_index"
}
```

### 3. 重建向量库

```http
POST /api/chat/rebuild
```

**响应示例：**

```json
{
  "status": "success",
  "message": "向量库重建成功"
}
```

## 参数调优

### 文本切分参数

在 `build_vector_store.py` 中调整：

```python
vector_store = build_and_save_vector_store(
    chunk_size=500,      # 文本块大小（默认 500）
    chunk_overlap=50      # 重叠大小（默认 50）
)
```

**建议值：**
- `chunk_size`: 300-1000（根据文档长度调整）
- `chunk_overlap`: 10-20% of chunk_size

### 检索参数

在 `app/api/chat_rag.py` 中调整：

```python
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}  # 返回最相关的 5 个文档
)
```

**建议值：**
- `k`: 3-10（更多文档 = 更全面但可能更慢）

### LLM 参数

在 `app/api/chat_rag.py` 中调整：

```python
llm = ChatZhipuAI(
    model="glm-4.7",
    temperature=0.3,      # 温度（0-1，越低越确定）
    api_key=api_key
)
```

**建议值：**
- `temperature`: 0.2-0.5（学术问答建议较低温度）

## 故障排查

### 问题 1: MongoDB 连接失败

```
错误: MongoDB 连接失败: [Errno 111] Connection refused
```

**解决方案：**
```bash
# 检查 MongoDB 是否运行
netstat -an | grep 27017

# 启动 MongoDB
sudo systemctl start mongod  # Linux
brew services start mongodb  # macOS
net start MongoDB           # Windows
```

### 问题 2: 智谱 API 调用失败

```
错误: 智谱API调用出错: 401 Unauthorized
```

**解决方案：**
- 检查 `.env` 文件中的 `DASHSCOPE_API_KEY` 是否正确
- 确保密钥有效且有足够的额度

### 问题 3: FAISS 索引不存在

```
错误: FAISS 索引不存在: ./faiss_index
```

**解决方案：**
```bash
# 重新构建向量库
python build_vector_store.py
```

### 问题 4: 内存不足

```
错误: MemoryError
```

**解决方案：**
- 减小 `chunk_size`
- 减少处理的论文数量
- 使用分批处理

### 问题 5: 构建速度太慢

**解决方案：**
- 减小 `chunk_size`
- 使用更快的嵌入模型
- 使用 GPU（安装 `faiss-gpu`）

## 高级功能

### 1. 增量更新

当有新论文加入数据库时，可以增量更新向量库：

```python
from app.rag.vector_store import ZhipuEmbeddings, save_faiss_index

# 加载现有索引
vector_store = load_faiss_index("./faiss_index", embeddings)

# 添加新文档
new_texts = ["新论文的文本内容..."]
vector_store.add_texts(new_texts)

# 保存更新后的索引
save_faiss_index(vector_store, "./faiss_index")
```

### 2. 自定义检索策略

```python
# 使用最大边界相关性（MMR）
retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 5, "fetch_k": 10}
)
```

### 3. 混合检索

结合语义检索和关键词检索：

```python
# 添加关键词权重
from langchain.retrievers import BM25Retriever

bm25_retriever = BM25Retriever.from_texts(texts)
combined_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever],
    weights=[0.7, 0.3]
)
```

## 性能优化

### 1. 批量处理

嵌入向量时使用批量处理（已在代码中实现）：

```python
batch_size = 10
for i in range(0, len(texts), batch_size):
    batch_texts = texts[i:i + batch_size]
    embeddings = embed_documents(batch_texts)
```

### 2. 并行处理

使用多线程加速：

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(embed, text) for text in texts]
    embeddings = [f.result() for f in futures]
```

### 3. 缓存机制

缓存嵌入向量避免重复计算：

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def embed_cached(text: str):
    return embed_query(text)
```

## 成本估算

### 智谱 API 成本

- `embedding-3` 模型：约 ¥0.0007 / 1K tokens
- `glm-4.7` 模型：约 ¥0.1 / 1K tokens

**示例：**
- 1000 篇论文，每篇约 1000 tokens
- 嵌入成本：1000 × 1000 / 1000 × ¥0.0007 = ¥0.7
- 问答成本（每次查询）：约 ¥0.02-0.05

## 后续改进方向

1. **多模态检索**: 支持图片、表格等内容
2. **引文网络**: 构建论文引用关系图
3. **用户反馈**: 收集用户对答案的评价，优化检索
4. **实时更新**: 自动检测新论文并更新向量库
5. **分布式部署**: 使用 PineCloud 等云服务
6. **多语言支持**: 支持中英文混合检索

## 技术支持

如有问题，请检查：
1. 日志输出（控制台）
2. MongoDB 连接状态
3. API 密钥配置
4. 文件权限（faiss_index 目录）

## 版本历史

- v1.0.0 (2026-01-29): 初始版本，支持基础 RAG 功能
