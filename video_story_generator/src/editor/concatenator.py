"""
视频拼接模块
职责：将多个视频拼接为一个，支持循环填充到目标时长
"""
import os
from moviepy import VideoFileClip, concatenate_videoclips

from ..config import VIDEO_CONFIG


class VideoConcatenator:
    """视频拼接器"""

    def __init__(self):
        self.output_resolution = VIDEO_CONFIG["output_resolution"]
        self.fps = VIDEO_CONFIG["fps"]
        self.target_duration = VIDEO_CONFIG["target_duration"]

    # ── 分辨率调整 ────────────────────────────────────────────
    @staticmethod
    def _resize_clip(clip, target_resolution):
        """兼容不同 moviepy 版本的 resize"""
        for method_name in ("resized", "with_size", "resize"):
            method = getattr(clip, method_name, None)
            if method:
                try:
                    return method(target_resolution)
                except (AttributeError, TypeError):
                    continue
        return clip  # 全部失败则保持原样

    # ── 截取 ──────────────────────────────────────────────────
    @staticmethod
    def _subclip(clip, start, end):
        """兼容不同 moviepy 版本的 subclip"""
        try:
            return clip.subclipped(start, end)
        except AttributeError:
            return clip.subclip(start, end)

    # ── 拼接 ──────────────────────────────────────────────────
    def concatenate(self, video_files, output_file, loop_if_needed=True):
        """
        拼接多个视频。

        Args:
            video_files: 视频文件路径列表
            output_file: 输出文件路径
            loop_if_needed: 总时长不足时是否循环填充

        Returns:
            拼接后的视频文件路径，失败返回 None
        """
        try:
            clips = []
            total_duration = 0

            for video_file in video_files:
                clip = VideoFileClip(video_file)
                clip = self._resize_clip(clip, self.output_resolution)
                clips.append(clip)
                total_duration += clip.duration

            # 循环填充
            if total_duration < self.target_duration and loop_if_needed:
                print(f"视频总时长 {total_duration:.1f}秒，不足目标时长 {self.target_duration}秒，将循环播放")
                loop_count = int(self.target_duration / total_duration) + 1
                all_clips = clips * loop_count
                final_clip = concatenate_videoclips(all_clips[:len(clips) * loop_count])
                final_clip = self._subclip(final_clip, 0, min(final_clip.duration, self.target_duration))
            else:
                final_clip = concatenate_videoclips(clips)

            os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
            final_clip.write_videofile(
                output_file,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
            )

            # 释放资源
            for clip in clips:
                clip.close()
            final_clip.close()

            print(f"视频拼接完成: {output_file}")
            return output_file

        except Exception as e:
            print(f"拼接视频失败: {e}")
            return None
