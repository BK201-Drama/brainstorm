"""
TTS 引擎
职责：调用 edge-tts 将单段文字转换为音频文件
"""
import os
import edge_tts

from ..config import TTS_CONFIG


class TTSEngine:
    """edge-tts 语音合成引擎"""

    def __init__(self):
        self.voice = TTS_CONFIG["voice"]
        self.rate = TTS_CONFIG["rate"]
        self.pitch = TTS_CONFIG["pitch"]

    async def synthesize(self, text, output_file):
        """
        将文字转换为音频文件。

        Args:
            text: 要合成的文本
            output_file: 输出音频文件路径

        Returns:
            (output_file, duration_seconds)，失败返回 (None, 0)
        """
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.voice,
                rate=self.rate,
                pitch=self.pitch,
            )
            await communicate.save(output_file)

            # 测量实际音频时长
            duration = self._measure_duration(output_file)
            return output_file, duration

        except Exception as e:
            print(f"生成音频失败: {e}")
            return None, 0

    @staticmethod
    def _measure_duration(audio_path):
        """用 moviepy 测量音频时长"""
        try:
            from moviepy import AudioFileClip
            clip = AudioFileClip(audio_path)
            duration = clip.duration
            clip.close()
            return duration
        except Exception:
            return 0
