import json
import os
import sys
from pytubefix import Playlist
from customtkinter import CTkImage
from PIL import Image


def resource_path(relative_path):
    """Get the absolute path for auto-py-to-exe"""
    if hasattr(sys, '_MEIPASS'):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


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
    return CTkImage(Image.open(path), size=(x, y))


def count_file_size(size_bytes):
    """Convert bytes to megabytes (MB) for representing file sizes"""
    if size_bytes >= 1024 * 1024 * 1024:
        return round(size_bytes / (1024 * 1024 * 1024), 2), "GB"
    else:
        return round(size_bytes / (1024 * 1024), 2), "MB"


def get_links(url, array):
    """Retrieve individual video links from a YouTube playlist and add them to a list"""
    if "list=" in url:
        p = Playlist(url)
        for link in p.video_urls:
            array.append(link)
    else:
        array.append(url)


def load_settings():
    # Load settings from JSON file
    path = os.path.join(os.environ['LOCALAPPDATA'], 'Tube-Getter', 'settings.json')
    try:
        with open(path, 'r') as file:
            return json.load(file).get('output_folder')
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return get_downloads_folder_path()


def save_settings(data, file_name):
    # Save settings to JSON file
    path = os.path.join(os.environ['LOCALAPPDATA'], 'Tube-Getter')
    settings_path = os.path.join(path, file_name)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(settings_path, 'w') as file:
        json.dump(data, file)


def open_downloads_folder():
    os.startfile(load_settings())


def format_download_speed_string(download_speed):
    if download_speed < 1000:
        return f'{download_speed:.2f} KiB/s'
    else:
        return f'{download_speed / 1024:.2f} MiB/s'


def handle_audio_extension(stream):
    if stream.mime_type == 'audio/mp4':
        return stream.default_filename.rsplit('.', 1)[0] + '.mp3'
    else:
        return stream.default_filename
