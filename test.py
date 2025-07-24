# pip install yt-dlp moviepy sanitize-filename

import os
import yt_dlp
import json
import csv
from sanitize_filename import sanitize
from moviepy import VideoFileClip, AudioFileClip, vfx, afx, CompositeVideoClip, CompositeAudioClip

# Load JSON settings
with open('./settings.json', 'r', encoding='utf-8') as f:
    json_file = json.load(f)

settings = json_file.get('settings', {})
fade_duration = settings.get('fade_duration', 2) # seconds with 2 as default
cd_url = settings.get('countdown_url')
cd_start = settings.get('countdown_start_time', 0)
cd_end = settings.get('countdown_end_time', 0)
cd_fade = settings.get('countdown_fade_duration', 1)
cd_start_offset = settings.get('countdown_start_offset', 0)
cd_end_offset = settings.get('countdown_end_offset', 0)

# Convert column letters to indices
columns = json_file.get('columns', {})
for key, value in columns.items():
    if isinstance(value, str) and len(value) == 1:
        columns[key] = ord(value.upper()) - ord('A')

# Validate file format
is_mp3_only = settings.get('mp3_only', False)
file_format = 'mp3' if is_mp3_only else 'mp4'

# Format start and end times helper
def time_to_seconds(timestr):
    parts = [int(p) for p in timestr.strip().split(':')]
    return sum(p * 60**i for i, p in enumerate(reversed(parts)))

# Fetch songs list from CSV
songs = []
with open('data/entry.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for i, row in enumerate(reader):
        if i < 1 or len(row) < columns['end_ts']:
            continue  # skip header or incomplete rows
        song_name = sanitize(row[columns['song_name']])  # column C
        song_artist = sanitize(row[columns['song_artist']])  # column D
        url = row[columns['url']]  # column J
        start_ts = row[columns['start_ts']]  # column K
        end_ts = row[columns['end_ts']]    # column L
        is_mirrored = (False if row[columns['is_mirrored']] == "ใช่" else True) if len(row) > columns['is_mirrored'] else True  # column P, if exists

        if not url or not song_name or not start_ts or not end_ts:
            break  # skip if URL or song details are missing
        
        songs.append({
            'file_name': f"{song_name} - {song_artist}".strip(),  # Remove special characters and foreign characters
            'url': url,
            'start_time': time_to_seconds(start_ts),
            'end_time': time_to_seconds(end_ts),
            'is_mirrored': is_mirrored
        })

# Create directories if they don't exist
os.makedirs("downloads", exist_ok=True)
os.makedirs("final", exist_ok=True)

# Download helper
def download_youtube(file_name, url):
    out_path = f"downloads/{file_name}" + (f".{file_format}" if not is_mp3_only else "") # Because mp3 will have its own extension

    if not os.path.exists(out_path + (f".{file_format}" if is_mp3_only else "")): # Check if already downloaded
        print(f"Downloading {file_name}...")
        ydl_opts = {
            'outtmpl': out_path, 
            'quiet': True,
            'compat-options': ['filename-sanitization'],  # Ensure file names are sanitized
            'noplaylist': True,  # Download only the single video, not playlists
        }

        if is_mp3_only:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '0',  # best quality :contentReference[oaicite:3]{index=3}
                }],
            })
        else:
            ydl_opts['format'] = 'mp4'
            
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Downloaded {file_name}")

    # NOTE: Any special characters in the file name will be replaced with # hastags
    return out_path + (f".{file_format}" if is_mp3_only else "") # But append mp3 back when finding the file

# Download countdown clip original to be copied
countdown_path = download_youtube("!countdown", cd_url)
countdown_raw = VideoFileClip(countdown_path) if not is_mp3_only else AudioFileClip(countdown_path)
countdown_duration = countdown_raw.duration
cd_end = min(cd_end, countdown_duration) # Ensure end time does not exceed video duration
base_countdown_clip = countdown_raw.subclipped(cd_start, cd_end)
base_countdown_clip = base_countdown_clip.with_effects([vfx.FadeIn(cd_fade), vfx.FadeOut(cd_fade),  afx.AudioNormalize(), afx.AudioFadeOut(cd_fade)]) if not is_mp3_only else base_countdown_clip.with_effects([afx.AudioNormalize(), afx.AudioFadeOut(cd_fade)])

# Prepare final clips list
final_clips = []

# Download and process each song
for song in songs:
    file_name = song['file_name']
    url = song['url']
    start_time = song.get('start_time', 0)
    end_time = song.get('end_time', 0)
    is_mirrored = song.get('is_mirrored', False)
    
    # Define clip variable and get duration
    video_path = download_youtube(file_name, url)
    clip = VideoFileClip(video_path) if not is_mp3_only else AudioFileClip(video_path)
    duration = clip.duration

    # Clamp start/end beyond fade duration
    start_time = max(0, start_time - fade_duration)
    end_time = min(duration, end_time + fade_duration)
    clip = clip.subclipped(start_time, end_time)

    # Apply video fade (optional)
    clip = clip.with_effects(
        [
            vfx.FadeIn(fade_duration),
            vfx.FadeOut(fade_duration),
            afx.AudioNormalize(),
            afx.AudioFadeIn(fade_duration),
            afx.AudioFadeOut(fade_duration)
        ]
    ) if not is_mp3_only else clip.with_effects(
        [
            afx.AudioNormalize(), 
            afx.AudioFadeIn(fade_duration), 
            afx.AudioFadeOut(fade_duration)
        ]
    )

    # Apply mirror if not mirrored yet
    if not is_mirrored and not is_mp3_only:
        clip = clip.with_effects([vfx.MirrorX()])
    
    # Insert countdown before this clip
    countdown = base_countdown_clip.copy()
    if len(final_clips) >= 2:
        # If there are previous clips, adjust countdown start time
        countdown = countdown.with_start(final_clips[-1].end - cd_start_offset)
    final_clips.append(countdown)
    
    # Insert the processed clip after countdown
    clip = clip.with_start(countdown.end - cd_end_offset)
    final_clips.append(clip)

    # Remove the original downloaded file
    print(f"Finished queuing {file_name}\n")

# Concatenate all final clips
if not final_clips:
    print("No clips to process. Exiting.")
    exit(0)
final_video = CompositeVideoClip(final_clips) if not is_mp3_only else CompositeAudioClip(final_clips)

# Export mp4 if not mp3 only
if not is_mp3_only:
    final_video_path = f"final/final_output.{file_format}"
    final_video.write_videofile(final_video_path)
    print(f"Exporting final video to {final_video_path}...")
    
    # Export audio separately
    final_audio_path = f"final/final_output.mp3"
    final_video.audio.write_audiofile(final_audio_path)
    print(f"Exporting final audio to {final_audio_path}...")
else:
    final_audio_path = f"final/final_output.{file_format}"
    final_video.write_audiofile(final_audio_path)
    print(f"Exporting final audio to {final_audio_path}...")

# Clean up downloaded and processed files
for clip in final_clips:
    clip.close()

for song in songs:
    file_name = song['file_name']
    os.remove(f"downloads/{file_name}.{file_format}")