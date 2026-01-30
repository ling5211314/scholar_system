from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class Paper(BaseModel):
    """论文模型"""
    文献类型: Optional[str] = None
    论文题目: Optional[str] = None
    作者: Optional[str] = None
    期刊_会议名称: Optional[str] = Field(None, alias="期刊/会议名称")
    发表时间: Optional[str] = None
    关键词: Optional[str] = None
    摘要: Optional[str] = None

    model_config = ConfigDict(
        validate_by_name=True,
        populate_by_name=True,
        use_enum_values=False
    )


class QueryRequest(BaseModel):
    """查询请求模型"""
    message: str  # 用户消息


class PaperSearchResult(BaseModel):
    """搜索结果模型"""
    query: dict
    papers: List[Paper]
    total: int
