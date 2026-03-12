"""
入口脚本 - 从项目根目录运行
"""
import sys
import os

# 添加src目录到路径
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

# 导入并运行主程序
from main import main

if __name__ == "__main__":
    main()
