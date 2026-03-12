"""
TTS 语音生成模块
"""
from .engine import TTSEngine
from .text_splitter import split_text_by_sentences
from .audio_merger import merge_audio_files
from .facade import text_to_audio, text_to_audio_sync
