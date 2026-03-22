"""
音频混合模块
职责：为视频添加/替换配音音轨
"""
import os
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips

from ..config import VIDEO_CONFIG, AUDIO_CONFIG


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

    @staticmethod
    def _mix_with_bgm(voice_audio, target_duration):
        """给主配音叠加背景音乐（可写死配置）"""
        if not AUDIO_CONFIG.get("bgm_enabled", True):
            return voice_audio

        bgm_file = AUDIO_CONFIG.get("bgm_file")
        if not bgm_file or not os.path.exists(bgm_file):
            return voice_audio

        try:
            bgm = AudioFileClip(bgm_file)
            if bgm.duration < target_duration:
                from moviepy import concatenate_audioclips
                loop_count = int(target_duration / bgm.duration) + 1
                bgm = concatenate_audioclips([bgm] * loop_count)

            bgm = AudioMixer._subclip_audio(bgm, 0, target_duration)
            bgm = bgm.with_volume_scaled(float(AUDIO_CONFIG.get("bgm_volume", 0.12)))

            from moviepy import CompositeAudioClip
            return CompositeAudioClip([bgm, voice_audio])
        except Exception as e:
            print(f"背景音乐混音失败，降级为纯配音: {e}")
            return voice_audio

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

            mixed_audio = self._mix_with_bgm(audio, video.duration)
            final_video = video.with_audio(mixed_audio)
            final_video.write_videofile(
                output_file,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
            )

            video.close()
            audio.close()
            try:
                mixed_audio.close()
            except Exception:
                pass
            final_video.close()

            print(f"配音添加完成: {output_file}")
            return output_file

        except Exception as e:
            print(f"添加配音失败: {e}")
            import traceback
            traceback.print_exc()
            return None
