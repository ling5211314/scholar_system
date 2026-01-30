from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# 使用 .env 中的配置
mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
db_name = os.getenv("MONGODB_DB_NAME", "scholar_papers")

print(f"MongoDB URL: {mongo_url}")
print(f"数据库名称: {db_name}")

try:
    client = MongoClient(mongo_url)
    db = client[db_name]

    # 列出所有集合
    collections = db.list_collection_names()
    print(f"\n集合列表: {collections}")

    if 'papers' in collections:
        count = db.papers.count_documents({})
        print(f"\npapers 集合中论文数量: {count}")

        if count > 0:
            # 获取第一条文档查看字段
            sample = db.papers.find_one()
            print(f"\n示例文档字段:")
            for key in sample.keys():
                value = sample[key]
                if isinstance(value, str) and len(value) > 50:
                    print(f"  {key}: {value[:50]}...")
                else:
                    print(f"  {key}: {value}")
        else:
            print("\npapers 集合为空")
    else:
        print("\n未找到 papers 集合")

    # 如果没有 papers 集合，检查其他集合
    if len(collections) > 0 and 'papers' not in collections:
        print(f"\n可用的集合: {collections}")
        for coll_name in collections:
            count = db[coll_name].count_documents({})
            print(f"  {coll_name}: {count} 条文档")

except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()
