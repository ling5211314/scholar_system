"""混合检索模块 - 结合语义检索和关键词检索（BM25）"""

import math
from typing import List, Dict, Any, Tuple
from collections import Counter
import re


class BM25Retriever:
    """
    BM25 关键词检索器

    BM25 是一种经典的文本检索算法，基于词频和文档长度进行相关性评分
    """

    def __init__(
        self,
        documents: List[str],
        k1: float = 1.2,
        b: float = 0.75,
        epsilon: float = 0.25
    ):
        """
        初始化 BM25 检索器

        Args:
            documents: 文档列表
            k1: 控制词频饱和度（通常 1.2-2.0）
            b: 控制文档长度归一化（通常 0.75）
            epsilon: 平滑参数
        """
        self.documents = documents
        self.k1 = k1
        self.b = b
        self.epsilon = epsilon

        # 预处理：分词
        self.tokenized_docs = [self._tokenize(doc) for doc in documents]

        # 构建 IDF 词典
        self.idf = self._build_idf()

        # 计算文档平均长度
        self.avg_doc_length = sum(len(tokens) for tokens in self.tokenized_docs) / len(self.tokenized_docs)

    def _tokenize(self, text: str) -> List[str]:
        """
        分词（简单实现，支持中文和英文）

        Args:
            text: 输入文本

        Returns:
            分词列表
        """
        # 中文分词：按字符分割
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)

        # 英文分词：按单词分割（转小写）
        english_words = re.findall(r'[a-zA-Z]+', text.lower())

        # 合并中文和英文
        tokens = chinese_chars + english_words

        return tokens

    def _build_idf(self) -> Dict[str, float]:
        """
        构建 IDF (Inverse Document Frequency) 词典

        Returns:
            IDF 词典
        """
        # 计算文档频率
        df = Counter()
        for tokens in self.tokenized_docs:
            # 每个词在文档中只计数一次
            unique_tokens = set(tokens)
            df.update(unique_tokens)

        # 计算总文档数
        total_docs = len(self.tokenized_docs)

        # 计算 IDF（添加平滑）
        idf = {}
        for term, freq in df.items():
            # IDF = log((N - df(t) + 0.5) / (df(t) + 0.5))
            idf[term] = math.log((total_docs - freq + 0.5) / (freq + 0.5) + 1.0)

        # 添加平滑，避免零分
        self._max_idf = max(idf.values()) if idf else 0.0
        for term in idf:
            idf[term] = max(idf[term], self._max_idf * self.epsilon)

        return idf

    def _score_document(self, query_tokens: List[str], doc_tokens: List[str], doc_length: int) -> float:
        """
        计算单个文档的 BM25 分数

        Args:
            query_tokens: 查询词列表
            doc_tokens: 文档词列表
            doc_length: 文档长度

        Returns:
            BM25 分数
        """
        score = 0.0

        # 计算文档词频
        doc_tf = Counter(doc_tokens)

        for token in query_tokens:
            if token in doc_tf and token in self.idf:
                # BM25 公式
                tf = doc_tf[token]
                idf = self.idf[token]

                # 标准化文档长度
                length_norm = 1 - self.b + self.b * (doc_length / self.avg_doc_length)

                # BM25 分数
                score += idf * (tf * (self.k1 + 1)) / (tf + self.k1 * length_norm)

        return score

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """
        检索最相关的文档

        Args:
            query: 查询文本
            top_k: 返回前 k 个结果

        Returns:
            (文档索引, 分数) 列表
        """
        # 分词查询
        query_tokens = self._tokenize(query)

        # 计算每个文档的分数
        scores = []
        for idx, doc_tokens in enumerate(self.tokenized_docs):
            score = self._score_document(query_tokens, doc_tokens, len(doc_tokens))
            scores.append((idx, score))

        # 排序并返回前 k 个
        scores.sort(key=lambda x: x[1], reverse=True)

        return scores[:top_k]


class HybridRetriever:
    """
    混合检索器 - 结合语义检索和关键词检索

    使用加权平均合并两种检索结果
    """

    def __init__(
        self,
        documents: List[str],
        semantic_scores: List[List[float]],  # 语义相似度分数矩阵
        semantic_weight: float = 0.7,
        bm25_weight: float = 0.3
    ):
        """
        初始化混合检索器

        Args:
            documents: 文档列表
            semantic_scores: 语义相似度分数列表 [query_doc_scores]
            semantic_weight: 语义检索权重
            bm25_weight: BM25 检索权重
        """
        self.documents = documents
        self.semantic_scores = semantic_scores
        self.semantic_weight = semantic_weight
        self.bm25_weight = bm25_weight

        # 归一化权重
        total_weight = semantic_weight + bm25_weight
        self.semantic_weight /= total_weight
        self.bm25_weight /= total_weight

        # 初始化 BM25 检索器
        self.bm25_retriever = BM25Retriever(documents)

    def retrieve(self, query: str, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        混合检索

        Args:
            query: 查询文本
            query_embedding: 查询的嵌入向量
            top_k: 返回前 k 个结果

        Returns:
            检索结果列表
            [
                {
                    "index": 文档索引,
                    "document": 文档内容,
                    "semantic_score": 语义分数,
                    "bm25_score": BM25分数,
                    "hybrid_score": 混合分数
                },
                ...
            ]
        """
        # 1. BM25 检索
        bm25_results = self.bm25_retriever.retrieve(query, top_k=top_k * 2)  # 多取一些
        bm25_scores = {idx: score for idx, score in bm25_results}

        # 2. 使用语义分数（已经计算过）
        # 这里简化处理，实际应用中可以实时计算语义相似度
        # 暂时使用文档索引作为示例
        semantic_scores = {i: 0.0 for i in range(len(self.documents))}

        # 3. 合并分数
        hybrid_scores = []
        for idx in range(len(self.documents)):
            bm25_score = bm25_scores.get(idx, 0.0)
            semantic_score = semantic_scores.get(idx, 0.0)

            # 加权平均
            hybrid_score = (
                self.semantic_weight * semantic_score +
                self.bm25_weight * bm25_score
            )

            hybrid_scores.append({
                "index": idx,
                "document": self.documents[idx],
                "semantic_score": semantic_score,
                "bm25_score": bm25_score,
                "hybrid_score": hybrid_score
            })

        # 4. 排序并返回前 k 个
        hybrid_scores.sort(key=lambda x: x["hybrid_score"], reverse=True)

        return hybrid_scores[:top_k]

    def retrieve_with_rerank(
        self,
        query: str,
        initial_results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        使用混合检索重排序结果

        适用于已经有语义检索结果，需要用 BM25 增强的场景

        Args:
            query: 查询文本
            initial_results: 初始检索结果（来自语义检索）
            top_k: 返回前 k 个结果

        Returns:
            重排序后的结果列表
        """
        # BM25 检索
        bm25_results = self.bm25_retriever.retrieve(query, top_k=top_k * 2)
        bm25_scores = {idx: score for idx, score in bm25_results}

        # 重排序初始结果
        reranked = []
        for result in initial_results:
            idx = result.get("index", -1)
            semantic_score = result.get("score", 0.0)
            bm25_score = bm25_scores.get(idx, 0.0)

            # 加权平均
            hybrid_score = (
                self.semantic_weight * semantic_score +
                self.bm25_weight * bm25_score
            )

            result_copy = result.copy()
            result_copy["bm25_score"] = bm25_score
            result_copy["hybrid_score"] = hybrid_score

            reranked.append(result_copy)

        # 排序
        reranked.sort(key=lambda x: x["hybrid_score"], reverse=True)

        return reranked[:top_k]


def normalize_scores(scores: List[float]) -> List[float]:
    """
    归一化分数到 [0, 1] 区间

    Args:
        scores: 分数列表

    Returns:
        归一化后的分数列表
    """
    if not scores:
        return []

    min_score = min(scores)
    max_score = max(scores)

    if max_score == min_score:
        return [1.0] * len(scores)

    return [(score - min_score) / (max_score - min_score) for score in scores]


def combine_results(
    semantic_results: List[Tuple[int, float]],
    bm25_results: List[Tuple[int, float]],
    semantic_weight: float = 0.7,
    bm25_weight: float = 0.3,
    top_k: int = 5
) -> List[Tuple[int, float]]:
    """
    合并语义检索和 BM25 检索结果

    Args:
        semantic_results: 语义检索结果 [(索引, 分数), ...]
        bm25_results: BM25 检索结果 [(索引, 分数), ...]
        semantic_weight: 语义检索权重
        bm25_weight: BM25 检索权重
        top_k: 返回前 k 个结果

    Returns:
        合并后的结果 [(索引, 混合分数), ...]
    """
    # 归一化权重
    total_weight = semantic_weight + bm25_weight
    semantic_weight /= total_weight
    bm25_weight /= total_weight

    # 构建分数字典
    semantic_dict = dict(semantic_results)
    bm25_dict = dict(bm25_results)

    # 收集所有文档索引
    all_indices = set(semantic_dict.keys()) | set(bm25_dict.keys())

    # 合并分数
    combined_scores = []
    for idx in all_indices:
        semantic_score = semantic_dict.get(idx, 0.0)
        bm25_score = bm25_dict.get(idx, 0.0)

        hybrid_score = semantic_weight * semantic_score + bm25_weight * bm25_score
        combined_scores.append((idx, hybrid_score))

    # 排序并返回前 k 个
    combined_scores.sort(key=lambda x: x[1], reverse=True)

    return combined_scores[:top_k]


if __name__ == "__main__":
    # 测试 BM25 检索器
    documents = [
        "深度学习在医学图像分割中的应用",
        "卷积神经网络在计算机视觉中的研究",
        "自然语言处理技术的发展与挑战",
        "机器学习算法的比较与分析",
        "强化学习在游戏AI中的应用"
    ]

    print("初始化 BM25 检索器...")
    retriever = BM25Retriever(documents)

    query = "深度学习医学图像"
    print(f"\n查询: {query}")

    results = retriever.retrieve(query, top_k=3)

    print("\n检索结果:")
    for idx, score in results:
        print(f"{idx + 1}. [{score:.4f}] {documents[idx]}")

    # 测试混合检索
    print("\n" + "="*60)
    print("测试混合检索（模拟）")
    print("="*60)

    semantic_results = [(0, 0.95), (1, 0.70), (2, 0.30)]
    bm25_results = [(0, 0.85), (3, 0.65), (1, 0.55)]

    print(f"\n语义检索结果: {semantic_results}")
    print(f"BM25 检索结果: {bm25_results}")

    combined = combine_results(
        semantic_results,
        bm25_results,
        semantic_weight=0.7,
        bm25_weight=0.3,
        top_k=3
    )

    print(f"\n混合检索结果: {combined}")
