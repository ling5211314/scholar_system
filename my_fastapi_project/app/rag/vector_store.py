"""向量存储管理模块 - 用于从 MongoDB 构建和保存 FAISS 向量库
支持多种分割策略：语义分割、递归字符分割、结构化分割
支持混合检索：语义检索 + 关键词检索
"""

import os
from typing import List, Dict, Any, Optional, Callable
from tqdm import tqdm
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatZhipuAI
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter
)
from langchain_core.embeddings import Embeddings
from httpx import Client
import httpx
from dotenv import load_dotenv
import re

from app.db.mongodb import get_mongo_client
from app.models.paper import Paper

load_dotenv()


# 本地嵌入模型类（使用 sentence-transformers）
class LocalEmbeddings(Embeddings):
    """本地嵌入模型封装 - 使用 sentence-transformers"""

    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Args:
            model_name: 模型名称，默认使用多语言模型，支持中英文
        """
        # 设置 Hugging Face 镜像（解决国内下载问题）
        os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
        
        from sentence_transformers import SentenceTransformer
        print(f"加载本地嵌入模型: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        print("本地嵌入模型加载完成\n")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文档"""
        return self.model.encode(texts, convert_to_numpy=True).tolist()

    def embed_query(self, text: str) -> List[float]:
        """嵌入单个查询"""
        return self.model.encode(text, convert_to_numpy=True).tolist()


# 智谱AI嵌入类
class ZhipuEmbeddings(Embeddings):
    """智谱 AI 嵌入模型封装"""

    def __init__(self, api_key: str, model: str = "embedding-3"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/embeddings"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文档（同步）"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        embeddings = []
        try:
            with httpx.Client(timeout=60.0) as client:
                # 批量处理，每批 10 个文本
                batch_size = 10
                for i in tqdm(range(0, len(texts), batch_size), desc="生成嵌入向量"):
                    batch_texts = texts[i:i + batch_size]

                    # 单个文本发送请求
                    batch_embeddings = []
                    for text in batch_texts:
                        payload = {
                            "model": self.model,
                            "input": text
                        }
                        response = client.post(self.api_url, headers=headers, json=payload)
                        response.raise_for_status()
                        result = response.json()
                        if "data" in result and len(result["data"]) > 0 and "embedding" in result["data"][0]:
                            batch_embeddings.append(result["data"][0]["embedding"])
                        else:
                            print(f"智谱API响应格式错误: {result}")
                            raise ValueError("智谱API响应格式错误")

                    embeddings.extend(batch_embeddings)
        except Exception as e:
            print(f"智谱API调用出错: {str(e)}")
            raise e

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """嵌入单个查询（同步）"""
        return self.embed_documents([text])[0]


def format_paper_document(paper: Dict[str, Any]) -> str:
    """
    将论文数据格式化为可嵌入的文本

    Args:
        paper: 论文数据字典

    Returns:
        格式化后的文本
    """
    parts = []

    # 论文题目
    if paper.get("论文题目"):
        parts.append(f"论文题目: {paper['论文题目']}")

    # 摘要
    if paper.get("摘要"):
        parts.append(f"摘要: {paper['摘要']}")

    # 关键词
    if paper.get("关键词"):
        parts.append(f"关键词: {paper['关键词']}")

    # 作者
    if paper.get("作者"):
        # 限制作者数量，避免太长
        authors = paper['作者']
        if len(authors) > 100:
            authors = authors[:100] + "..."
        parts.append(f"作者: {authors}")

    # 期刊/会议名称
    if paper.get("期刊/会议名称"):
        parts.append(f"期刊/会议: {paper['期刊/会议名称']}")

    # 发表时间
    if paper.get("发表时间"):
        parts.append(f"发表时间: {paper['发表时间']}")

    return "\n".join(parts)


def load_papers_from_mongodb(db_name: str = "scholar_db", collection_name: str = "papers") -> List[Dict[str, Any]]:
    """
    从 MongoDB 加载所有论文数据

    Args:
        db_name: 数据库名称
        collection_name: 集合名称

    Returns:
        论文数据列表
    """
    print(f"\n{'='*60}")
    print(f"从 MongoDB 加载论文数据...")
    print(f"数据库: {db_name}, 集合: {collection_name}")
    print(f"{'='*60}\n")

    try:
        client = get_mongo_client()
        db = client[db_name]
        collection = db[collection_name]

        # 统计文档数量
        total_count = collection.count_documents({})
        print(f"找到 {total_count} 篇论文\n")

        if total_count == 0:
            print("警告: 数据库中没有论文数据!")
            return []

        # 加载所有论文
        papers = list(collection.find({}))

        print(f"成功加载 {len(papers)} 篇论文\n")
        return papers

    except Exception as e:
        print(f"从 MongoDB 加载数据失败: {str(e)}")
        raise


def prepare_documents_for_embedding(papers: List[Dict[str, Any]]) -> List[str]:
    """
    将论文数据准备为可嵌入的文档列表

    Args:
        papers: 论文数据列表

    Returns:
        格式化后的文档文本列表
    """
    print(f"\n{'='*60}")
    print(f"准备文档用于嵌入...")
    print(f"{'='*60}\n")

    documents = []

    for paper in tqdm(papers, desc="格式化文档"):
        formatted_text = format_paper_document(paper)
        if formatted_text.strip():
            documents.append(formatted_text)

    print(f"\n共准备 {len(documents)} 个文档\n")
    return documents


def split_documents_by_strategy(
    documents: List[str],
    embeddings: Embeddings,
    split_strategy: str = "recursive",
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[str]:
    """
    根据策略分割文档

    Args:
        documents: 文档列表
        embeddings: 嵌入模型
        split_strategy: 分割策略
            - "recursive": 递归字符分割（简单快速）
            - "structured": 结构化分割（基于论文结构）
        chunk_size: 文本块大小（仅用于递归分割）
        chunk_overlap: 文本块重叠大小（仅用于递归分割）

    Returns:
        分割后的文本块列表
    """
    print(f"\n{'='*60}")
    print(f"使用分割策略: {split_strategy}")
    print(f"{'='*60}\n")

    chunks = []

    if split_strategy == "recursive":
        # 递归字符分割（快速，但不够智能）
        print("使用递归字符分割...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",  # 段落
                "\n",    # 行
                "。",    # 中文句号
                "！",    # 中文感叹号
                "？",    # 中文问号
                "；",    # 中文分号
                "，",    # 中文逗号
                ". ",    # 英文句号
                "! ",    # 英文感叹号
                "? ",    # 英文问号
                "; ",    # 英文分号
                ", ",    # 英文逗号
                " ",     # 空格
                ""       # 字符
            ]
        )

        for doc in tqdm(documents, desc="递归分割文档"):
            doc_chunks = text_splitter.split_text(doc)
            chunks.extend(doc_chunks)

    elif split_strategy == "semantic":
        # 语义分割在新版本中不可用，回退到递归分割
        print("语义分割在新版本中不可用，使用递归分割...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",  # 段落
                "\n",    # 行
                "。",    # 中文句号
                "！",    # 中文感叹号
                "？",    # 中文问号
                "；",    # 中文分号
                "，",    # 中文逗号
                ". ",    # 英文句号
                "! ",    # 英文感叹号
                "? ",    # 英文问号
                "; ",    # 英文分号
                ", ",    # 英文逗号
                " ",     # 空格
                ""       # 字符
            ]
        )

        for doc in tqdm(documents, desc="递归分割文档"):
            doc_chunks = text_splitter.split_text(doc)
            chunks.extend(doc_chunks)
            return split_documents_by_strategy(
                documents, embeddings, "recursive",
                chunk_size, chunk_overlap
            )

    elif split_strategy == "structured":
        # 结构化分割（基于论文的字段结构）
        print("使用结构化分割...")
        chunks = split_documents_structured(documents)

    else:
        raise ValueError(f"未知的分割策略: {split_strategy}")

    print(f"\n分割后共 {len(chunks)} 个文本块\n")
    return chunks


def split_documents_structured(documents: List[str]) -> List[str]:
    """
    结构化分割：根据论文的字段结构进行分割

    这种方法将每篇论文的字段（题目、摘要、关键词等）作为独立的文本块

    Args:
        documents: 格式化的论文文档列表

    Returns:
        分割后的文本块列表
    """
    chunks = []

    for doc in tqdm(documents, desc="结构化分割"):
        # 按标记分割字段
        lines = doc.split('\n')
        current_chunk = ""

        for line in lines:
            if line.startswith(("论文题目:", "摘要:", "关键词:", "作者:", "期刊/会议:", "发表时间:")):
                # 遇到新字段，保存当前块（如果有）
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = line
            else:
                # 继续当前块
                current_chunk += "\n" + line

        # 保存最后一个块
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

    return chunks


def build_faiss_index(
    documents: List[str],
    embeddings: Embeddings,
    split_strategy: str = "recursive",
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> FAISS:
    """
    构建 FAISS 向量索引

    Args:
        documents: 文档列表
        embeddings: 嵌入模型
        split_strategy: 分割策略
            - "recursive": 递归字符分割
            - "semantic": 语义分割（推荐）
            - "structured": 结构化分割
        chunk_size: 文本块大小（仅用于递归分割）
        chunk_overlap: 文本块重叠大小（仅用于递归分割）
        breakpoint_threshold_type: 语义分割阈值类型

    Returns:
        FAISS 向量索引
    """
    print(f"\n{'='*60}")
    print(f"构建 FAISS 向量索引...")
    print(f"分割策略: {split_strategy}")
    if split_strategy == "recursive":
        print(f"参数: chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
    print(f"{'='*60}\n")

    # 文本切分
    chunks = split_documents_by_strategy(
        documents,
        embeddings,
        split_strategy,
        chunk_size,
        chunk_overlap
    )

    # 构建向量索引
    print("构建向量索引...")
    vector_store = FAISS.from_texts(chunks, embeddings)

    print(f"\n向量索引构建成功!\n")
    return vector_store


def save_faiss_index(vector_store: FAISS, save_path: str):
    """
    保存 FAISS 索引到本地

    Args:
        vector_store: FAISS 向量索引
        save_path: 保存路径
    """
    print(f"\n{'='*60}")
    print(f"保存 FAISS 索引...")
    print(f"保存路径: {save_path}")
    print(f"{'='*60}\n")

    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # 保存索引
        vector_store.save_local(save_path)

        print(f"FAISS 索引保存成功!\n")

    except Exception as e:
        print(f"保存 FAISS 索引失败: {str(e)}")
        raise


def load_faiss_index(load_path: str, embeddings: Embeddings) -> FAISS:
    """
    从本地加载 FAISS 索引

    Args:
        load_path: 加载路径
        embeddings: 嵌入模型

    Returns:
        FAISS 向量索引
    """
    print(f"\n{'='*60}")
    print(f"加载 FAISS 索引...")
    print(f"加载路径: {load_path}")
    print(f"{'='*60}\n")

    try:
        vector_store = FAISS.load_local(load_path, embeddings, allow_dangerous_deserialization=True)
        print(f"FAISS 索引加载成功!\n")
        return vector_store
    except Exception as e:
        print(f"加载 FAISS 索引失败: {str(e)}")
        raise


def build_and_save_vector_store(
    db_name: str = "scholar_db",
    collection_name: str = "papers",
    save_path: str = None,
    split_strategy: str = "recursive",
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> FAISS:
    """
    完整流程：从 MongoDB 加载数据、构建向量索引、保存到本地

    Args:
        db_name: 数据库名称
        collection_name: 集合名称
        save_path: 保存路径（默认: 项目根目录下的 faiss_index）
        split_strategy: 分割策略
            - "recursive": 递归字符分割（快速）
            - "structured": 结构化分割（按字段）
        chunk_size: 文本块大小（仅用于递归分割）
        chunk_overlap: 文本块重叠大小（仅用于递归分割）

    Returns:
        FAISS 向量索引
    """
    print(f"\n{'#'*60}")
    print(f"# 开始构建 RAG 向量库")
    print(f"# 数据库: {db_name}.{collection_name}")
    print(f"# 分割策略: {split_strategy}")

    import time
    print(f"# 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}\n")

    start_time = time.time()

    try:
        # 1. 初始化嵌入模型（使用本地模型，避免API限制）
        print("初始化本地嵌入模型...")
        use_local = True  # 设置为False使用智谱API
        if use_local:
            embeddings = LocalEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
        else:
            print("初始化智谱 AI 嵌入模型...")
            api_key = os.getenv("DASHSCOPE_API_KEY", "")
            embeddings = ZhipuEmbeddings(api_key=api_key, model="embedding-3")

        print("嵌入模型初始化完成\n")

        # 2. 从 MongoDB 加载论文数据
        papers = load_papers_from_mongodb(db_name, collection_name)

        if not papers:
            print("错误: 没有论文数据，无法构建向量库!")
            return None

        # 3. 准备文档
        documents = prepare_documents_for_embedding(papers)

        # 4. 构建向量索引
        vector_store = build_faiss_index(
            documents,
            embeddings,
            split_strategy,
            chunk_size,
            chunk_overlap
        )

        # 5. 保存索引
        if save_path is None:
            # 默认保存到项目根目录
            save_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "faiss_index")

        save_faiss_index(vector_store, save_path)

        # 统计信息
        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"\n{'#'*60}")
        print(f"# 向量库构建完成!")
        print(f"# 论文数量: {len(papers)}")
        print(f"# 文档数量: {len(documents)}")
        print(f"# 分割策略: {split_strategy}")
        print(f"# 耗时: {elapsed_time:.2f} 秒")
        print(f"# 保存路径: {save_path}")
        print(f"{'#'*60}\n")

        return vector_store

    except Exception as e:
        print(f"\n{'#'*60}")
        print(f"# 向量库构建失败!")
        print(f"# 错误: {str(e)}")
        print(f"{'#'*60}\n")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # 测试构建向量库 - 使用语义分割
    build_and_save_vector_store(
        db_name="scholar_db",
        collection_name="papers",
        save_path="./faiss_index",
        split_strategy="semantic",  # 尝试: "semantic", "recursive", "structured"
        chunk_size=500,
        chunk_overlap=50,
        breakpoint_threshold_type="percentile"  # 尝试: "percentile", "standard_deviation", "interquartile"
    )
