"""
视频编辑模块
视频拼接、添加字幕、添加配音
"""
import os
from moviepy import VideoFileClip, AudioFileClip, ColorClip, TextClip, CompositeVideoClip, concatenate_videoclips
from config import VIDEO_CONFIG, SUBTITLE_CONFIG, OUTPUT_CONFIG


class VideoEditor:
    def __init__(self):
        self.output_resolution = VIDEO_CONFIG["output_resolution"]
        self.fps = VIDEO_CONFIG["fps"]
        self.output_dir = OUTPUT_CONFIG["output_dir"]
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
    def concatenate_videos(self, video_files, output_file, loop_if_needed=True):
        """
        拼接多个视频
        
        Args:
            video_files: 视频文件路径列表
            loop_if_needed: 如果总时长不足，是否循环播放
        
        Returns:
            拼接后的视频文件路径
        """
        try:
            clips = []
            total_duration = 0
            target_duration = VIDEO_CONFIG["target_duration"]
            
            for video_file in video_files:
                clip = VideoFileClip(video_file)
                # 调整分辨率（moviepy 2.x使用resized）
                try:
                    clip = clip.resized(self.output_resolution)
                except AttributeError:
                    # 如果resized不存在，尝试其他方法
                    try:
                        clip = clip.with_size(self.output_resolution)
                    except AttributeError:
                        try:
                            clip = clip.resize(self.output_resolution)
                        except AttributeError:
                            # 如果都不存在，保持原样
                            pass
                clips.append(clip)
                total_duration += clip.duration
            
            # 如果总时长不足且需要循环
            if total_duration < target_duration and loop_if_needed:
                print(f"视频总时长 {total_duration:.1f}秒，不足目标时长 {target_duration}秒，将循环播放")
                # 计算需要循环多少次
                loop_count = int(target_duration / total_duration) + 1
                all_clips = clips * loop_count
                # 只取需要的时长
                final_clip = concatenate_videoclips(all_clips[:len(clips) * loop_count])
                # 截取到目标时长（moviepy 2.x使用subclipped）
                try:
                    final_clip = final_clip.subclipped(0, min(final_clip.duration, target_duration))
                except AttributeError:
                    final_clip = final_clip.subclip(0, min(final_clip.duration, target_duration))
            else:
                final_clip = concatenate_videoclips(clips)
            
            # 写入文件
            final_clip.write_videofile(
                output_file,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac'
            )
            
            # 关闭所有clips
            for clip in clips:
                clip.close()
            final_clip.close()
            
            print(f"视频拼接完成: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"拼接视频失败: {e}")
            return None
    
    def add_subtitles(self, video_file, subtitle_timeline, output_file):
        """
        为视频添加字幕（使用PIL渲染中文字幕，确保正确显示）
        
        Args:
            video_file: 视频文件路径
            subtitle_timeline: 字幕时间轴，格式: [{"start": 0, "end": 5, "text": "字幕内容", "duration": 5}, ...]
            output_file: 输出视频文件路径
        
        Returns:
            添加字幕后的视频文件路径
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            import os
            
            video = VideoFileClip(video_file)
            
            # 创建字幕clips
            subtitle_clips = []
            os.makedirs(os.path.join(OUTPUT_CONFIG["temp_dir"], "subtitles"), exist_ok=True)
            
            # 加载中文字体
            font_paths = [
                "C:/Windows/Fonts/simsun.ttc",  # 宋体
                "C:/Windows/Fonts/simhei.ttf",  # 黑体
                "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
            ]
            
            font = None
            for path in font_paths:
                if os.path.exists(path):
                    try:
                        font = ImageFont.truetype(path, SUBTITLE_CONFIG["font_size"])
                        break
                    except:
                        continue
            
            if font is None:
                font = ImageFont.load_default()
            
            for i, subtitle in enumerate(subtitle_timeline):
                try:
                    text = subtitle["text"]
                    start_time = subtitle["start"]
                    # 使用duration字段（如果存在），否则计算
                    duration = subtitle.get("duration", subtitle["end"] - subtitle["start"])
                    
                    # 创建字幕图片
                    img_width = int(video.w - SUBTITLE_CONFIG["margin"] * 2)
                    img_height = 100
                    
                    img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(img)
                    
                    # 计算文本位置
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    # 文本换行处理
                    if text_width > img_width - 40:
                        words = text.split()
                        lines = []
                        current_line = ""
                        for word in words:
                            test_line = current_line + word + " " if current_line else word + " "
                            bbox = draw.textbbox((0, 0), test_line, font=font)
                            if bbox[2] - bbox[0] <= img_width - 40:
                                current_line = test_line
                            else:
                                if current_line:
                                    lines.append(current_line.strip())
                                current_line = word + " "
                        if current_line:
                            lines.append(current_line.strip())
                        text = "\n".join(lines)
                        bbox = draw.textbbox((0, 0), text, font=font)
                        text_height = bbox[3] - bbox[1]
                    
                    # 绘制半透明背景
                    bg_height = text_height + 20
                    bg_y = (img_height - bg_height) // 2
                    bg_alpha = int(255 * SUBTITLE_CONFIG["bg_opacity"])
                    bg_img = Image.new('RGBA', (img_width, bg_height), (0, 0, 0, bg_alpha))
                    img.paste(bg_img, (0, bg_y), bg_img)
                    
                    # 绘制文本
                    text_x = (img_width - text_width) // 2
                    text_y = (img_height - text_height) // 2
                    draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 255))
                    
                    # 保存图片
                    subtitle_img_path = os.path.join(OUTPUT_CONFIG["temp_dir"], "subtitles", f"subtitle_{i:03d}.png")
                    img.save(subtitle_img_path)
                    
                    # 创建ImageClip
                    subtitle_clip = ImageClip(subtitle_img_path)
                    subtitle_clip = subtitle_clip.with_duration(duration)
                    subtitle_clip = subtitle_clip.with_start(start_time)
                    subtitle_clip = subtitle_clip.with_position(('center', video.h - SUBTITLE_CONFIG["margin"] - SUBTITLE_CONFIG["font_size"]))
                    
                    subtitle_clips.append(subtitle_clip)
                    
                except Exception as e:
                    print(f"字幕 {i+1} 创建失败: {e}")
                    continue
            
            # 合成视频
            final_video = CompositeVideoClip([video] + subtitle_clips)
            
            # 写入文件
            final_video.write_videofile(
                output_file,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac'
            )
            
            # 关闭clips
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
    
    def add_audio(self, video_file, audio_file, output_file):
        """
        为视频添加配音
        
        Args:
            video_file: 视频文件路径
            audio_file: 音频文件路径
            output_file: 输出视频文件路径
        
        Returns:
            添加配音后的视频文件路径
        """
        try:
            video = VideoFileClip(video_file)
            audio = AudioFileClip(audio_file)
            
            # 如果音频比视频长，截取音频（moviepy 2.x使用subclipped）
            if audio.duration > video.duration:
                try:
                    audio = audio.subclipped(0, video.duration)
                except AttributeError:
                    audio = audio.subclip(0, video.duration)
            # 如果视频比音频长，循环音频或静音
            elif audio.duration < video.duration:
                # 可以循环音频或保持静音
                # 这里选择循环音频
                from moviepy import concatenate_audioclips
                loop_count = int(video.duration / audio.duration) + 1
                audio_clips = [audio] * loop_count
                try:
                    audio = concatenate_audioclips(audio_clips).subclipped(0, video.duration)
                except AttributeError:
                    audio = concatenate_audioclips(audio_clips).subclip(0, video.duration)
            
            # 设置音频
            final_video = video.with_audio(audio)
            
            # 写入文件
            final_video.write_videofile(
                output_file,
                fps=self.fps,
                codec='libx264',
                audio_codec='aac'
            )
            
            # 关闭clips
            video.close()
            audio.close()
            final_video.close()
            
            print(f"配音添加完成: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"添加配音失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_final_video(self, video_file, audio_file, subtitle_timeline, output_file):
        """
        创建最终视频（视频+配音+字幕）
        
        Args:
            video_file: 视频文件路径
            audio_file: 音频文件路径
            subtitle_timeline: 字幕时间轴
            output_file: 输出视频文件路径
        
        Returns:
            最终视频文件路径
        """
        # 先添加音频
        temp_video = os.path.join(OUTPUT_CONFIG["temp_dir"], "temp_with_audio.mp4")
        video_with_audio = self.add_audio(video_file, audio_file, temp_video)
        
        if not video_with_audio:
            return None
        
        # 再添加字幕
        final_video = self.add_subtitles(video_with_audio, subtitle_timeline, output_file)
        
        # 清理临时文件
        if os.path.exists(temp_video):
            os.remove(temp_video)
        
        return final_video
