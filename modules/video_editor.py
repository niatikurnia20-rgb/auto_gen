import os
import requests

try:
    from moviepy import AudioFileClip, VideoFileClip, concatenate_videoclips, vfx
except ImportError:
    from moviepy.editor import AudioFileClip, VideoFileClip, concatenate_videoclips
    vfx = None

from config import TEMP_FOLDER
from modules.video_format import get_target_size, normalize_aspect_ratio


def _resize_clip(clip, width=None, height=None):
    kwargs = {}
    if width is not None:
        kwargs["width"] = width
    if height is not None:
        kwargs["height"] = height

    if hasattr(clip, "resized"):
        return clip.resized(**kwargs)
    return clip.resize(**kwargs)


def _subclip(clip, start_time, end_time):
    if hasattr(clip, "subclipped"):
        return clip.subclipped(start_time, end_time)
    return clip.subclip(start_time, end_time)


def _loop_clip(clip, duration):
    if hasattr(clip, "with_effects") and vfx is not None:
        return clip.with_effects([vfx.Loop(duration=duration)])
    return clip.loop(duration=duration)


def _set_duration(clip, duration):
    if hasattr(clip, "with_duration"):
        return clip.with_duration(duration)
    return clip.set_duration(duration)


def _set_audio(clip, audio_clip):
    if hasattr(clip, "with_audio"):
        return clip.with_audio(audio_clip)
    return clip.set_audio(audio_clip)


def _crop_clip(clip, x1, y1, x2, y2):
    if hasattr(clip, "cropped"):
        return clip.cropped(x1=x1, y1=y1, x2=x2, y2=y2)
    return clip.crop(x1=x1, y1=y1, x2=x2, y2=y2)


def _fit_clip_to_frame(clip, target_width, target_height):
    source_width = getattr(clip, "w", 0)
    source_height = getattr(clip, "h", 0)

    if not source_width or not source_height:
        raise ValueError("Invalid source clip size.")

    width_scale = target_width / source_width
    height_scale = target_height / source_height

    if width_scale >= height_scale:
        clip = _resize_clip(clip, width=target_width)
    else:
        clip = _resize_clip(clip, height=target_height)

    x1 = max(int((clip.w - target_width) / 2), 0)
    y1 = max(int((clip.h - target_height) / 2), 0)
    x2 = x1 + target_width
    y2 = y1 + target_height

    return _crop_clip(clip, x1=x1, y1=y1, x2=x2, y2=y2)

def download_file(url, filename):
    try:
        with open(filename, 'wb') as f:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Download Error: {e}")
        return False

def create_video(script_text, audio_path, media_urls, output_filename, aspect_ratio='landscape'):
    aspect_ratio = normalize_aspect_ratio(aspect_ratio)
    target_width, target_height = get_target_size(aspect_ratio)

    # 1. Load Audio
    try:
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration # e.g., 60 seconds
    except:
        raise ValueError("Could not load audio.")

    if not media_urls:
        raise ValueError("No video clips found.")
    
    # 2. Logic: How long should each clip be?
    # We want fast cuts (e.g., every 5 seconds) to keep it engaging.
    target_clip_duration = 5.0 
    
    clips = []
    current_duration = 0
    media_index = 0
    
    # 3. Build the video loop until we match audio duration
    while current_duration < audio_duration:
        # Cycle through the media files we have
        vid_url = media_urls[media_index % len(media_urls)]
        media_index += 1
        
        local_vid_path = os.path.join(TEMP_FOLDER, f"clip_{media_index}.mp4")
        
        if not download_file(vid_url, local_vid_path):
            continue

        try:
            video_clip = VideoFileClip(local_vid_path).without_audio()
            video_clip = _fit_clip_to_frame(video_clip, target_width, target_height)
            
            # Determine how much time is left to fill
            time_left = audio_duration - current_duration
            
            # Use the shorter of: target duration (5s) OR time left
            this_clip_duration = min(target_clip_duration, time_left)
            
            # Handle source clip length
            if video_clip.duration < this_clip_duration:
                # If source is too short, loop it
                video_clip = _loop_clip(video_clip, duration=this_clip_duration)
            else:
                # Cut a random segment or the start
                video_clip = _subclip(video_clip, 0, this_clip_duration)
            
            video_clip = _set_duration(video_clip, this_clip_duration)
            clips.append(video_clip)
            current_duration += this_clip_duration
            
        except Exception as e:
            print(f"Clip Error: {e}")
            
    # 4. Final Assembly
    if clips:
        final_video = concatenate_videoclips(clips, method="compose")
        final_video = _set_audio(final_video, audio_clip)
        
        # Add subtitles (Optional, simple centered text)
        # Note: Complex subtitles require ImageMagick. If it fails, we skip text.
        try:
           # (We skip text here to ensure video renders 100% of the time for now)
           pass 
        except:
           pass

        final_video.write_videofile(
            output_filename, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            preset='ultrafast'
        )
        return output_filename
    else:
        raise ValueError("Video creation failed.")
