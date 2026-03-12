"""
视频下载模块
支持从YouTube、B站等平台下载视频
"""
import os
from pathlib import Path
from config import DOWNLOAD_CONFIG

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    print("警告: yt-dlp未安装，无法从网络下载视频，只能使用本地视频文件")


class VideoDownloader:
    def __init__(self):
        self.output_dir = DOWNLOAD_CONFIG["output_dir"]
        self.max_duration = DOWNLOAD_CONFIG["max_video_duration"]
        self.min_duration = DOWNLOAD_CONFIG["min_video_duration"]
        self.quality = DOWNLOAD_CONFIG["video_quality"]
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
    def download_video(self, url, output_filename=None):
        if not YT_DLP_AVAILABLE:
            print("错误: yt-dlp未安装，无法下载视频")
            return None
        """
        下载单个视频
        
        Args:
            url: 视频URL（支持YouTube、B站等）
            output_filename: 输出文件名（可选）
        
        Returns:
            下载的视频文件路径
        """
        if output_filename is None:
            output_filename = "%(title)s.%(ext)s"
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(self.output_dir, output_filename),
            'quiet': False,
            'no_warnings': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 先获取视频信息
                info = ydl.extract_info(url, download=False)
                duration = info.get('duration', 0)
                
                # 检查视频时长
                if duration < self.min_duration:
                    print(f"视频太短（{duration}秒），跳过")
                    return None
                if duration > self.max_duration:
                    print(f"视频太长（{duration}秒），将截取前{self.max_duration}秒")
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegVideoRemuxer',
                        'preferedformat': 'mp4',
                    }]
                    ydl_opts['postprocessor_args'] = {
                        'ffmpeg': ['-t', str(self.max_duration)]
                    }
                
                # 下载视频
                ydl.download([url])
                
                # 返回下载的文件路径
                filename = ydl.prepare_filename(info)
                if os.path.exists(filename):
                    return filename
                else:
                    # 尝试查找实际下载的文件
                    downloaded_files = list(Path(self.output_dir).glob("*.mp4"))
                    if downloaded_files:
                        return str(downloaded_files[-1])
                    return None
                    
        except Exception as e:
            print(f"下载视频失败: {e}")
            return None
    
    def download_multiple_videos(self, urls, target_duration=600):
        """
        下载多个视频，直到总时长接近目标时长
        
        Args:
            urls: 视频URL列表
            target_duration: 目标总时长（秒）
        
        Returns:
            下载的视频文件路径列表
        """
        downloaded_files = []
        total_duration = 0
        
        for url in urls:
            if total_duration >= target_duration:
                break
                
            print(f"正在下载: {url}")
            file_path = self.download_video(url)
            
            if file_path:
                # 获取视频时长
                try:
                    from moviepy import VideoFileClip
                    clip = VideoFileClip(file_path)
                    duration = clip.duration
                    clip.close()
                    
                    if total_duration + duration <= target_duration * 1.2:  # 允许20%的误差
                        downloaded_files.append(file_path)
                        total_duration += duration
                        print(f"已下载: {file_path}, 时长: {duration:.1f}秒, 总时长: {total_duration:.1f}秒")
                    else:
                        # 如果加上这个视频会超过目标时长，删除它
                        os.remove(file_path)
                        print(f"跳过此视频（会超过目标时长）")
                except Exception as e:
                    print(f"获取视频时长失败: {e}")
                    downloaded_files.append(file_path)
        
        print(f"下载完成，共 {len(downloaded_files)} 个视频，总时长: {total_duration:.1f}秒")
        return downloaded_files
    
    def download_from_local(self, file_paths):
        """
        使用本地已有的视频文件
        
        Args:
            file_paths: 本地视频文件路径列表
        
        Returns:
            视频文件路径列表
        """
        valid_files = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                valid_files.append(file_path)
            else:
                print(f"文件不存在: {file_path}")
        return valid_files
