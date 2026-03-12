"""
音频片段合并模块
职责：将多个 TTS 音频片段合并为一个完整音频文件
"""


def merge_audio_files(audio_files, output_file):
    """
    合并多个音频文件为一个。

    Args:
        audio_files: 音频文件路径列表
        output_file: 输出音频文件路径

    Returns:
        合并后的文件路径，失败返回 None
    """
    try:
        from moviepy import concatenate_audioclips, AudioFileClip

        clips = [AudioFileClip(f) for f in audio_files]
        final_audio = concatenate_audioclips(clips)
        final_audio.write_audiofile(output_file, codec='mp3')

        for clip in clips:
            clip.close()
        final_audio.close()

        return output_file

    except Exception as e:
        print(f"合并音频失败: {e}")
        return None
