import json
import os
import re
import subprocess
import requests
import zipfile
import threading
from datetime import datetime
from pytubefix import Playlist
from customtkinter import CTkImage
from PIL import Image
from bs4 import BeautifulSoup
from src.config import GITHUB_URL
from src.resource_path import resource_path

ffmpeg_exe = 'ffmpeg.exe'


def get_downloads_folder_path():
    """Get the path to the Downloads folder on Windows"""
    user_profile = os.environ['USERPROFILE']
    downloads_folder = os.path.join(user_profile, 'Downloads')
    return downloads_folder


def center_window(window, width, height):
    """Center window based on the resolution"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f'{width}x{height}+{x}+{y}')
    window.update_idletasks()


def imager(path, x, y):
    """Easy way to create image with CTK"""
    return CTkImage(Image.open(path), size=(x, y))


def get_links(url, array):
    """Retrieve individual video links from a YouTube playlist and add them to a list"""
    if "list=" in url:
        p = Playlist(url)
        for link in p.video_urls:
            array.append(link)
    else:
        array.append(url)


def load_settings():
    """Load settings from JSON file"""
    path = os.path.join(os.environ['LOCALAPPDATA'], 'Tube-Getter', 'settings.json')
    try:
        with open(path, 'r') as file:
            return json.load(file).get('output_folder')
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return get_downloads_folder_path()


def save_settings(data, file_name):
    """Save settings to JSON file"""
    path = os.path.join(os.environ['LOCALAPPDATA'], 'Tube-Getter')
    settings_path = os.path.join(path, file_name)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(settings_path, 'w') as file:
        json.dump(data, file)


def open_downloads_folder():
    """Use os to open target folder"""
    os.startfile(load_settings())


def format_file_size(size_bytes) -> str:
    """Convert bytes to MB / GB"""
    if size_bytes >= 1024 ** 3:
        return f'{(size_bytes / (1024 ** 3)):.2f} GB'
    else:
        return f'{(size_bytes / (1024 ** 2)):.2f} MB'


def format_dl_speed_string(download_speed):
    """Format dl speed to KB/s and MB/s"""
    if download_speed < 1000:
        return f'{download_speed:.2f} KiB/s'
    else:
        return f'{download_speed / 1024:.2f} MiB/s'


def format_filename(filename):
    """Remove special characters and capitalize filename string"""
    chars_removed_title = re.sub(r'[^\w ]', '', filename)
    words = chars_removed_title.split()
    new_words = []
    for word in words:
        new_words.append(word.capitalize())
    return ' '.join(new_words)


def format_date(date):
    """Format date to DD-MM-YYYY"""
    return datetime.strptime(str(date).split(' ')[0], '%Y-%m-%d').strftime('%d-%m-%Y')


def convert_time(time_in_sec):
    """Convert time in seconds to HH:MM:SS"""
    hours = time_in_sec // 3600
    time_in_sec %= 3600
    minutes = time_in_sec // 60
    time_in_sec %= 60
    return f'{hours:02d}:{minutes:02d}:{time_in_sec:02d}'


def handle_audio_extension(stream):
    """Create string with mp3 in case YouTube audio downloads as mp4"""
    if stream.mime_type == 'audio/mp4':
        return stream.default_filename.rsplit('.', 1)[0] + '.mp3'
    else:
        return stream.default_filename


def unzip_ffmpeg():
    """Unzip ffmpeg file"""
    dir_path = os.path.join(os.environ['LOCALAPPDATA'], 'Tube-Getter')
    exe_path = os.path.join(dir_path, ffmpeg_exe)

    if not os.path.exists(exe_path):
        os.makedirs(dir_path, exist_ok=True)

    with zipfile.ZipFile(resource_path('ffmpeg/ffmpeg.zip'), 'r') as zip_ref:
        zip_ref.extract(ffmpeg_exe, dir_path)


def convert_to_mp3(input_file, output_file, progress_callback=None):
    """Use ffmpeg to convert mp4 to mp3. Output progress"""
    ffmpeg_path = os.path.join(os.environ['LOCALAPPDATA'], 'Tube-Getter', ffmpeg_exe)

    ffmpeg_command = [ffmpeg_path, '-i', input_file, '-b:a', '128k', '-y', output_file]

    process = subprocess.Popen(
        ffmpeg_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW,
        universal_newlines=True)

    duration = extract_duration(process.stderr)
    track_progress(process.stderr, duration, progress_callback)

    progress_thread = threading.Thread(target=track_progress,
                                       args=(process.stderr, duration, progress_callback))
    progress_thread.start()


def extract_duration(ffmpeg_output):
    """Extract duration information from ffmpeg output"""
    for line in ffmpeg_output:
        if 'Duration: ' in line:
            match = re.search(r'Duration:\s+(\d{2}):(\d{2}):(\d{2}).\d+', line)
            if match:
                hours, minutes, seconds = map(int, match.groups())
                return hours * 3600 + minutes * 60 + seconds


def track_progress(ffmpeg_output, duration, progress_callback):
    """Extract time progress information from ffmpeg output and call the progress_callback"""
    for line in ffmpeg_output:
        if 'time=' in line and duration:
            match = re.search(r'time=\s*(\d{2}):(\d{2}):(\d{2}).\d+', line)
            if match:
                hours, minutes, seconds = map(int, match.groups())
                current_time = hours * 3600 + minutes * 60 + seconds
                progress = round(current_time / duration, 3)
                progress_callback(progress)


def check_for_new_version():
    """Check for new version in GitHub repo"""
    response = requests.get(GITHUB_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.find(class_='css-truncate css-truncate-target text-bold mr-2').text.split()[2][1:]

