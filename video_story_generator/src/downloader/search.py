"""
视频搜索模块
职责：在各平台搜索视频并返回URL
"""
import logging

logger = logging.getLogger(__name__)

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False


def search_bilibili(keyword, count=2):
    """
    使用 yt-dlp 搜索B站视频并返回URL列表。

    Args:
        keyword: 搜索关键词
        count: 返回数量

    Returns:
        视频URL列表
    """
    if not YT_DLP_AVAILABLE:
        logger.warning("yt-dlp未安装，无法搜索")
        return []

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "playlist_items": f"1:{count}",
    }
    search_url = f"bilisearch{count}:{keyword}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(search_url, download=False)
            if result and "entries" in result:
                return [
                    entry["url"]
                    for entry in result["entries"]
                    if entry and entry.get("url")
                ]
    except Exception as e:
        print(f"  搜索失败: {e}")

    return []
