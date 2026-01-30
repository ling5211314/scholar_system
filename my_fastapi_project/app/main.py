from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine, Base
from app.api import users, navigator, papers, chat_rag
import os
from dotenv import load_dotenv

load_dotenv()

# 创建所有数据表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="学者评估系统 API",
    description="基于RAG技术的智能问答系统",
    version="1.2.0"
)

# 获取CORS配置
cors_origins = os.getenv("CORS_ORIGINS", '["http://localhost:5173","http://localhost:3000"]')
try:
    import json
    cors_origins = json.loads(cors_origins)
except:
    cors_origins = ["http://localhost:5173", "http://localhost:3000"]

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 临时允许所有来源用于调试
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 注册路由
app.include_router(users.router)
app.include_router(chat_rag.router)  # RAG API
app.include_router(navigator.router)
app.include_router(papers.router)


@app.get("/", tags=["系统"])
async def root():
    return {
        "message": "欢迎使用学者评估系统 API",
        "version": "1.1.0",
        "features": [
            "用户认证",
            "智能问答（RAG）",
            "研究向导",
            "论文搜索"
        ],
        "docs": "/docs"
    }


@app.get("/health", tags=["系统"])
async def health_check():
    return {"status": "healthy", "rag_enabled": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
