"""
主流程编排（Pipeline）
职责：组织 下载→拼接→故事→配音→合成 五步流水线
支持：单章与多章节并发生成
"""
import os
import re
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from .config import OUTPUT_CONFIG, VIDEO_CONFIG
from .downloader import VideoDownloader
from .editor import VideoCompositor
from .story import StoryGenerator, save_chapter_text, load_story_text
from .tts import text_to_audio_sync


def _ensure_dirs():
    """确保必要的输出 / 临时目录存在"""
    os.makedirs(OUTPUT_CONFIG["output_dir"], exist_ok=True)
    os.makedirs(OUTPUT_CONFIG["temp_dir"], exist_ok=True)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(os.path.join(project_root, "stories"), exist_ok=True)


def _normalize_chapter(chapter: str) -> str:
    s = str(chapter).strip().lower().replace("chapter-", "")
    if not s.isdigit():
        raise ValueError(f"非法章节编号: {chapter}")
    return f"{int(s):03d}"


def _parse_chapters(chapter: str, chapters: str | None) -> list[str]:
    """支持单章和范围，如 001 或 001-010"""
    if not chapters:
        return [_normalize_chapter(chapter)]

    m = re.match(r"^\s*(\d+)\s*-\s*(\d+)\s*$", chapters)
    if not m:
        return [_normalize_chapter(chapters)]

    start, end = int(m.group(1)), int(m.group(2))
    if end < start:
        raise ValueError("--chapters 范围非法：end < start")
    return [f"{i:03d}" for i in range(start, end + 1)]


def _render_one_chapter(concatenated_video: str, novel_name: str, chapter: str, project_root: str, output_dir: str):
    """渲染单章视频（可并发）"""
    # 读取章节文本
    story_text, story_file = load_story_text(
        story_file=None,
        project_root=project_root,
        novel_name=novel_name,
        chapter=chapter,
    )

    # 每章独立临时文件，避免并发冲突
    temp_dir = OUTPUT_CONFIG["temp_dir"]
    audio_file = os.path.join(temp_dir, f"story_audio_ch{chapter}.mp3")

    audio_path, subtitle_timeline = text_to_audio_sync(story_text, audio_file)
    if not audio_path:
        raise RuntimeError(f"章节 {chapter} 配音失败")

    chapter_out = os.path.join(output_dir, f"chapter-{chapter}.mp4")
    compositor = VideoCompositor()
    final_video = compositor.create_final_video(
        concatenated_video,
        audio_path,
        subtitle_timeline,
        chapter_out,
    )
    if not final_video:
        raise RuntimeError(f"章节 {chapter} 合成失败")

    return {
        "chapter": chapter,
        "story_file": story_file,
        "output": final_video,
        "chars": len(story_text),
        "subtitle_count": len(subtitle_timeline),
    }


def main():
    parser = argparse.ArgumentParser(description='视频故事生成器')
    parser.add_argument('--urls', nargs='+', help='视频URL列表')
    parser.add_argument('--local-videos', nargs='+', help='本地视频文件路径列表')
    parser.add_argument('--story-topic', type=str, help='故事主题（会生成章节文本）')
    parser.add_argument('--story-text', type=str, help='直接提供故事文本（会生成章节文本）')
    parser.add_argument('--story-file', type=str, help='直接读取故事txt文件，例如 stories/xxx/chapter-001.txt')
    parser.add_argument('--novel-name', type=str, help='小说名（用于章节存储和读取）')
    parser.add_argument('--chapter', type=str, default='001', help='章节编号，如 001 / 1 / chapter-001')
    parser.add_argument('--chapters', type=str, help='批量章节，如 001-010（与 --novel-name 搭配）')
    parser.add_argument('--workers', type=int, default=2, help='批量章节并发数（默认2）')
    parser.add_argument('--output', type=str, default='output/final_video.mp4', help='输出视频文件路径')
    parser.add_argument('--clip-start', type=float, default=0.0, help='素材剪辑起始秒数（用于YouTube/B站解压视频）')
    parser.add_argument('--clip-duration', type=float, default=None, help='素材剪辑时长（秒）')

    args = parser.parse_args()

    _ensure_dirs()

    print("=" * 60)
    print("视频故事生成器")
    print("=" * 60)

    # ── 步骤1: 获取视频素材 ───────────────────────────────────
    print("\n[步骤1] 获取视频素材...")
    downloader = VideoDownloader(
        clip_start=args.clip_start,
        clip_duration=args.clip_duration,
    )

    video_files = []
    if args.local_videos:
        video_files = downloader.load_local_videos(args.local_videos)
    elif args.urls:
        video_files = downloader.download_multiple_videos(
            args.urls,
            target_duration=VIDEO_CONFIG["target_duration"],
        )
    else:
        print("错误: 请提供视频URL或本地视频文件路径")
        print("  python main.py --urls <url1> <url2> ...")
        print("  python main.py --local-videos <file1> <file2> ...")
        return

    if not video_files:
        print("错误: 没有获取到视频文件")
        return

    print(f"[OK] 已获取 {len(video_files)} 个视频文件")

    # ── 步骤2: 拼接视频（只做一次）────────────────────────────
    print("\n[步骤2] 拼接视频...")
    compositor = VideoCompositor()
    temp_video = os.path.join(OUTPUT_CONFIG["temp_dir"], "concatenated_video.mp4")
    concatenated_video = compositor.concatenate_videos(video_files, temp_video)

    if not concatenated_video:
        print("错误: 视频拼接失败")
        return
    print("[OK] 视频拼接完成")

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 单文件模式优先
    if args.story_file:
        print("\n[步骤3] 单文件故事模式...")
        story_text, story_file = load_story_text(
            story_file=args.story_file,
            project_root=project_root,
            novel_name=None,
            chapter=None,
        )
        print(f"[OK] 已从文本读取故事（{len(story_text)} 字）")
        print(f"故事来源: {story_file}")

        print("\n[步骤4] 生成配音和字幕...")
        audio_file = os.path.join(OUTPUT_CONFIG["temp_dir"], "story_audio.mp3")
        audio_path, subtitle_timeline = text_to_audio_sync(story_text, audio_file)
        if not audio_path:
            print("错误: 配音生成失败")
            return

        print("\n[步骤5] 合成最终视频（视频+配音+字幕）...")
        final_video = compositor.create_final_video(
            concatenated_video,
            audio_path,
            subtitle_timeline,
            args.output,
        )
        if not final_video:
            print("错误: 最终视频合成失败")
            return

        print("\n" + "=" * 60)
        print("[OK] 完成！")
        print("=" * 60)
        print(f"最终视频: {final_video}")
        print(f"故事文本: {story_file}")
        return

    # 小说章节模式（单章或批量）
    if not args.novel_name:
        # 向后兼容：未给 novel_name 时，继续旧行为
        print("\n[步骤3] 兼容模式：生成单段故事...")
        story_gen = StoryGenerator()
        story_text = args.story_text or story_gen.generate_story(topic=args.story_topic)
        story_file = save_chapter_text(project_root, (args.story_topic or "默认小说"), args.chapter, story_text)

        audio_file = os.path.join(OUTPUT_CONFIG["temp_dir"], "story_audio.mp3")
        audio_path, subtitle_timeline = text_to_audio_sync(story_text, audio_file)
        final_video = compositor.create_final_video(
            concatenated_video,
            audio_path,
            subtitle_timeline,
            args.output,
        )
        print(f"最终视频: {final_video}")
        print(f"故事文本: {story_file}")
        return

    chapter_list = _parse_chapters(args.chapter, args.chapters)

    # 如果传了文本/主题且只渲染单章，则先落 txt
    if len(chapter_list) == 1 and (args.story_text or args.story_topic):
        story_gen = StoryGenerator()
        story_text = args.story_text or story_gen.generate_story(topic=args.story_topic)
        saved = save_chapter_text(project_root, args.novel_name, chapter_list[0], story_text)
        print(f"[OK] 已生成章节文本: {saved}")

    novel_output_dir = os.path.join(OUTPUT_CONFIG["output_dir"], args.novel_name)
    os.makedirs(novel_output_dir, exist_ok=True)

    print(f"\n[步骤3-5] 章节渲染模式：共 {len(chapter_list)} 章，并发={max(1, args.workers)}")

    if len(chapter_list) == 1:
        info = _render_one_chapter(concatenated_video, args.novel_name, chapter_list[0], project_root, novel_output_dir)
        print("\n" + "=" * 60)
        print("[OK] 完成！")
        print("=" * 60)
        print(f"最终视频: {info['output']}")
        print(f"故事文本: {info['story_file']}")
        return

    # 批量并发
    results = []
    errors = []
    workers = min(max(1, args.workers), len(chapter_list))
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {
            ex.submit(_render_one_chapter, concatenated_video, args.novel_name, ch, project_root, novel_output_dir): ch
            for ch in chapter_list
        }
        for fut in as_completed(futs):
            ch = futs[fut]
            try:
                info = fut.result()
                results.append(info)
                print(f"[OK] 章节 {ch} 完成 -> {info['output']}")
            except Exception as e:
                errors.append((ch, str(e)))
                print(f"[X] 章节 {ch} 失败: {e}")

    results.sort(key=lambda x: x['chapter'])

    print("\n" + "=" * 60)
    print("批量渲染完成")
    print("=" * 60)
    print(f"成功: {len(results)} / {len(chapter_list)}")
    if results:
        print("输出文件:")
        for r in results:
            print(f"  - {r['output']}")
    if errors:
        print("失败章节:")
        for ch, err in errors:
            print(f"  - chapter-{ch}: {err}")
