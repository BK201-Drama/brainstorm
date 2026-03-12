"""
TTS 门面（Facade）
职责：编排 分句→逐段合成→合并 的完整流程，对外提供简洁接口
"""
import asyncio
import os

from ..config import OUTPUT_CONFIG
from .engine import TTSEngine
from .text_splitter import split_text_by_sentences
from .audio_merger import merge_audio_files


async def text_to_audio(text, output_file):
    """
    将完整文本转换为音频（自动分段 → 逐段TTS → 合并 → 返回字幕时间轴）。

    Args:
        text: 完整文本
        output_file: 输出音频文件路径

    Returns:
        (audio_file_path, subtitle_timeline)
        subtitle_timeline: [{"start":0, "end":3.5, "text":"...", "duration":3.5}, ...]
    """
    temp_dir = OUTPUT_CONFIG["temp_dir"]
    os.makedirs(temp_dir, exist_ok=True)

    # 1. 分句
    segments = split_text_by_sentences(text)
    print(f"文本已分为 {len(segments)} 个片段")

    # 2. 逐段合成
    engine = TTSEngine()
    audio_files = []
    subtitle_timeline = []
    current_time = 0

    for i, segment_text in enumerate(segments):
        segment_file = os.path.join(temp_dir, f"audio_segment_{i:03d}.mp3")
        print(f"正在生成音频片段 {i+1}/{len(segments)}: {segment_text[:30]}...")

        audio_path, duration = await engine.synthesize(segment_text, segment_file)

        if audio_path:
            # 二次测量以确保精度
            actual_duration = engine._measure_duration(audio_path)
            if actual_duration > 0:
                duration = actual_duration

            audio_files.append(audio_path)
            subtitle_timeline.append({
                "start": current_time,
                "end": current_time + duration,
                "text": segment_text,
                "duration": duration,
            })
            current_time += duration

    if not audio_files:
        return None, []

    # 3. 合并
    print("正在合并音频...")
    merged_audio = merge_audio_files(audio_files, output_file)

    return merged_audio, subtitle_timeline


def text_to_audio_sync(text, output_file):
    """同步版本的文本转音频（供非 async 代码调用）"""
    return asyncio.run(text_to_audio(text, output_file))
