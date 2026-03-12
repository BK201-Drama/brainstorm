"""
TTS语音生成模块
使用edge-tts生成中文语音
"""
import asyncio
import edge_tts
import os
from pathlib import Path
from config import TTS_CONFIG, OUTPUT_CONFIG


class TTSGenerator:
    def __init__(self):
        self.voice = TTS_CONFIG["voice"]
        self.rate = TTS_CONFIG["rate"]
        self.pitch = TTS_CONFIG["pitch"]
        self.temp_dir = OUTPUT_CONFIG["temp_dir"]
        # 确保临时目录存在
        os.makedirs(self.temp_dir, exist_ok=True)
        
    async def generate_audio(self, text, output_file):
        """
        生成单个音频文件
        
        Args:
            text: 要转换的文本
            output_file: 输出音频文件路径
        
        Returns:
            音频文件路径和时长
        """
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.voice,
                rate=self.rate,
                pitch=self.pitch
            )
            
            await communicate.save(output_file)
            
            # 获取音频时长
            from moviepy import AudioFileClip
            audio = AudioFileClip(output_file)
            duration = audio.duration
            audio.close()
            
            return output_file, duration
            
        except Exception as e:
            print(f"生成音频失败: {e}")
            return None, 0
    
    async def generate_audio_segments(self, text_segments):
        """
        为多个文本片段生成音频（精确测量实际时长，确保字幕同步）
        
        Args:
            text_segments: 文本片段列表，每个元素是 (text, start_time, end_time) 或 text
        
        Returns:
            (音频文件路径列表, 字幕时间轴列表)
            字幕时间轴格式: [{"start": 0, "end": 5, "text": "...", "duration": 5}, ...]
        """
        audio_files = []
        subtitle_timeline = []
        current_time = 0
        
        for i, segment in enumerate(text_segments):
            if isinstance(segment, tuple):
                text = segment[0]
            else:
                text = segment
            
            output_file = os.path.join(self.temp_dir, f"audio_segment_{i:03d}.mp3")
            
            print(f"正在生成音频片段 {i+1}/{len(text_segments)}: {text[:30]}...")
            audio_file, duration = await self.generate_audio(text, output_file)
            
            if audio_file:
                # 实际测量音频时长（更精确）
                try:
                    audio_clip = AudioFileClip(audio_file)
                    actual_duration = audio_clip.duration
                    audio_clip.close()
                    duration = actual_duration  # 使用实际测量的时长
                except:
                    pass  # 如果测量失败，使用返回的duration
                
                audio_files.append(audio_file)
                subtitle_timeline.append({
                    "start": current_time,
                    "end": current_time + duration,
                    "text": text,
                    "duration": duration  # 添加duration字段用于字幕同步
                })
                current_time += duration
        
        return audio_files, subtitle_timeline
    
    def merge_audio_files(self, audio_files, output_file):
        """
        合并多个音频文件
        
        Args:
            audio_files: 音频文件路径列表
            output_file: 输出音频文件路径
        
        Returns:
            合并后的音频文件路径
        """
        try:
            from moviepy import concatenate_audioclips, AudioFileClip
            
            clips = [AudioFileClip(f) for f in audio_files]
            final_audio = concatenate_audioclips(clips)
            final_audio.write_audiofile(output_file, codec='mp3')
            
            # 关闭所有clips
            for clip in clips:
                clip.close()
            final_audio.close()
            
            return output_file
            
        except Exception as e:
            print(f"合并音频失败: {e}")
            return None
    
    def split_text_by_sentences(self, text):
        """
        将文本按句子分割
        
        Args:
            text: 完整文本
        
        Returns:
            句子列表
        """
        import re
        # 按句号、问号、感叹号分割
        sentences = re.split(r'[。！？\n]', text)
        # 过滤空字符串和过短的句子
        sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        return sentences
    
    async def text_to_audio(self, text, output_file):
        """
        将完整文本转换为音频（自动分段）
        
        Args:
            text: 完整文本
            output_file: 输出音频文件路径
        
        Returns:
            (音频文件路径, 字幕时间轴)
        """
        # 分段
        segments = self.split_text_by_sentences(text)
        print(f"文本已分为 {len(segments)} 个片段")
        
        # 生成音频片段
        audio_files, subtitle_timeline = await self.generate_audio_segments(segments)
        
        if not audio_files:
            return None, []
        
        # 合并音频
        print("正在合并音频...")
        merged_audio = self.merge_audio_files(audio_files, output_file)
        
        return merged_audio, subtitle_timeline


# 同步包装函数
def text_to_audio_sync(text, output_file):
    """同步版本的文本转音频"""
    generator = TTSGenerator()
    return asyncio.run(generator.text_to_audio(text, output_file))
