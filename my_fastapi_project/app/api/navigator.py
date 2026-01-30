from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os
from dotenv import load_dotenv
import httpx
import json

load_dotenv()

router = APIRouter(prefix="/api/navigator", tags=["研究向导"])


class ResearchRequest(BaseModel):
    topic: str
    language: str = "zh"  # zh or en


class Paper(BaseModel):
    title: str
    authors: list[str]
    year: int
    venue: str
    cited_by_count: int = 0
    url: str


class Scholar(BaseModel):
    name: str
    institution: str
    research_areas: list[str]
    profile_url: str


class ResearchPathResponse(BaseModel):
    topic: str
    path: dict
    scholars: list[Scholar]


# 初始化 GLM-4 模型
api_key = os.getenv("DASHSCOPE_API_KEY", "")
if not api_key:
    raise ValueError("未设置 DASHSCOPE_API_KEY 环境变量")

llm = ChatZhipuAI(model="glm-4", temperature=0.7, api_key=api_key)


def generate_research_path(topic: str, language: str = "zh") -> dict:
    """
    使用 GLM-4 生成研究路径
    """
    lang_instruction = "中文" if language == "zh" else "英文"
    
    prompt_template = ChatPromptTemplate.from_template("""
你是一个专业的学术研究向导。请为用户的研究领域 "{topic}" 生成一条学习路径。

请严格按照以下JSON格式返回结果（不要添加任何其他文字说明）：

{{
  "foundation": [
    {{
      "title": "经典奠基性论文标题",
      "authors": ["作者1", "作者2"],
      "year": 2018,
      "venue": "会议/期刊名称（如 NeurIPS, CVPR, ICML等）",
      "cited_by_count": 引用次数,
      "url": "论文链接（如果不确定，可以使用 https://arxiv.org/placeholder）"
    }}
  ],
  "core": [
    {{
      "title": "核心论文标题",
      "authors": ["作者1", "作者2"],
      "year": 2023,
      "venue": "会议/期刊名称",
      "cited_by_count": 引用次数,
      "url": "论文链接"
    }}
  ],
  "frontier": [
    {{
      "title": "前沿论文标题",
      "authors": ["作者1", "作者2"],
      "year": 2024,
      "venue": "会议/期刊名称",
      "cited_by_count": 引用次数,
      "url": "论文链接"
    }}
  ]
}}

要求：
1. foundation：2-3篇经典奠基性论文（高被引、5年前以上）
2. core：3-4篇近3年高质量顶会论文
3. frontier：2-3篇最近6个月的最新预印本
4. 引用次数和年份要尽量准确
5. 论文链接优先使用 arxiv.org

请使用{lang_instruction}输出。
""")

    try:
        chain = prompt_template | llm
        response = chain.invoke({"topic": topic, "lang_instruction": lang_instruction})
        
        # 将 AIMessage 转换为字符串
        response_str = str(response.content) if hasattr(response, 'content') else str(response)
        
        # 尝试解析 JSON
        json_start = response_str.find("{")
        json_end = response_str.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            json_str = response_str[json_start:json_end]
            result = json.loads(json_str)
            return result
        else:
            # 如果没有找到 JSON，返回结构化数据
            return {
                "foundation": [],
                "core": [],
                "frontier": []
            }
    except Exception as e:
        print(f"生成研究路径时出错: {e}")
        return {
            "foundation": [],
            "core": [],
            "frontier": []
        }


def generate_scholars(topic: str, language: str = "zh") -> list[dict]:
    """
    使用 GLM-4 推荐核心学者
    """
    lang_instruction = "中文" if language == "zh" else "英文"
    
    prompt_template = ChatPromptTemplate.from_template("""
请为研究领域 "{topic}" 推荐 3-5 位核心学者。

请严格按照以下JSON格式返回结果（不要添加任何其他文字说明）：

[
  {{
    "name": "学者姓名",
    "institution": "机构名称",
    "research_areas": ["研究方向1", "研究方向2"],
    "profile_url": "个人主页链接（如果不确定，可以使用 https://openalex.org/placeholder）"
  }}
]

要求：
1. 选择该领域公认的权威学者
2. 确保机构名称准确
3. 研究方向要简洁明确

请使用{lang_instruction}输出。
""")

    try:
        chain = prompt_template | llm
        response = chain.invoke({"topic": topic, "lang_instruction": lang_instruction})
        
        # 将 AIMessage 转换为字符串
        response_str = str(response.content) if hasattr(response, 'content') else str(response)
        
        # 尝试解析 JSON
        json_start = response_str.find("[")
        json_end = response_str.rfind("]") + 1
        if json_start != -1 and json_end > json_start:
            json_str = response_str[json_start:json_end]
            result = json.loads(json_str)
            return result
        else:
            return []
    except Exception as e:
        print(f"生成学者推荐时出错: {e}")
        return []


@router.post("/generate", response_model=ResearchPathResponse, summary="生成研究路径")
async def generate_navigator(request: ResearchRequest):
    """
    根据研究方向生成学习路径和学者推荐
    """
    try:
        print(f"生成研究路径: {request.topic}")
        
        # 并发生成路径和学者推荐
        path = generate_research_path(request.topic, request.language)
        scholars = generate_scholars(request.topic, request.language)
        
        return ResearchPathResponse(
            topic=request.topic,
            path=path,
            scholars=scholars
        )
    except Exception as e:
        print(f"生成研究路径时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")
