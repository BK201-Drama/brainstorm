"""
视频合成编排模块
职责：组织 拼接→配音→字幕 的流水线，生成最终视频
"""
import os

from ..config import OUTPUT_CONFIG
from .concatenator import VideoConcatenator
from .subtitle_renderer import SubtitleRenderer
from .audio_mixer import AudioMixer


class VideoCompositor:
    """
    最终视频合成器。
    按顺序调用 拼接器 → 音频混合器 → 字幕渲染器，生成完整视频。
    """

    def __init__(self):
        self.concatenator = VideoConcatenator()
        self.subtitle_renderer = SubtitleRenderer()
        self.audio_mixer = AudioMixer()
        self.output_dir = OUTPUT_CONFIG["output_dir"]
        self.temp_dir = OUTPUT_CONFIG["temp_dir"]
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

    def concatenate_videos(self, video_files, output_file, loop_if_needed=True):
        """拼接多个视频（委托给 VideoConcatenator）"""
        return self.concatenator.concatenate(video_files, output_file, loop_if_needed)

    def create_final_video(self, video_file, audio_file, subtitle_timeline, output_file):
        """
        创建最终视频（视频 + 配音 + 字幕）。

        Args:
            video_file: 拼接后的视频文件
            audio_file: 配音音频文件
            subtitle_timeline: 字幕时间轴
            output_file: 最终输出路径

        Returns:
            最终视频路径，失败返回 None
        """
        # 1. 先添加音频
        temp_video = os.path.join(self.temp_dir, "temp_with_audio.mp4")
        video_with_audio = self.audio_mixer.add_audio(video_file, audio_file, temp_video)
        if not video_with_audio:
            return None

        # 2. 再添加字幕
        final_video = self.subtitle_renderer.add_subtitles(
            video_with_audio, subtitle_timeline, output_file
        )

        # 3. 清理临时文件
        if os.path.exists(temp_video):
            os.remove(temp_video)

        return final_video
