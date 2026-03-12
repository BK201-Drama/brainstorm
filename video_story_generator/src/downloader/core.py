"""
视频下载核心逻辑
职责：单个视频下载、并发下载编排、时长筛选
"""
import os
import uuid
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..config import DOWNLOAD_CONFIG
from ..utils.ffmpeg import FFMPEG_PATH, remove_audio_from_video, get_video_duration
from ..utils.file_naming import find_downloaded_file

logger = logging.getLogger(__name__)

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    logger.warning("yt-dlp未安装，无法从网络下载视频，只能使用本地视频文件")


class VideoDownloader:
    """视频下载器：负责从网络平台下载视频"""

    def __init__(self, output_dir=None):
        self.output_dir = output_dir or DOWNLOAD_CONFIG["output_dir"]
        self.max_duration = DOWNLOAD_CONFIG["max_video_duration"]
        self.min_duration = DOWNLOAD_CONFIG["min_video_duration"]
        self.quality = DOWNLOAD_CONFIG["video_quality"]
        self.max_workers = DOWNLOAD_CONFIG["max_concurrent_downloads"]
        self.remove_audio = DOWNLOAD_CONFIG["remove_audio"]
        self.socket_timeout = DOWNLOAD_CONFIG["socket_timeout"]
        self.retries = DOWNLOAD_CONFIG["retries"]
        os.makedirs(self.output_dir, exist_ok=True)

    # ── yt-dlp 选项 ──────────────────────────────────────────
    def _make_ydl_opts(self, output_template):
        """构建 yt-dlp 选项字典"""
        return {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_template,
            'quiet': False,
            'no_warnings': False,
            'merge_output_format': 'mp4',
            'ffmpeg_location': FFMPEG_PATH,
            'noplaylist': True,
            'socket_timeout': self.socket_timeout,
            'retries': self.retries,
        }

    # ── 单视频下载 ────────────────────────────────────────────
    def download_video(self, url, output_filename=None):
        """
        下载单个视频（含时长过滤 + 静音处理 + 唯一命名）。

        Args:
            url: 视频URL（支持YouTube、B站等）
            output_filename: 输出文件名（可选，为空则自动生成唯一名称）

        Returns:
            下载的视频文件路径，失败返回 None
        """
        if not YT_DLP_AVAILABLE:
            print("错误: yt-dlp未安装，无法下载视频")
            return None

        # 生成唯一文件名，避免覆盖
        if output_filename is None:
            short_id = uuid.uuid4().hex[:8]
            output_filename = f"video_{short_id}.%(ext)s"

        output_template = os.path.join(self.output_dir, output_filename)
        ydl_opts = self._make_ydl_opts(output_template)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 先获取视频信息（不下载）
                info = ydl.extract_info(url, download=False)
                duration = info.get('duration', 0)
                title = info.get('title', 'unknown')

                # 时长过滤
                if duration and duration < self.min_duration:
                    print(f"视频太短（{duration}秒 < {self.min_duration}秒），跳过: {title}")
                    return None
                if duration and duration > self.max_duration:
                    print(f"视频太长（{duration}秒 > {self.max_duration}秒），跳过: {title}")
                    return None

                print(f"  正在下载: {title} ({duration}秒)")

                # 下载
                ydl.download([url])
                filename = ydl.prepare_filename(info)

                # 查找实际下载的文件
                downloaded_file = find_downloaded_file(filename, fallback_dir=self.output_dir)

                if downloaded_file:
                    # 静音处理
                    if self.remove_audio:
                        print(f"  正在移除音频: {os.path.basename(downloaded_file)}")
                        remove_audio_from_video(downloaded_file)
                    return downloaded_file
                else:
                    return None

        except Exception as e:
            print(f"下载视频失败: {e}")
            return None

    # ── 线程安全封装 ──────────────────────────────────────────
    def _download_video_safe(self, url, output_filename=None):
        """线程安全的下载方法（用于并发下载）"""
        try:
            file_path = self.download_video(url, output_filename)
            return (url, file_path, None)
        except Exception as e:
            return (url, None, str(e))

    # ── 并发下载 ──────────────────────────────────────────────
    def download_videos_concurrent(self, urls, max_workers=None):
        """
        并发下载多个视频。

        Args:
            urls: 视频URL列表
            max_workers: 最大并发数（默认使用配置值）

        Returns:
            下载成功的文件路径列表
        """
        if not urls:
            return []

        workers = min(max_workers or self.max_workers, len(urls))
        print(f"开始并发下载 {len(urls)} 个视频（并发数: {workers}）...")

        downloaded_files = []
        failed_urls = []

        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_url = {
                executor.submit(self._download_video_safe, url): url
                for url in urls
            }
            for future in as_completed(future_to_url):
                url, file_path, error = future.result()
                if file_path:
                    downloaded_files.append(file_path)
                    print(f"✓ 下载成功: {os.path.basename(file_path)}")
                else:
                    failed_urls.append(url)
                    err_msg = f" - {error}" if error else ""
                    print(f"✗ 下载失败: {url}{err_msg}")

        print(f"\n下载完成: 成功 {len(downloaded_files)}/{len(urls)}")
        if failed_urls:
            print("失败的URL:")
            for url in failed_urls:
                print(f"  - {url}")

        return downloaded_files

    # ── 按目标时长下载 ────────────────────────────────────────
    def download_multiple_videos(self, urls, target_duration=600):
        """
        并发下载多个视频，按时长筛选到目标时长。

        Args:
            urls: 视频URL列表
            target_duration: 目标总时长（秒）

        Returns:
            下载的视频文件路径列表
        """
        downloaded_files = self.download_videos_concurrent(urls)
        if not downloaded_files:
            return []

        selected_files = []
        total_duration = 0

        for file_path in downloaded_files:
            try:
                duration = get_video_duration(file_path)
                if duration is None:
                    selected_files.append(file_path)
                    continue

                if total_duration + duration <= target_duration * 1.2:
                    selected_files.append(file_path)
                    total_duration += duration
                    print(f"已选择: {os.path.basename(file_path)}, 时长: {duration:.1f}秒, 累计: {total_duration:.1f}秒")
                else:
                    print(f"跳过（会超过目标时长）: {os.path.basename(file_path)}")

                if total_duration >= target_duration:
                    break
            except Exception as e:
                print(f"获取视频时长失败: {e}")
                selected_files.append(file_path)

        print(f"下载完成，共 {len(selected_files)} 个视频，总时长: {total_duration:.1f}秒")
        return selected_files

    # ── 本地文件 ──────────────────────────────────────────────
    @staticmethod
    def load_local_videos(file_paths):
        """
        校验并返回本地已有的视频文件路径。

        Args:
            file_paths: 本地视频文件路径列表

        Returns:
            存在的视频文件路径列表
        """
        valid_files = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                valid_files.append(file_path)
            else:
                print(f"文件不存在: {file_path}")
        return valid_files

    # 保持向后兼容
    download_from_local = load_local_videos
