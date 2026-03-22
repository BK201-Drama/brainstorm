"""
FFmpeg 相关工具
职责：ffmpeg 路径获取、视频静音处理、视频时长探测
"""
import os
import subprocess
import shutil
import logging

logger = logging.getLogger(__name__)

# ── ffmpeg 路径 ──────────────────────────────────────────────
try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG_PATH = shutil.which("ffmpeg") or "ffmpeg"


# ── 静音处理 ─────────────────────────────────────────────────
def remove_audio_from_video(video_path, ffmpeg_path=None):
    """
    使用 ffmpeg 移除视频中的音频轨道（静音处理）。
    采用 -c:v copy 方式，仅去除音频流，不重编码视频，速度极快。

    Args:
        video_path: 视频文件路径
        ffmpeg_path: ffmpeg 可执行文件路径（默认使用全局 FFMPEG_PATH）

    Returns:
        处理后的视频文件路径，失败返回原路径
    """
    ffmpeg_path = ffmpeg_path or FFMPEG_PATH

    if not os.path.exists(video_path):
        return video_path

    temp_output = video_path + ".muted.mp4"
    try:
        cmd = [
            ffmpeg_path,
            "-i", video_path,
            "-an",              # 移除音频
            "-c:v", "copy",     # 视频流直接复制
            "-y",               # 覆盖输出
            temp_output,
        ]
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300,
        )
        if result.returncode == 0 and os.path.exists(temp_output):
            os.replace(temp_output, video_path)
            return video_path
        else:
            if os.path.exists(temp_output):
                os.remove(temp_output)
            logger.warning("静音处理失败(ffmpeg返回码=%d): %s", result.returncode, video_path)
            return video_path
    except Exception as e:
        if os.path.exists(temp_output):
            os.remove(temp_output)
        logger.warning("静音处理出错: %s", e)
        return video_path


# ── 时长探测 ─────────────────────────────────────────────────
def _get_ffprobe_path(ffmpeg_path=None):
    """根据 ffmpeg 路径推断 ffprobe 路径"""
    ffmpeg_path = ffmpeg_path or FFMPEG_PATH
    ffprobe_path = ffmpeg_path.replace("ffmpeg", "ffprobe")
    if shutil.which(ffprobe_path):
        return ffprobe_path

    # 尝试同目录下的 ffprobe
    ffprobe_dir = os.path.dirname(ffmpeg_path)
    candidate = os.path.join(ffprobe_dir, "ffprobe")
    if os.name == "nt":
        candidate += ".exe"
    if os.path.exists(candidate):
        return candidate

    return "ffprobe"


def clip_video(video_path, start_time=0.0, duration=None, ffmpeg_path=None):
    """
    使用 ffmpeg 对视频做快速剪辑（解压/放松视频常用）。

    Args:
        video_path: 输入视频路径
        start_time: 起始秒数
        duration: 剪辑时长（秒），None 表示从 start 到结尾
        ffmpeg_path: ffmpeg 路径

    Returns:
        剪辑后文件路径（失败返回原路径）
    """
    ffmpeg_path = ffmpeg_path or FFMPEG_PATH

    if not os.path.exists(video_path):
        return video_path

    start_time = max(0.0, float(start_time or 0.0))
    if duration is not None:
        duration = float(duration)
        if duration <= 0:
            return video_path

    temp_output = video_path + ".clip.mp4"

    cmd = [ffmpeg_path, "-ss", str(start_time), "-i", video_path]
    if duration is not None:
        cmd += ["-t", str(duration)]
    cmd += ["-c:v", "copy", "-c:a", "copy", "-y", temp_output]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300,
        )
        if result.returncode == 0 and os.path.exists(temp_output):
            os.replace(temp_output, video_path)
            return video_path

        # copy 模式在非关键帧起点可能失败，fallback 重编码
        if os.path.exists(temp_output):
            os.remove(temp_output)

        cmd_reencode = [ffmpeg_path, "-ss", str(start_time), "-i", video_path]
        if duration is not None:
            cmd_reencode += ["-t", str(duration)]
        cmd_reencode += ["-c:v", "libx264", "-c:a", "aac", "-y", temp_output]

        result = subprocess.run(
            cmd_reencode,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=600,
        )
        if result.returncode == 0 and os.path.exists(temp_output):
            os.replace(temp_output, video_path)
            return video_path

        if os.path.exists(temp_output):
            os.remove(temp_output)
        logger.warning("视频剪辑失败(ffmpeg返回码=%d): %s", result.returncode, video_path)
        return video_path

    except Exception as e:
        if os.path.exists(temp_output):
            os.remove(temp_output)
        logger.warning("视频剪辑出错: %s", e)
        return video_path


def get_video_duration(video_path, ffmpeg_path=None):
    """
    获取视频时长（秒）。优先使用 ffprobe（更快），失败则 fallback 到 moviepy。

    Args:
        video_path: 视频文件路径
        ffmpeg_path: ffmpeg 路径（用于推断 ffprobe 路径）

    Returns:
        时长（秒），失败返回 None
    """
    ffprobe_path = _get_ffprobe_path(ffmpeg_path)
    try:
        cmd = [
            ffprobe_path,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path,
        ]
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30
        )
        if result.returncode == 0:
            return float(result.stdout.decode().strip())
    except Exception:
        pass

    # fallback: 使用 moviepy
    try:
        from moviepy import VideoFileClip
        clip = VideoFileClip(video_path)
        duration = clip.duration
        clip.close()
        return duration
    except Exception:
        return None
