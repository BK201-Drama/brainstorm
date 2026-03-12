"""
通用视频下载脚本（按类别 / 命令行参数）

特性：并发下载 · 自动静音 · 唯一文件名 · 30分钟以内时长过滤
"""
import os
import sys

# 确保项目根目录在 sys.path 中
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.downloader import VideoDownloader


def download_videos_by_category(video_dict, base_output_dir=None):
    """
    按类别并发下载视频。

    Args:
        video_dict: {"类别名": [url1, url2, ...], ...}
        base_output_dir: 基础输出目录
    """
    if base_output_dir is None:
        base_output_dir = os.path.join(_PROJECT_ROOT, "downloads")

    all_downloaded = {}
    all_failed = {}

    for category, urls in video_dict.items():
        if not urls:
            continue

        print(f"\n{'='*60}")
        print(f"开始下载【{category}】类别的视频 ({len(urls)} 个)")
        print(f"{'='*60}")

        category_dir = os.path.join(base_output_dir, category)
        os.makedirs(category_dir, exist_ok=True)

        downloader = VideoDownloader(output_dir=category_dir)
        downloaded_files = downloader.download_videos_concurrent(urls)

        failed_count = len(urls) - len(downloaded_files)
        all_downloaded[category] = downloaded_files
        all_failed[category] = failed_count

        print(f"\n【{category}】下载完成: 成功 {len(downloaded_files)}, 失败 {failed_count}")

    # 总结
    print(f"\n{'='*60}")
    print("全部下载完成！")
    print(f"{'='*60}")

    total_success = sum(len(f) for f in all_downloaded.values())
    total_failed = sum(all_failed.values())
    print(f"\n总计: 成功 {total_success}, 失败 {total_failed}")

    for category, files in all_downloaded.items():
        if files:
            print(f"\n【{category}】下载的文件:")
            for fp in files:
                size_mb = os.path.getsize(fp) / (1024 * 1024) if os.path.exists(fp) else 0
                print(f"  - {fp}  ({size_mb:.1f} MB)")

    return all_downloaded


def download_videos(urls, output_dir=None):
    """
    并发下载视频（兼容旧版本调用）。
    """
    downloader = VideoDownloader()
    if output_dir:
        downloader.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    print(f"开始下载 {len(urls)} 个视频...")
    print(f"输出目录: {downloader.output_dir}")
    print("=" * 60)

    downloaded_files = downloader.download_videos_concurrent(urls)

    print("\n" + "=" * 60)
    print(f"下载完成！成功: {len(downloaded_files)}, 失败: {len(urls) - len(downloaded_files)}")

    if downloaded_files:
        print("\n下载的文件:")
        for fp in downloaded_files:
            size_mb = os.path.getsize(fp) / (1024 * 1024) if os.path.exists(fp) else 0
            print(f"  - {fp}  ({size_mb:.1f} MB)")

    return downloaded_files


if __name__ == "__main__":
    videos = {
        "解压": [],
        "美食": [],
        "打扫": [],
    }

    if len(sys.argv) > 1:
        download_videos(sys.argv[1:])
    elif any(videos.values()):
        download_videos_by_category(videos)
    else:
        print("=" * 60)
        print("视频下载脚本")
        print("=" * 60)
        print("\n使用方法:")
        print("  方式1: python scripts/download_videos.py <url1> <url2> ...")
        print("  方式2: 编辑脚本的 videos 字典后运行")
        print("\n支持的平台: YouTube · B站 · 其他 yt-dlp 支持的平台")
