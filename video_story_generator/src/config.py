"""
配置文件
"""
import os

# 视频相关配置
VIDEO_CONFIG = {
    "target_duration": 600,  # 目标总时长（秒），10分钟 = 600秒
    "output_resolution": (1920, 1080),  # 输出分辨率
    "fps": 30,  # 帧率
    "video_format": "mp4",
}

# 获取项目根目录（src的父目录）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 视频下载配置
DOWNLOAD_CONFIG = {
    "output_dir": os.path.join(PROJECT_ROOT, "downloads"),  # 下载目录
    "max_video_duration": 300,  # 单个视频最大时长（秒），5分钟
    "min_video_duration": 30,  # 单个视频最小时长（秒）
    "video_quality": "best",  # 视频质量：best, worst, 720p, 1080p等
}

# TTS配置
TTS_CONFIG = {
    "voice": "zh-CN-XiaoxiaoNeural",  # 中文女声，可选：zh-CN-XiaoyiNeural（女）, zh-CN-YunyangNeural（男）
    "rate": "+0%",  # 语速：-50% 到 +100%
    "pitch": "+0Hz",  # 音调：-50Hz 到 +50Hz
}

# 字幕配置
SUBTITLE_CONFIG = {
    "font_size": 60,
    "font_color": "white",
    "bg_color": "black",
    "bg_opacity": 0.6,
    "position": "bottom",  # bottom, top, center
    "margin": 50,  # 距离边缘的像素
}

# 故事生成配置
STORY_CONFIG = {
    "min_words": 800,  # 最少字数
    "max_words": 1500,  # 最多字数
    "style": "故事会",  # 风格
}

# 输出配置
OUTPUT_CONFIG = {
    "output_dir": os.path.join(PROJECT_ROOT, "output"),
    "temp_dir": os.path.join(PROJECT_ROOT, "temp"),
}

# 创建必要的目录
for dir_name in [DOWNLOAD_CONFIG["output_dir"], OUTPUT_CONFIG["output_dir"], OUTPUT_CONFIG["temp_dir"]]:
    os.makedirs(dir_name, exist_ok=True)
