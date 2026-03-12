"""
字幕渲染模块
职责：使用 PIL 渲染中文字幕图片，合成到视频上
"""
import os
from moviepy import VideoFileClip, CompositeVideoClip, ImageClip

from ..config import SUBTITLE_CONFIG, OUTPUT_CONFIG, VIDEO_CONFIG


class SubtitleRenderer:
    """字幕渲染器"""

    def __init__(self):
        self.font_size = SUBTITLE_CONFIG["font_size"]
        self.bg_opacity = SUBTITLE_CONFIG["bg_opacity"]
        self.margin = SUBTITLE_CONFIG["margin"]
        self.fps = VIDEO_CONFIG["fps"]
        self.temp_dir = os.path.join(OUTPUT_CONFIG["temp_dir"], "subtitles")
        os.makedirs(self.temp_dir, exist_ok=True)

    # ── 字体加载 ──────────────────────────────────────────────
    def _load_font(self):
        """加载中文字体，依次尝试宋体/黑体/微软雅黑，最后 fallback 到默认字体"""
        from PIL import ImageFont

        font_paths = [
            "C:/Windows/Fonts/simsun.ttc",   # 宋体
            "C:/Windows/Fonts/simhei.ttf",   # 黑体
            "C:/Windows/Fonts/msyh.ttc",     # 微软雅黑
        ]
        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, self.font_size)
                except Exception:
                    continue
        return ImageFont.load_default()

    # ── 单条字幕图片 ──────────────────────────────────────────
    def _render_subtitle_image(self, text, img_width, index):
        """
        渲染单条字幕为 PNG 图片。

        Args:
            text: 字幕文字
            img_width: 图片宽度
            index: 序号（用于文件名）

        Returns:
            图片文件路径
        """
        from PIL import Image, ImageDraw

        img_height = 100
        font = self._load_font()

        img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 计算文本尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # 换行处理
        if text_width > img_width - 40:
            text, text_width, text_height = self._wrap_text(draw, text, font, img_width - 40)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_height = bbox[3] - bbox[1]

        # 半透明背景
        bg_height = text_height + 20
        bg_y = (img_height - bg_height) // 2
        bg_alpha = int(255 * self.bg_opacity)
        bg_img = Image.new('RGBA', (img_width, bg_height), (0, 0, 0, bg_alpha))
        img.paste(bg_img, (0, bg_y), bg_img)

        # 绘制文字
        text_x = (img_width - text_width) // 2
        text_y = (img_height - text_height) // 2
        draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))

        # 保存
        img_path = os.path.join(self.temp_dir, f"subtitle_{index:03d}.png")
        img.save(img_path)
        return img_path

    @staticmethod
    def _wrap_text(draw, text, font, max_width):
        """将过长文本按字符换行"""
        words = list(text)  # 中文按字符拆分
        lines = []
        current_line = ""
        for char in words:
            test_line = current_line + char
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)

        wrapped = "\n".join(lines)
        bbox = draw.textbbox((0, 0), wrapped, font=font)
        return wrapped, bbox[2] - bbox[0], bbox[3] - bbox[1]

    # ── 为视频添加字幕 ────────────────────────────────────────
    def add_subtitles(self, video_file, subtitle_timeline, output_file):
        """
        为视频叠加字幕。

        Args:
            video_file: 视频文件路径
            subtitle_timeline: [{"start":0, "end":5, "text":"...", "duration":5}, ...]
            output_file: 输出视频路径

        Returns:
            输出文件路径，失败返回 None
        """
        try:
            video = VideoFileClip(video_file)
            subtitle_clips = []
            img_width = int(video.w - self.margin * 2)

            for i, subtitle in enumerate(subtitle_timeline):
                try:
                    text = subtitle["text"]
                    start_time = subtitle["start"]
                    duration = subtitle.get("duration", subtitle["end"] - subtitle["start"])

                    img_path = self._render_subtitle_image(text, img_width, i)

                    clip = ImageClip(img_path)
                    clip = clip.with_duration(duration)
                    clip = clip.with_start(start_time)
                    clip = clip.with_position(('center', video.h - self.margin - self.font_size))
                    subtitle_clips.append(clip)

                except Exception as e:
                    print(f"字幕 {i+1} 创建失败: {e}")
                    continue

            final_video = CompositeVideoClip([video] + subtitle_clips)
            final_video.write_videofile(
                output_file,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
            )

            video.close()
            for clip in subtitle_clips:
                clip.close()
            final_video.close()

            print(f"字幕添加完成: {output_file}")
            return output_file

        except Exception as e:
            print(f"添加字幕失败: {e}")
            import traceback
            traceback.print_exc()
            return None
