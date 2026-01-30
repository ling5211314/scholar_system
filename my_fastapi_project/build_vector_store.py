"""
向量库构建脚本

使用方法:
1. 确保 MongoDB 正在运行
2. 确保已设置 DASHSCOPE_API_KEY 环境变量
3. 运行: python build_vector_store.py

支持的分割策略:
|- recursive: 递归字符分割（快速但简单）
|- structured: 结构化分割（按论文字段）
"""

import sys
import os
import argparse

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.rag.vector_store import build_and_save_vector_store


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='构建 RAG 向量库')
    parser.add_argument(
        '--strategy',
        type=str,
        default='recursive',
        choices=['recursive', 'structured'],
        help='文本分割策略 (默认: recursive)'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=500,
        help='文本块大小，仅用于 recursive 策略 (默认: 500)'
    )
    parser.add_argument(
        '--overlap',
        type=int,
        default=50,
        help='文本块重叠大小，仅用于 recursive 策略 (默认: 50)'
    )

    args = parser.parse_args()

    print("\n" + "="*70)
    print("                    向量库构建工具")
    print("="*70)

    print("\n配置参数:\n")
    print(f"  分割策略: {args.strategy}")
    print(f"  文本块大小: {args.chunk_size}")
    print(f"  重叠大小: {args.overlap}\n")

    try:
        # 构建并保存向量库
        vector_store = build_and_save_vector_store(
            db_name="scholar_papers",
            collection_name="scholar_papers",
            save_path="./faiss_index",  # 保存在项目根目录
            split_strategy=args.strategy,
            chunk_size=args.chunk_size,
            chunk_overlap=args.overlap
        )

        if vector_store:
            print("\n" + "="*70)
            print("              [OK] 向量库构建完成!")
            print("="*70 + "\n")
            print("下一步:")
            print("1. 重启 FastAPI 服务器")
            print("2. 访问 /api/chat/ask 接口进行问答")
            print("3. 测试混合检索功能\n")
        else:
            print("\n" + "="*70)
            print("              [FAIL] 向量库构建失败!")
            print("="*70 + "\n")

    except Exception as e:
        print(f"\n构建过程中发生错误: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
