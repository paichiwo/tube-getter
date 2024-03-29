import json
import os
import sys
from pytube import Playlist


def resource_path(relative_path):
    """Get the absolute path to a resource, accommodating both development and PyInstaller builds"""
    if hasattr(sys, '_MEIPASS'):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def get_downloads_folder_path():
    """Get the path to the Downloads folder on Windows"""
    user_profile = os.environ['USERPROFILE']
    downloads_folder = os.path.join(user_profile, 'Downloads')
    return downloads_folder


def center_window(window, width, height):
    """Center a window on the screen using the provided dimensions"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")
    window.update_idletasks()


def count_file_size(size_bytes):
    """Convert bytes to megabytes (MB) for representing file sizes"""
    return round(size_bytes / (1024 * 1024), 1)


def get_playlist_links(url, array):
    """    Retrieve individual video links from a YouTube playlist and add them to a list"""
    if "list=" in url:
        p = Playlist(url)
        for link in p.video_urls:
            array.append(link)
    else:
        array.append(url)


def load_settings():
    """Load settings from a JSON file"""
    path = os.path.join(os.environ['LOCALAPPDATA'], 'Tube-Getter', 'settings.json')
    try:
        with open(path, 'r') as file:
            settings = json.load(file)
            return settings.get('output_folder')
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        output_folder = get_downloads_folder_path()
        return output_folder


def save_settings(output_folder):
    """Save settings to a JSON file"""
    settings_file = 'settings.json'
    path = os.path.join(os.environ['LOCALAPPDATA'], 'Tube-Getter')
    settings_path = os.path.join(path, settings_file)
    data = {'output_folder': output_folder}

    if not os.path.exists(path):
        os.makedirs(path)

    with open(settings_path, 'w') as file:
        json.dump(data, file)
