"""
视频故事生成器 - 唯一入口
从项目根目录运行：python main.py --help
"""
import sys
import os

# 确保项目根目录在 sys.path 中（支持 from src.xxx import ...）
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.pipeline import main

if __name__ == "__main__":
    main()
