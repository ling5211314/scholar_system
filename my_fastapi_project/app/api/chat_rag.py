"""RAG API 接口 - 集成向量检索和问答
支持混合检索：语义检索 + BM25 关键词检索
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv
import os

from app.api.users import get_current_active_user
from app.models.user import User
from app.rag.vector_store import LocalEmbeddings, ZhipuEmbeddings, load_faiss_index
from app.rag.hybrid_retriever import BM25Retriever, combine_results

load_dotenv()

router = APIRouter(prefix="/api/rag", tags=["智能问答RAG"])

# 全局变量
api_key = os.getenv("DASHSCOPE_API_KEY", "")
vector_store = None
rag_chain = None
bm25_retriever = None


def format_docs(docs):
    """格式化检索到的文档"""
    return "\n\n---\n\n".join([d.page_content for d in docs])


def initialize_rag_system(enable_hybrid: bool = False):
    """
    初始化 RAG 系统
    从本地加载 FAISS 索引并构建 RAG 链

    Args:
        enable_hybrid: 是否启用混合检索（语义 + BM25）
    """
    global vector_store, rag_chain, bm25_retriever

    try:
        print("="*60)
        print("初始化 RAG 系统...")
        print("="*60)

        # 1. 初始化嵌入模型（使用本地模型）
        print("\n1. 初始化嵌入模型...")
        print("   使用本地嵌入模型")
        embeddings = LocalEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
        print("   ✓ 嵌入模型初始化完成")

        # 2. 加载 FAISS 索引
        print("\n2. 加载 FAISS 向量索引...")
        # 索引文件在项目根目录的 faiss_index
        faiss_path = r"F:\code_local\scholar_evaluatin\faiss_index"

        if os.path.exists(faiss_path):
            vector_store = load_faiss_index(faiss_path, embeddings)
            print(f"   ✓ FAISS 索引加载成功: {faiss_path}")
        else:
            print(f"   ✗ FAISS 索引不存在: {faiss_path}")
            print(f"   提示: 请先运行 'python build_vector_store.py' 构建向量库")
            return False

        # 3. 创建检索器
        print("\n3. 创建检索器...")
        search_kwargs = {"k": 5}  # 返回最相关的 5 个文档

        if enable_hybrid:
            print("   启用混合检索（语义 + BM25）")
            # 混合检索将在检索时动态实现
            retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs=search_kwargs
            )
        else:
            print("   使用语义检索")
            retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs=search_kwargs
            )
        print("   ✓ 检索器创建完成")

        # 4. 初始化 LLM
        print("\n4. 初始化智谱 GLM-4 模型...")
        llm = ChatZhipuAI(model="glm-4.7", temperature=0.3, api_key=api_key)
        print("   ✓ GLM-4 模型初始化完成")

        # 5. 构建 RAG 链
        print("\n5. 构建 RAG 链...")
        prompt = ChatPromptTemplate.from_template("""
你是一个专业的学术助手。请根据以下检索到的论文相关信息来回答用户的问题。

【重要提示】:
1. 仅基于提供的上下文信息回答问题，不要编造内容
2. 如果上下文信息不足以回答问题，请诚实地说明
3. 引用具体的论文和作者来支持你的回答
4. 保持回答的专业性和准确性

【检索到的相关信息】:
{context}

【用户问题】: {question}

【你的回答】:
""")

        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        print("   ✓ RAG 链构建完成")

        # 6. 初始化 BM25 检索器（如果启用混合检索）
        if enable_hybrid:
            print("\n6. 初始化 BM25 检索器...")
            # 获取所有文档文本
            all_docs = [doc.page_content for doc in vector_store.docstore._dict.values()]
            bm25_retriever = BM25Retriever(all_docs)
            print("   ✓ BM25 检索器初始化完成")

        print("\n" + "="*60)
        print("✓ RAG 系统初始化成功!")
        print(f"混合检索: {'已启用' if enable_hybrid else '未启用'}")
        print("="*60 + "\n")

        return True

    except Exception as e:
        print("\n" + "="*60)
        print("✗ RAG 系统初始化失败!")
        print(f"错误: {str(e)}")
        print("="*60 + "\n")
        import traceback
        traceback.print_exc()
        return False


class Question(BaseModel):
    question: str  # 用户问题
    use_hybrid: bool = False  # 是否使用混合检索
    semantic_weight: float = 0.7  # 语义检索权重
    bm25_weight: float = 0.3  # BM25 检索权重


class RAGAnswer(BaseModel):
    answer: str
    sources: List[str]
    retrieval_count: int
    retrieval_method: str  # "semantic" 或 "hybrid"
    scores: Optional[List[dict]] = None  # 检索分数详情


@router.post("/ask", summary="向AI提问（RAG）", response_model=RAGAnswer)
async def ask(question: Question):
    """
    向AI提问接口 - 使用 RAG 技术

    支持两种检索模式：
    - 纯语义检索（默认）
    - 混合检索（语义 + BM25）
    """
    try:
        # 确保 RAG 系统已初始化
        if vector_store is None or rag_chain is None:
            if not initialize_rag_system(enable_hybrid=question.use_hybrid):
                raise HTTPException(
                    status_code=503,
                    detail="RAG 系统未初始化，请先构建向量库（运行 python build_vector_store.py）"
                )

        print(f"\n{'='*60}")
        print(f"收到问答请求")
        print(f"问题: {question.question}")
        print(f"检索模式: {'混合检索' if question.use_hybrid else '语义检索'}")
        print(f"{'='*60}\n")

        retrieval_method = "semantic"
        scores = []

        if question.use_hybrid:
            # 混合检索
            print("1. 执行混合检索（语义 + BM25）...")

            # 语义检索
            retriever = vector_store.as_retriever(search_kwargs={"k": 10})
            semantic_docs = retriever.invoke(question.question)

            # BM25 检索
            all_docs = [doc.page_content for doc in vector_store.docstore._dict.values()]
            bm25_retriever = BM25Retriever(all_docs)
            bm25_results = bm25_retriever.retrieve(question.question, top_k=10)

            # 合并结果
            semantic_scores = [(i, 1.0) for i, doc in enumerate(semantic_docs)]
            combined = combine_results(
                semantic_scores,
                bm25_results,
                semantic_weight=question.semantic_weight,
                bm25_weight=question.bm25_weight,
                top_k=5
            )

            # 获取最终文档
            relevant_docs = []
            for idx, _ in combined:
                if idx < len(semantic_docs):
                    relevant_docs.append(semantic_docs[idx])
                    scores.append({
                        "index": idx,
                        "hybrid_score": combined[idx][1],
                        "retrieval": "hybrid"
                    })

            retrieval_method = "hybrid"
            print(f"   混合检索完成，找到 {len(relevant_docs)} 个相关文档")

        else:
            # 纯语义检索
            print("1. 执行语义检索...")
            retriever = vector_store.as_retriever(search_kwargs={"k": 5})
            relevant_docs = retriever.invoke(question.question)

            retrieval_count = len(relevant_docs)
            print(f"   语义检索完成，找到 {retrieval_count} 个相关文档")

        # 格式化源文档
        sources = []
        for doc in relevant_docs:
            # 提取论文题目和摘要作为源信息
            content = doc.page_content
            sources.append(content[:200] + "..." if len(content) > 200 else content)

        # 生成答案
        print("2. 生成答案...")
        answer = rag_chain.invoke(question.question)

        print(f"   答案生成成功\n")

        return {
            "answer": answer,
            "sources": sources,
            "retrieval_count": len(relevant_docs),
            "retrieval_method": retrieval_method,
            "scores": scores if question.use_hybrid else None
        }

    except HTTPException as he:
        print(f"\nHTTP错误: {he.status_code} - {he.detail}\n")
        raise he
    except Exception as e:
        print(f"\n处理问题时出错: {str(e)}\n")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rebuild", summary="重建向量库")
async def rebuild_vector_store(strategy: str = "semantic"):
    """
    重建向量库接口（需要管理员权限）

    Args:
        strategy: 分割策略 (semantic, recursive, structured)
    """
    try:
        print(f"\n开始重建向量库，分割策略: {strategy}...")

        from app.rag.vector_store import build_and_save_vector_store

        result = build_and_save_vector_store(
            db_name="scholar_db",
            collection_name="papers",
            save_path="./faiss_index",
            split_strategy=strategy,
            chunk_size=500,
            chunk_overlap=50
        )

        if result:
            # 重新初始化 RAG 系统
            initialize_rag_system()
            return {
                "status": "success",
                "message": "向量库重建成功",
                "strategy": strategy
            }
        else:
            raise HTTPException(status_code=500, detail="向量库重建失败")

    except Exception as e:
        print(f"重建向量库失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", summary="检查 RAG 系统状态")
async def check_status():
    """
    检查 RAG 系统状态
    """
    global vector_store, rag_chain, bm25_retriever

    is_initialized = vector_store is not None and rag_chain is not None
    is_hybrid_ready = bm25_retriever is not None

    # 检查 FAISS 索引文件
    faiss_path = r"F:\code_local\scholar_evaluatin\faiss_index"
    faiss_exists = os.path.exists(faiss_path)

    return {
        "system_initialized": is_initialized,
        "hybrid_retrieval_ready": is_hybrid_ready,
        "faiss_index_exists": faiss_exists,
        "faiss_index_path": faiss_path
    }


# 启动时自动初始化（可选，默认不启用混合检索）
try:
    initialize_rag_system(enable_hybrid=False)
except Exception as e:
    print(f"启动时 RAG 初始化失败: {e}")
