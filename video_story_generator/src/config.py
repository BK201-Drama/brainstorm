"""
项目配置（纯常量定义，无副作用）
所有目录的实际创建由各模块在初始化时自行负责。
"""
import os

# 项目根目录（src 的父目录）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 视频相关 ──────────────────────────────────────────────────
VIDEO_CONFIG = {
    "target_duration": 30,            # 目标总时长（秒）：30秒（demo）
    "output_resolution": (1920, 1080),
    "fps": 30,
    "video_format": "mp4",
}

# ── 下载相关 ──────────────────────────────────────────────────
DOWNLOAD_CONFIG = {
    "output_dir": os.path.join(PROJECT_ROOT, "downloads"),
    "max_video_duration": 1800,       # 单个视频最大时长（秒）：30分钟
    "min_video_duration": 30,         # 单个视频最小时长（秒）
    "video_quality": "best",
    "max_concurrent_downloads": 4,
    "remove_audio": True,             # 下载后自动移除音频
    "socket_timeout": 60,
    "retries": 3,
}

# ── TTS 相关 ──────────────────────────────────────────────────
TTS_CONFIG = {
    "voice": "zh-CN-XiaoxiaoNeural",  # 可选：zh-CN-XiaoyiNeural（女）zh-CN-YunyangNeural（男）
    "rate": "+0%",
    "pitch": "+0Hz",
}

# ── 字幕相关 ──────────────────────────────────────────────────
SUBTITLE_CONFIG = {
    "font_size": 60,
    "font_color": "white",
    "bg_color": "black",
    "bg_opacity": 0.6,
    "position": "bottom",
    "margin": 50,
}

# ── 故事生成相关 ──────────────────────────────────────────────
STORY_CONFIG = {
    "min_words": 800,
    "max_words": 1500,
    "style": "故事型",
}

# ── 输出 / 临时目录 ──────────────────────────────────────────
OUTPUT_CONFIG = {
    "output_dir": os.path.join(PROJECT_ROOT, "output"),
    "temp_dir": os.path.join(PROJECT_ROOT, "temp"),
}
