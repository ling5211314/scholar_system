"""
数据库初始化脚本
运行此脚本会创建数据库表
"""
from app.db.session import engine, Base
from app.models.user import User

def init_database():
    """创建所有数据库表"""
    print("开始创建数据库表...")
    
    try:
        Base.metadata.create_all(bind=engine)
        print("数据库表创建成功！")
        print("\n已创建的表:")
        for table_name in Base.metadata.tables:
            print(f"  - {table_name}")
    except Exception as e:
        print(f"创建数据库表时出错: {e}")
        raise

if __name__ == "__main__":
    init_database()
