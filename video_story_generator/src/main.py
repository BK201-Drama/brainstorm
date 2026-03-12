"""
主程序
整合所有功能：视频下载、拼接、故事生成、配音、字幕
"""
import os
import sys
import argparse
from pathlib import Path

# 添加src目录到路径，确保可以导入模块
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from video_downloader import VideoDownloader
from video_editor import VideoEditor
from story_generator import StoryGenerator
from tts_generator import TTSGenerator, text_to_audio_sync
from config import OUTPUT_CONFIG, VIDEO_CONFIG


def main():
    parser = argparse.ArgumentParser(description='视频故事生成器')
    parser.add_argument('--urls', nargs='+', help='视频URL列表（可选）')
    parser.add_argument('--local-videos', nargs='+', help='本地视频文件路径列表（可选）')
    parser.add_argument('--story-topic', type=str, help='故事主题（可选）')
    parser.add_argument('--story-text', type=str, help='直接提供故事文本（可选）')
    parser.add_argument('--output', type=str, default='output/final_video.mp4', help='输出视频文件路径')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("视频故事生成器")
    print("=" * 60)
    
    # 步骤1: 下载/获取视频
    print("\n[步骤1] 获取视频素材...")
    downloader = VideoDownloader()
    
    video_files = []
    if args.local_videos:
        video_files = downloader.download_from_local(args.local_videos)
    elif args.urls:
        video_files = downloader.download_multiple_videos(
            args.urls, 
            target_duration=VIDEO_CONFIG["target_duration"]
        )
    else:
        print("错误: 请提供视频URL或本地视频文件路径")
        print("使用方法:")
        print("  python main.py --urls <url1> <url2> ...")
        print("  或")
        print("  python main.py --local-videos <file1> <file2> ...")
        return
    
    if not video_files:
        print("错误: 没有获取到视频文件")
        return
    
    print(f"✓ 已获取 {len(video_files)} 个视频文件")
    
    # 步骤2: 拼接视频
    print("\n[步骤2] 拼接视频...")
    editor = VideoEditor()
    temp_video = os.path.join(OUTPUT_CONFIG["temp_dir"], "concatenated_video.mp4")
    concatenated_video = editor.concatenate_videos(video_files, temp_video)
    
    if not concatenated_video:
        print("错误: 视频拼接失败")
        return
    
    print("✓ 视频拼接完成")
    
    # 步骤3: 生成故事
    print("\n[步骤3] 生成故事...")
    story_gen = StoryGenerator()
    
    if args.story_text:
        story_text = args.story_text
    else:
        story_text = story_gen.generate_story(topic=args.story_topic)
    
    print(f"✓ 故事生成完成（{len(story_text)} 字）")
    print(f"\n故事预览:\n{story_text[:200]}...\n")
    
    # 保存故事文本
    story_file = os.path.join(OUTPUT_CONFIG["output_dir"], "story.txt")
    with open(story_file, 'w', encoding='utf-8') as f:
        f.write(story_text)
    print(f"故事已保存到: {story_file}")
    
    # 步骤4: 生成配音和字幕
    print("\n[步骤4] 生成配音和字幕...")
    tts_gen = TTSGenerator()
    
    audio_file = os.path.join(OUTPUT_CONFIG["temp_dir"], "story_audio.mp3")
    audio_path, subtitle_timeline = text_to_audio_sync(story_text, audio_file)
    
    if not audio_path:
        print("错误: 配音生成失败")
        return
    
    print(f"✓ 配音生成完成")
    print(f"✓ 字幕时间轴生成完成（共 {len(subtitle_timeline)} 条字幕）")
    
    # 步骤5: 合成最终视频
    print("\n[步骤5] 合成最终视频（视频+配音+字幕）...")
    final_video = editor.create_final_video(
        concatenated_video,
        audio_path,
        subtitle_timeline,
        args.output
    )
    
    if not final_video:
        print("错误: 最终视频合成失败")
        return
    
    print("\n" + "=" * 60)
    print("✓ 完成！")
    print("=" * 60)
    print(f"最终视频: {final_video}")
    print(f"故事文本: {story_file}")
    print("\n你可以使用以下命令查看视频:")
    print(f"  (Windows) start {final_video}")
    print(f"  (Mac/Linux) open {final_video}")


if __name__ == "__main__":
    main()
