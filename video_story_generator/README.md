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

## 使用方法

**注意：** 从项目根目录运行 `main.py`，它会自动导入 `src` 目录中的模块。

### 方式1: 使用视频URL（从网络下载）

```bash
python main.py --urls https://www.youtube.com/watch?v=xxx https://www.bilibili.com/video/xxx
```

### 方式2: 使用本地视频文件

```bash
python main.py --local-videos downloads/video1.mp4 downloads/video2.mp4 downloads/video3.mp4
```

### 方式3: 指定故事主题

```bash
python main.py --local-videos downloads/video1.mp4 downloads/video2.mp4 --story-topic "中年人的情感故事"
```

### 方式4: 使用自定义故事文本

```bash
python main.py --local-videos downloads/video1.mp4 --story-text "你的故事文本..."
```

### 指定输出文件

```bash
python main.py --local-videos downloads/video1.mp4 --output output/my_video.mp4
```

## 配置

编辑 `config.py` 可以修改：
- 视频分辨率、帧率
- TTS语音选择（男声/女声）
- 字幕样式（字体大小、颜色、位置）
- 目标视频时长

## 输出文件

- `output/final_video.mp4`: 最终生成的视频
- `output/story.txt`: 生成的故事文本
- `temp/`: 临时文件目录

## 注意事项

1. **视频下载**：需要网络连接，某些平台可能需要VPN
2. **TTS语音**：edge-tts需要网络连接，首次使用会下载语音模型
3. **处理时间**：根据视频数量和长度，处理时间可能需要几分钟到几十分钟
4. **存储空间**：确保有足够的磁盘空间（建议至少5GB）

## 常见问题

### Q: 视频下载失败？
A: 检查网络连接，某些平台可能需要VPN。也可以使用本地视频文件。

### Q: TTS生成失败？
A: 确保网络连接正常，edge-tts需要在线下载语音模型。

### Q: 字幕显示不正常？
A: 程序会自动加载Windows系统中文字体（宋体/黑体/微软雅黑）。如果仍有问题，检查系统字体安装情况。

### Q: 音频和字幕不同步？
A: 程序已自动修复同步问题，通过实际测量每段音频时长来精确计算字幕时间轴，确保完美同步。

### Q: 视频处理很慢？
A: 视频处理是CPU密集型任务，大视频文件需要较长时间。可以先用小视频测试。

## 项目结构

```
video_story_generator/
├── main.py              # 入口脚本（从根目录运行）
├── src/                 # 源代码目录
│   ├── __init__.py
│   ├── main.py          # 主程序逻辑
│   ├── config.py        # 配置文件
│   ├── video_downloader.py
│   ├── video_editor.py
│   ├── story_generator.py
│   └── tts_generator.py
├── downloads/           # 视频素材目录
├── output/              # 输出目录
├── temp/                # 临时文件目录
├── requirements.txt     # Python依赖
└── README.md           # 本文件
```

## 示例

```bash
# 使用本地视频生成故事视频
python main.py --local-videos downloads/video1.mp4 downloads/video2.mp4 --story-topic "普通人的真实故事"

# 从YouTube下载视频并生成
python main.py --urls https://www.youtube.com/watch?v=dQw4w9WgXcQ --story-topic "励志故事"
```

## 技术栈

- **MoviePy**: 视频处理
- **edge-tts**: 文字转语音
- **yt-dlp**: 视频下载
- **FFmpeg**: 视频编码

## 许可证

MIT License
