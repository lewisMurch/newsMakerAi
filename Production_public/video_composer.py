import os
import subprocess
import json
from moviepy.editor import (VideoFileClip, ImageClip, CompositeVideoClip, 
                            AudioFileClip, CompositeAudioClip, ColorClip)
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import footage_getter
import date_getter
import numpy as np
import pathlib
current_dir = str(pathlib.Path().resolve())

# flag for using GPU to render video
USE_GPU = True

from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_text_image_rounded(text, font_size, font_color, image_width, image_height, corner_radius=20):
    font_path = "Fonts/Frutiger.ttf"
    font = ImageFont.truetype(font_path, font_size)
    image = Image.new('RGBA', (image_width, image_height), (0, 0, 0, 0))  # Transparent background
    mask = Image.new('L', (image_width, image_height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [(0, 0), (image_width, image_height)], 
        radius=corner_radius, 
        fill=255
    )
    image.paste((0, 0, 0, 255), (0, 0), mask)  # Pasting a black rounded rectangle


    draw = ImageDraw.Draw(image)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    draw.text(((image_width - text_width) // 2, (image_height - text_height) // 2), text, font=font, fill=font_color)
    
    return np.array(image)

def create_text_image(text, font_size, font_color, image_width, image_height):
    font_path = "Fonts/Frutiger.ttf"
    font = ImageFont.truetype(font_path, font_size)
    
    image = Image.new('RGB', (image_width, image_height), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    draw.text((0, (image_height - text_height) // 2), text, font=font, fill=font_color)
    return np.array(image)

def blur_image(image_path, blur_percentage, politic):
    pil_image = Image.open(image_path).convert('RGB')
    blur_radius = blur_percentage * 2  # Adjust as necessary for desired effect
    blurred_image = pil_image.filter(ImageFilter.GaussianBlur(blur_radius))

    blurred_image_path = os.path.join(current_dir, 'politics', politic, "blurred_image.jpg")
    blurred_image.save(blurred_image_path)
    return blurred_image_path

def run(text, video_name, politic, blur_percentage=7, scale_speed=0.02):
    final_width, final_height = 1080, 1920
    volume = 6
    delay = 0

    image_box_x1, image_box_y1 = 0, 0
    image_box_x2, image_box_y2 = 1080, 768

    avatar_box_x1, avatar_box_y1 = 20, 370
    avatar_box_x2, avatar_box_y2 = 260, 660

    additional_video_box_x1, additional_video_box_y1 = 0, 768
    additional_video_box_x2, additional_video_box_y2 = 1080, 1920
    
    black_bar_height = 100
    black_bar_y = 728
    text = 'Headline: ' + text.rstrip('.')

    #removes the sometimes up to 3 '!''s the LLM can place
    text = text.rstrip('!')
    text = text.rstrip('!')
    text = text.rstrip('!')

    scrolling_text = text

    # Define the image paths
    related_image_path = os.path.join('politics', politic, 'related_images')
    default_image_path = 'Assets/news.jpg'

    try:
        # List image files in the directory
        image_files = [f for f in os.listdir(related_image_path) if os.path.isfile(os.path.join(related_image_path, f)) and f.endswith(('.png', '.jpg', '.jpeg'))]
        
        if image_files:
            # Get the most recent image
            most_recent_image_path = os.path.join(related_image_path, max(image_files, key=lambda f: os.path.getctime(os.path.join(related_image_path, f))))
        else:
            # If no images are found, use the default image
            most_recent_image_path = default_image_path
    except Exception as e:
        # If there is an error (e.g., the directory doesn't exist), use the default image
        most_recent_image_path = default_image_path

    avatar_path = os.path.join(current_dir, 'politics', politic, 'mascot_video', "final_mascot.webm")
    avatar_clip = VideoFileClip(avatar_path).set_start(delay)
    
    image_clip = ImageClip(most_recent_image_path)
    blurred_image_path = blur_image(most_recent_image_path, blur_percentage, politic)
    image_clip_blur_background = ImageClip(blurred_image_path)

    attention_video_path = footage_getter.check_and_swap_folders(politic)
    additional_video_clip = VideoFileClip(attention_video_path)

    image_clip_duration = avatar_clip.duration + delay
    image_clip = image_clip.set_duration(image_clip_duration)
    image_clip_blur_background = image_clip_blur_background.set_duration(image_clip_duration)
    additional_video_clip = additional_video_clip.set_duration(image_clip_duration)

    def resize_and_position_clip(clip, box_x1, box_y1, box_x2, box_y2, fill_axis=None):
        box_width = box_x2 - box_x1
        box_height = box_y2 - box_y1

        if fill_axis == 'x':
            clip = clip.resize(width=box_width)
        elif fill_axis == 'y':
            clip = clip.resize(height=box_height)
        else:
            if clip.w / clip.h < box_width / box_height:
                clip = clip.resize(height=box_height)
            else:
                clip = clip.resize(width=box_width)

        clip_x = box_x1 + (box_width - clip.w) / 2
        clip_y = box_y1 + (box_height - clip.h) / 2

        return clip.set_position((clip_x, clip_y))

    image_clip = resize_and_position_clip(image_clip, image_box_x1, image_box_y1, image_box_x2, image_box_y2, 'y')
    image_clip_blur_background = resize_and_position_clip(image_clip_blur_background, image_box_x1, image_box_y1, image_box_x2, image_box_y2, 'x')
    avatar_clip = resize_and_position_clip(avatar_clip, avatar_box_x1, avatar_box_y1, avatar_box_x2, avatar_box_y2, 'x')
    additional_video_clip = resize_and_position_clip(additional_video_clip, additional_video_box_x1, additional_video_box_y1, additional_video_box_x2, additional_video_box_y2, 'y')

    # Apply dynamic scaling to the image_clip_blur_background
    def dynamic_scale(t):
        return 1 + scale_speed * t

    image_clip_blur_background = image_clip_blur_background.resize(dynamic_scale)

    filepath_TTS = os.path.join('politics', politic, 'TTS')
    tts_audio_path = current_dir + f"/{filepath_TTS}/TTS_output.wav"

    news_audio_path = os.path.join('politics', politic, 'static_audio', 'news_sound.mp3')
    news_audio = AudioFileClip(news_audio_path).volumex(volume / 100)
    tts_audio = AudioFileClip(tts_audio_path).set_start(delay)

    tts_audio_duration = min(tts_audio.duration, image_clip_duration)
    tts_audio = tts_audio.set_duration(tts_audio_duration)

    combined_audio = CompositeAudioClip([
        avatar_clip.audio.set_duration(image_clip_duration).set_start(delay),
        news_audio.set_duration(image_clip_duration),
        tts_audio.set_duration(tts_audio_duration)
    ])

    date = date_getter.get_formatted_date()

    black_bar_clip = ColorClip(size=(final_width, black_bar_height), color=(0, 0, 0)).set_position(('center', black_bar_y)).set_duration(image_clip_duration)

    scroll_speed = len(text) / (image_clip_duration * 410)

    text_image = create_text_image(scrolling_text, 54, "white", final_width * 10, black_bar_height)
    text_clip = ImageClip(text_image).set_duration(image_clip_duration)
    text_clip = text_clip.set_position(lambda t: (final_width - (final_width + text_image.shape[1]) * (t * scroll_speed), black_bar_y))

    # Create date text image
    date = ' ' + date
    char_width = 20
    date_image = create_text_image_rounded(date, 40, "white", char_width * len(date), 70, 20)
    date_clip = ImageClip(date_image).set_duration(image_clip_duration)
    date_clip = date_clip.set_position((final_width - (char_width * len(date)), final_height - 70))

    final_clip = CompositeVideoClip([image_clip_blur_background, additional_video_clip, image_clip, avatar_clip, black_bar_clip, text_clip, date_clip], size=(final_width, final_height))

    final_clip.audio = combined_audio
    os.makedirs('final_videos', exist_ok=True)
    # Add a $ to the second character of the video name
    video_name_before_render = video_name[:1] + '$' + video_name[2:]

    # Paths for the video files
    temp_video_path = f"final_videos/{video_name_before_render}.mp4"
    final_video_path = f"final_videos/{video_name}.mp4"

    # Render the video with the temporary name
    if USE_GPU:
        print('USING GPU TO RENDER')
        final_clip.write_videofile(temp_video_path, codec="h264_nvenc", fps=30, audio_codec="aac", bitrate="10000k")
    else:
        print('USING CPU TO RENDER')
        final_clip.write_videofile(temp_video_path, codec="libx264", fps=30, audio_codec="aac", bitrate="10000k")

    # Rename the video file to the proper name after rendering is complete
    try:
        os.rename(temp_video_path, final_video_path)
        print(f"Video has been renamed to: {final_video_path}")

    except:
        os.rename(temp_video_path + 'copy 1', final_video_path)
        print(f"Video has been renamed to: {temp_video_path + 'copy 1'}")
