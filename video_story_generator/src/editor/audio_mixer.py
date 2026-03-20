"""
音频混合模块
职责：为视频添加/替换配音音轨
"""
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips

from ..config import VIDEO_CONFIG


class AudioMixer:
    """音频混合器"""

    def __init__(self):
        self.fps = VIDEO_CONFIG["fps"]

    @staticmethod
    def _subclip_audio(audio, start, end):
        """兼容不同 moviepy 版本的 subclip"""
        try:
            return audio.subclipped(start, end)
        except AttributeError:
            return audio.subclip(start, end)

    @staticmethod
    def _subclip_video(video, start, end):
        try:
            return video.subclipped(start, end)
        except AttributeError:
            return video.subclip(start, end)

    def add_audio(self, video_file, audio_file, output_file):
        """
        为视频添加配音（保证对齐）。
        - 音频 > 视频：循环/延长视频到音频时长
        - 音频 < 视频：循环音频到视频时长

        Args:
            video_file: 视频文件路径
            audio_file: 音频文件路径
            output_file: 输出视频路径

        Returns:
            输出文件路径，失败返回 None
        """
        try:
            video = VideoFileClip(video_file)
            audio = AudioFileClip(audio_file)

            if audio.duration > video.duration:
                loop_count = int(audio.duration / video.duration) + 1
                video = concatenate_videoclips([video] * loop_count)
                video = self._subclip_video(video, 0, audio.duration)
            elif audio.duration < video.duration:
                from moviepy import concatenate_audioclips
                loop_count = int(video.duration / audio.duration) + 1
                audio = self._subclip_audio(concatenate_audioclips([audio] * loop_count), 0, video.duration)

            print(f"[对齐检查] video={video.duration:.3f}s, audio={audio.duration:.3f}s")

            final_video = video.with_audio(audio)
            final_video.write_videofile(
                output_file,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
            )

            video.close()
            audio.close()
            final_video.close()

            print(f"配音添加完成: {output_file}")
            return output_file

        except Exception as e:
            print(f"添加配音失败: {e}")
            import traceback
            traceback.print_exc()
            return None
