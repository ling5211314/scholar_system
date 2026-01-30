import sys
sys.path.insert(0, '.')
from app.db.mongodb import get_mongo_client

client = get_mongo_client()
print('所有数据库:', [db for db in client.list_database_names() if db not in ['admin', 'local', 'config']])

# 检查每个数据库的集合
for db_name in client.list_database_names():
    if db_name not in ['admin', 'local', 'config']:
        db = client[db_name]
        print(f'\n数据库 {db_name} 中的集合:')
        for coll_name in db.list_collection_names():
            count = db[coll_name].count_documents({})
            print(f'  - {coll_name}: {count} 条文档')
