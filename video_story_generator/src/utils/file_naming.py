"""
文件命名与查找工具
职责：生成唯一文件名、查找已下载文件
"""
import os
import uuid
from pathlib import Path


def get_unique_filename(output_dir, prefix="video", ext="mp4"):
    """
    生成唯一的文件名，避免覆盖已有文件。

    Args:
        output_dir: 输出目录
        prefix: 文件名前缀
        ext: 文件扩展名

    Returns:
        唯一的文件路径
    """
    short_id = uuid.uuid4().hex[:8]
    filename = f"{prefix}_{short_id}.{ext}"
    return os.path.join(output_dir, filename)


def find_downloaded_file(expected_path, fallback_dir=None):
    """
    查找实际下载的文件（yt-dlp 可能改变扩展名）。

    查找策略（按优先级）：
    1. 检查预期路径是否存在
    2. 尝试 .mp4 扩展名
    3. 按文件名前缀在目录中查找
    4. 取目录中最新的 .mp4 文件

    Args:
        expected_path: 预期的文件路径
        fallback_dir: 备选搜索目录

    Returns:
        实际文件路径，未找到返回 None
    """
    # 策略 1: 预期路径
    if os.path.exists(expected_path):
        return expected_path

    # 策略 2: .mp4 扩展名
    mp4_path = Path(expected_path).with_suffix('.mp4')
    if mp4_path.exists():
        return str(mp4_path)

    # 策略 3: 按前缀查找
    base_name = Path(expected_path).stem
    output_dir = os.path.dirname(expected_path) or fallback_dir
    if output_dir and os.path.isdir(output_dir):
        for f in os.listdir(output_dir):
            if f.startswith(base_name):
                return os.path.join(output_dir, f)

        # 策略 4: 最新 .mp4
        mp4_files = sorted(
            Path(output_dir).glob("*.mp4"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if mp4_files:
            return str(mp4_files[0])

    return None
