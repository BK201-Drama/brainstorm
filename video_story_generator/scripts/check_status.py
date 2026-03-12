"""
检查程序运行状态
显示：Python 进程、输出文件、临时文件
"""
import os
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
TEMP_DIR = PROJECT_ROOT / "temp"


def check_python_processes():
    """检查是否有 Python 进程在运行"""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
            capture_output=True,
            text=True,
            encoding='gbk'
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:  # 有表头
            print("=" * 60)
            print("Python 进程:")
            print("=" * 60)
            for line in lines[1:]:  # 跳过表头
                if line.strip():
                    parts = line.split(',')
                    if len(parts) >= 2:
                        pid = parts[1].strip('"')
                        name = parts[0].strip('"')
                        print(f"  PID: {pid:>8}  -  {name}")
            return True
        else:
            print("=" * 60)
            print("Python 进程: 无")
            print("=" * 60)
            return False
    except Exception as e:
        print(f"检查进程失败: {e}")
        return False


def check_output_files():
    """检查输出目录的最新文件"""
    print("\n" + "=" * 60)
    print("输出目录最新文件:")
    print("=" * 60)
    
    if not OUTPUT_DIR.exists():
        print("  输出目录不存在")
        return
    
    files = list(OUTPUT_DIR.glob("*"))
    if not files:
        print("  无文件")
        return
    
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    for f in files[:5]:
        mtime = time.ctime(f.stat().st_mtime)
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {f.name:30}  {mtime:20}  {size_mb:8.2f} MB")


def check_temp_files():
    """检查临时目录的最新文件"""
    print("\n" + "=" * 60)
    print("临时目录最新文件:")
    print("=" * 60)
    
    if not TEMP_DIR.exists():
        print("  临时目录不存在")
        return
    
    files = list(TEMP_DIR.rglob("*"))
    files = [f for f in files if f.is_file()]
    if not files:
        print("  无文件")
        return
    
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    for f in files[:10]:
        rel_path = f.relative_to(TEMP_DIR)
        mtime = time.ctime(f.stat().st_mtime)
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  {str(rel_path):40}  {mtime:20}  {size_mb:8.2f} MB")


def main():
    print("\n" + "=" * 60)
    print("程序运行状态检查")
    print("=" * 60)
    
    has_process = check_python_processes()
    check_output_files()
    check_temp_files()
    
    print("\n" + "=" * 60)
    if has_process:
        print("[状态] 程序正在运行中...")
    else:
        print("[状态] 程序未运行")
    print("=" * 60)


if __name__ == "__main__":
    main()
