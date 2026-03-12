# 视频故事生成器

自动化生成带配音和字幕的视频故事。

## 功能

1. **视频下载/获取**：从YouTube、B站等平台下载视频，或使用本地视频
2. **视频拼接**：将多个视频拼接成总时长约10分钟的视频
3. **故事生成**：自动生成故事文本
4. **配音生成**：使用edge-tts将故事文本转换为中文语音
5. **字幕添加**：使用PIL渲染中文字幕，确保正确显示，并与配音精确同步

## 安装

1. 安装Python依赖：
```bash
pip install -r requirements.txt
```

2. 安装FFmpeg（视频处理必需）：
   - Windows: 下载 https://ffmpeg.org/download.html 并添加到PATH
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

3. 检查依赖：
```bash
python scripts/check_deps.py
```

## 使用方法

**注意：** 所有命令均从项目根目录运行。

### 方式1: 使用视频URL（从网络下载）

```bash
python main.py --urls https://www.youtube.com/watch?v=xxx https://www.bilibili.com/video/xxx
```

### 方式2: 使用本地视频文件

```bash
python main.py --local-videos downloads/video1.mp4 downloads/video2.mp4
```

### 方式3: 指定故事主题

```bash
python main.py --local-videos downloads/video1.mp4 --story-topic "中年人的情感故事"
```

### 方式4: 使用自定义故事文本

```bash
python main.py --local-videos downloads/video1.mp4 --story-text "你的故事文本..."
```

### 方式5: B站分类自动下载

```bash
python scripts/auto_download.py
```

### 方式6: 通用视频下载

```bash
python scripts/download_videos.py <url1> <url2> ...
```

## 配置

编辑 `src/config.py` 可以修改：
- 视频分辨率、帧率
- TTS语音选择（男声/女声）
- 字幕样式（字体大小、颜色、位置）
- 目标视频时长
- 下载并发数、时长限制、自动静音

## 输出文件

- `output/final_video.mp4`: 最终生成的视频
- `output/story.txt`: 生成的故事文本
- `temp/`: 临时文件目录

## 项目结构

```
video_story_generator/
├── main.py                          # 唯一入口
├── scripts/                         # 独立 CLI 脚本
│   ├── auto_download.py             #   B站分类下载
│   ├── download_videos.py           #   通用视频下载
│   └── check_deps.py               #   依赖检查
├── src/                             # 核心包
│   ├── __init__.py
│   ├── config.py                    # 配置常量（纯定义，无副作用）
│   ├── pipeline.py                  # 主流程编排
│   ├── utils/                       # 通用工具
│   │   ├── ffmpeg.py                #   ffmpeg 路径、静音处理、时长探测
│   │   └── file_naming.py           #   唯一文件名、文件查找
│   ├── downloader/                  # 视频下载
│   │   ├── core.py                  #   核心下载逻辑（单个/并发/时长筛选）
│   │   └── search.py                #   平台搜索（B站等）
│   ├── editor/                      # 视频编辑
│   │   ├── concatenator.py          #   视频拼接
│   │   ├── subtitle_renderer.py     #   字幕渲染（PIL）
│   │   ├── audio_mixer.py           #   音频混合
│   │   └── compositor.py            #   最终合成编排
│   ├── story/                       # 故事生成
│   │   └── generator.py             #   故事文本生成
│   └── tts/                         # TTS 语音
│       ├── engine.py                #   edge-tts 引擎
│       ├── text_splitter.py         #   文本分句
│       ├── audio_merger.py          #   音频片段合并
│       └── facade.py                #   TTS 门面（完整流程）
├── downloads/                       # 视频素材目录
├── output/                          # 输出目录
├── temp/                            # 临时文件目录
├── requirements.txt
└── README.md
```

### 模块职责（单一职责原则）

| 模块 | 职责 |
|------|------|
| `config.py` | 纯配置常量定义 |
| `pipeline.py` | 主流程五步编排 |
| `utils/ffmpeg.py` | ffmpeg 路径获取、静音处理、时长探测 |
| `utils/file_naming.py` | 唯一文件名生成、下载文件查找 |
| `downloader/core.py` | 单视频下载、并发下载、时长筛选 |
| `downloader/search.py` | B站等平台视频搜索 |
| `editor/concatenator.py` | 多视频拼接（含循环填充） |
| `editor/subtitle_renderer.py` | PIL 字幕图片渲染 + 叠加 |
| `editor/audio_mixer.py` | 音频轨道混合/替换 |
| `editor/compositor.py` | 合成编排（音频→字幕→输出） |
| `story/generator.py` | 故事文本生成 |
| `tts/engine.py` | edge-tts 单段语音合成 |
| `tts/text_splitter.py` | 文本按标点分句 |
| `tts/audio_merger.py` | 多音频片段合并 |
| `tts/facade.py` | TTS 完整流程门面 |

## 技术栈

- **MoviePy**: 视频处理
- **edge-tts**: 文字转语音
- **yt-dlp**: 视频下载
- **FFmpeg**: 视频编码
- **Pillow**: 字幕渲染

## 许可证

MIT License
