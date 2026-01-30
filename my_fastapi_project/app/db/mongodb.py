"""数据库连接模块 - MongoDB 连接"""

from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()


def get_mongo_client():
    """
    获取 MongoDB 客户端连接

    Returns:
        MongoClient: MongoDB 客户端实例
    """
    # 从环境变量读取连接字符串，如果没有则使用默认值
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

    try:
        client = MongoClient(mongo_url)
        # 测试连接
        client.admin.command('ping')
        print(f"MongoDB 连接成功: {mongo_url}")
        return client
    except Exception as e:
        print(f"MongoDB 连接失败: {str(e)}")
        raise


def get_mongo_database(db_name: str):
    """
    获取指定数据库

    Args:
        db_name: 数据库名称

    Returns:
        Database: MongoDB 数据库实例
    """
    client = get_mongo_client()
    return client[db_name]


def get_mongo_collection(db_name: str, collection_name: str):
    """
    获取指定集合

    Args:
        db_name: 数据库名称
        collection_name: 集合名称

    Returns:
        Collection: MongoDB 集合实例
    """
    db = get_mongo_database(db_name)
    return db[collection_name]
