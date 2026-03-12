"""
B站分类视频自动下载脚本
类别：satisfying(解压)、food(美食)、cleaning(打扫)

特性：并发下载 · 自动静音 · 唯一文件名 · 30分钟以内时长过滤
"""
import os
import sys

# 确保项目根目录在 sys.path 中
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.downloader import VideoDownloader, search_bilibili
from src.config import DOWNLOAD_CONFIG

DOWNLOAD_DIR = os.path.join(_PROJECT_ROOT, "downloads")

# ── 分类配置 ──────────────────────────────────────────────────
CATEGORIES = {
    "satisfying": {
        "keyword": "解压视频",
        "fallback_urls": [
            "https://www.bilibili.com/video/BV1xMWLeYE1e",
            "https://www.bilibili.com/video/BV1CP411n7f2",
        ],
    },
    "food": {
        "keyword": "美食制作",
        "fallback_urls": [
            "https://www.bilibili.com/video/BV1sM411e7Lj",
            "https://www.bilibili.com/video/BV1fj411o7dE",
        ],
    },
    "cleaning": {
        "keyword": "打扫卫生 解压",
        "fallback_urls": [
            "https://www.bilibili.com/video/BV1Bm4y1J7uK",
            "https://www.bilibili.com/video/BV1sm4y1D7XE",
        ],
    },
}

CAT_LABELS = {"satisfying": "解压", "food": "美食", "cleaning": "打扫"}


def main():
    print("=" * 60)
    print("Bilibili 视频下载器（并发 + 静音处理）")
    print("=" * 60)

    # 搜索并收集 URL
    all_tasks = {}
    for cat_name, cat_info in CATEGORIES.items():
        label = CAT_LABELS.get(cat_name, cat_name)
        cat_dir = os.path.join(DOWNLOAD_DIR, cat_name)
        os.makedirs(cat_dir, exist_ok=True)

        print(f"\n搜索 [{label}]: {cat_info['keyword']} ...")
        urls = search_bilibili(cat_info["keyword"], count=2)
        if urls:
            print(f"  找到 {len(urls)} 个视频")
            for u in urls:
                print(f"    - {u}")
        else:
            urls = cat_info["fallback_urls"]
            print(f"  未搜到结果，使用备用 URL ({len(urls)} 个)")

        all_tasks[cat_name] = (cat_dir, urls)

    # 按类别并发下载
    results = {}
    for cat_name, (cat_dir, urls) in all_tasks.items():
        label = CAT_LABELS.get(cat_name, cat_name)
        print(f"\n{'─' * 40}")
        print(f"[{label}] 开始下载 {len(urls)} 个视频 → {cat_dir}")
        print(f"{'─' * 40}")

        downloader = VideoDownloader(output_dir=cat_dir)
        downloaded = downloader.download_videos_concurrent(urls)
        results[cat_name] = downloaded

    # 汇总
    print("\n" + "=" * 60)
    print("下载汇总:")
    total_ok = 0
    for cat_name, files in results.items():
        label = CAT_LABELS.get(cat_name, cat_name)
        total_urls = len(all_tasks[cat_name][1])
        print(f"  {label}: {len(files)}/{total_urls}")
        total_ok += len(files)
    print(f"  合计: {total_ok} 个视频下载成功")
    print("=" * 60)

    # 列出已下载文件
    print("\n已下载文件:")
    for cat_name, files in results.items():
        label = CAT_LABELS.get(cat_name, cat_name)
        for fp in sorted(files):
            size_mb = os.path.getsize(fp) / (1024 * 1024)
            print(f"  [{label}] {os.path.basename(fp)}  ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
