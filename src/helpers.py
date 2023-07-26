import json
import os
import sys

from pytube import Playlist, YouTube


def resource_path(relative_path):
    """PyInstaller requirement,
    Get an absolute path to resource, works for dev and for PyInstaller."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def get_downloads_folder_path():
    """Get the path to the Downloads folder on Windows"""
    user_profile = os.environ['USERPROFILE']
    downloads_folder = os.path.join(user_profile, 'Downloads')
    return downloads_folder


def center_window(window, width, height):
    """Create a window in the center of the screen, using desired dimensions"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")
    window.update_idletasks()


def count_file_size(size_bytes):
    """Count the stream file sizes in MB"""
    return round(size_bytes / (1024 * 1024), 1)


def get_playlist_links(url, array):
    """Create a list with individual links from yt playlist"""
    if "playlist" in url:
        p = Playlist(url)
        for link in p.video_urls:
            array.append(link)
    else:
        array.append(url)


def get_data_for_treeview(i_tag, output_format, yt_list):
    """Return a list with data to display in the treeview"""
    treeview_list = []
    for url in yt_list:
        yt = YouTube(url)
        try:
            treeview_list.append([
                yt.streams.get_by_itag(i_tag).title,
                output_format,
                f"{count_file_size(yt.streams.get_by_itag(i_tag).filesize)} MB",
                "0 %",
                "0 Mb/s",
                "Queued"
            ])
        except AttributeError:
            treeview_list.append([
                yt.streams.get_highest_resolution().title,
                output_format,
                f"{count_file_size(yt.streams.get_highest_resolution().filesize)} MB",
                "0 %",
                "0 Mb/s",
                "Queued"
            ])
    return treeview_list


def load_settings():
    """Load settings from .json file"""
    try:
        with open(resource_path('../data/settings.json'), 'r') as file:
            settings = json.load(file)
            return settings['output_folder']
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        output_folder = get_downloads_folder_path()
        return output_folder


def save_settings(output_folder):
    """Save settings to .json file"""
    with open(resource_path('../data/settings.json'), 'w') as file:
        json.dump({'output_folder': output_folder}, file)



