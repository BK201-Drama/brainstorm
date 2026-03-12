"""
依赖检查脚本
职责：快速检查所有必要依赖是否已安装
"""


def check():
    deps = {
        "yt_dlp": "yt-dlp",
        "moviepy": "moviepy",
        "edge_tts": "edge-tts",
        "PIL": "Pillow",
        "imageio_ffmpeg": "imageio-ffmpeg",
    }
    for module, package in deps.items():
        try:
            __import__(module)
            print(f"  [OK] {package}")
        except ImportError:
            print(f"  [X] {package}  (未安装，请运行: pip install {package})")


if __name__ == "__main__":
    print("依赖检查:")
    check()
