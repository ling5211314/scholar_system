from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import json
import re
from app.db.mongodb import get_mongo_collection
from app.models.paper import Paper, PaperSearchResult, QueryRequest

load_dotenv()

router = APIRouter(prefix="/api/papers", tags=["论文搜索"])


# 初始化 GLM-4 模型
api_key = os.getenv("DASHSCOPE_API_KEY", "")
if not api_key:
    raise ValueError("未设置 DASHSCOPE_API_KEY 环境变量")

llm = ChatZhipuAI(model="glm-4", temperature=0.1, api_key=api_key)


def parse_query_to_mongodb(message: str) -> dict:
    """
    使用 GLM-4 将自然语言查询转换为 MongoDB 查询条件
    """
    # 使用 f-string + 三重引号，避免 .format() 的花括号冲突
    prompt = f"""你是一个专业的学术查询助手。请将用户的自然语言查询转换为 MongoDB 查询条件。

数据库集合 papers 的字段如下（全部为中文）：
- 文献类型: 期刊 或 会议
- 论文题目: 论文标题
- 作者: 作者列表
- 期刊/会议名称: 期刊或会议名称（如 CVPR, ICLR, Pattern Recognition）
- 发表时间: 年份（如 2023, 2024）
- 关键词: 关键词列表（逗号分隔）
- 摘要: 论文摘要

用户消息: {message}

请生成 MongoDB 查询条件，格式为 Python dict。
例如：
- 年份查询: {{"发表时间": "2023"}}
- 关键词查询: {{"关键词": {{"$regex": "图像分割", "$options": "i"}}}}
- 多条件查询: {{"发表时间": "2023", "关键词": {{"$regex": "图像分割", "$options": "i"}}}}

重要说明：
1. 只返回 JSON 格式的查询条件，不要有任何其他文字
2. 使用正则表达式进行模糊匹配，并添加 $options: "i" 实现不区分大小写
3. 确保字段名与数据库字段名完全一致（使用中文）
4. 如果查询不明确，返回空字典 {{}}
5. 不要使用 $or、$and 等复杂操作符，保持简单查询
"""

    try:
        response_str = ""
        try:
            response = llm.invoke(prompt)
            response_str = str(response.content) if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"LLM调用出错: {e}")
            return {}

        # 清理可能的 markdown 代码块
        response_str = re.sub(r'```(?:python|json)?\s*', '', response_str, flags=re.IGNORECASE)
        response_str = re.sub(r'```\s*', '', response_str)

        # 提取最外层的 dict
        dict_start = response_str.find("{")
        dict_end = response_str.rfind("}") + 1
        if dict_start != -1 and dict_end > dict_start:
            dict_str = response_str[dict_start:dict_end]
            # 替换单引号为双引号（JSON 标准）
            dict_str = dict_str.replace("'", '"')
            # 修复可能的尾随逗号（非标准 JSON）
            dict_str = re.sub(r',\s*}', '}', dict_str)
            dict_str = re.sub(r',\s*\]', ']', dict_str)
            result = json.loads(dict_str)
            print(f"解析后的查询: {result}")
            return result
        else:
            print(f"未找到有效的dict: {response_str[:200]}")
            return {}
    except Exception as e:
        print(f"解析查询时出错: {e}")
        if 'response_str' in locals():
            print(f"原始响应: {response_str}")
        return {}


@router.post("/search", response_model=PaperSearchResult, summary="论文搜索")
async def search_papers(request: QueryRequest):
    """
    根据自然语言查询搜索论文
    """
    try:
        print(f"查询消息: {request.message}")

        # 将自然语言转换为 MongoDB 查询
        query = parse_query_to_mongodb(request.message)
        print(f"生成的查询: {query}")

        # 执行查询
        papers_collection = get_mongo_collection("scholar_papers", "scholar_papers")
        cursor = papers_collection.find(query).limit(50)

        # 转换结果
        papers = []
        for doc in cursor:
            # 移除 MongoDB 的 _id 字段
            if "_id" in doc:
                del doc["_id"]
            papers.append(Paper(**doc))

        return PaperSearchResult(
            query=query,
            papers=papers,
            total=len(papers)
        )
    except Exception as e:
        print(f"搜索论文时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/", summary="获取所有论文")
async def get_all_papers(limit: int = 50, skip: int = 0):
    """
    获取所有论文（分页）
    """
    try:
        papers_collection = get_mongo_collection("scholar_papers", "scholar_papers")
        cursor = papers_collection.find().skip(skip).limit(limit)

        papers = []
        for doc in cursor:
            if "_id" in doc:
                del doc["_id"]
            papers.append(Paper(**doc))

        total = papers_collection.count_documents({})

        return {
            "papers": papers,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.post("/execute", summary="直接执行 MongoDB 查询")
async def execute_query(query: dict = Body(..., description="MongoDB 查询条件")):
    """
    直接执行 MongoDB 查询
    """
    try:
        print(f"执行查询: {query}")

        papers_collection = get_mongo_collection("scholar_papers", "scholar_papers")
        cursor = papers_collection.find(query).limit(50)

        papers = []
        for doc in cursor:
            if "_id" in doc:
                del doc["_id"]
            papers.append(Paper(**doc))

        return {
            "query": query,
            "papers": papers,
            "total": len(papers)
        }
    except Exception as e:
        print(f"执行查询时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
