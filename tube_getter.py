#!/usr/bin/env python3

import os
import sys
import threading
import urllib.error
import data
import webbrowser
import PySimpleGUI as psg
from datetime import datetime
from pytube import YouTube
from pytube import Playlist
import pytube.exceptions


def resource_path(relative_path):
    """PyInstaller requirement,
    Get an absolute path to resource, works for dev and for PyInstaller."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


version = "1.1"
themes = ["LightGrey", "DarkGrey4"]
colors = ["#FBFBFB", "#52524E"]
yt_playlist = []
table_list = []
download_start_time = datetime.now()


def settings_popup():
    """Creates a new window with app information / settings."""
    layout = [[psg.Image(filename=resource_path("./images/yt3d.png"))],
              [psg.Text(f"YOUTUBE GETTER v{version}\nby Paichiwo\n2023\n\n{data.popup_message}",
                        justification='c')],
              [psg.Image(filename=resource_path("./images/github.png")),
               psg.Text("GitHub",
                        font=("Arial", 10, "underline"),
                        enable_events=True)],
              [psg.Text("")],
              [psg.Button('OK')]]
    window = psg.Window("Information",
                        layout,
                        element_justification='c',
                        grab_anywhere=True,
                        finalize=True,
                        icon=resource_path("./images/yt3d.png"))
    while True:
        event, values = window.read()
        if event == psg.WIN_CLOSED:
            break
        if event in "GitHub":
            webbrowser.open(data.github_link)
        window.close()


def count_file_size(size_bytes):
    """Count the stream file sizes."""
    return round(size_bytes / (1024 * 1024), 1)


def get_playlist_links(url):
    """Create a list with user links."""
    if "playlist" in url:
        p = Playlist(url)
        for link in p.video_urls:
            yt_playlist.append(link)
    else:
        yt_playlist.append(url)


def update_table(i_tag, output_format,  window):
    """Update the table with user links information."""
    table_list.clear()
    for url in yt_playlist:
        yt = YouTube(url)
        try:
            table_list.append(
                [yt.streams.get_by_itag(i_tag).title,
                 output_format,
                 f"{count_file_size(yt.streams.get_by_itag(i_tag).filesize)} MB",
                 "0%",
                 "0 Mb/s",
                 "Queued"])
        except AttributeError:
            table_list.append(
                [yt.streams.get_highest_resolution().title,
                 output_format,
                 f"{count_file_size(yt.streams.get_highest_resolution().filesize)} MB",
                 "0%",
                 "0 Mb/s",
                 "Queued"])
    window["-TABLE-"].update(table_list)


def download_video(playlist, output_path, window):
    """Download video stream - highest resolution."""
    for index, link in enumerate(playlist):
        yt = YouTube(link, on_progress_callback=lambda stream, chunk, bytes_remaining: count_progress(
            index, stream, chunk, bytes_remaining, window))

        yt_stream = yt.streams.get_highest_resolution()
        # Set status to 'downloading'
        table_list[index][5] = "Downloading"
        window["-TABLE-"].update(table_list)
        try:
            yt_stream.download(output_path=output_path, filename=yt_stream.default_filename)
            # Set status to 'complete'
            table_list[index][5] = "Complete"
            window["-TABLE-"].update(table_list)
        except (PermissionError, RuntimeError):
            psg.popup("ERROR: Permission Error.")


def download_audio(playlist, output_path, window):
    """Download audio stream."""
    for index, link in enumerate(playlist):
        yt = YouTube(link, on_progress_callback=lambda stream, chunk, bytes_remaining: count_progress(
            index, stream, chunk, bytes_remaining, window))

        yt_stream = yt.streams.get_audio_only()
        # Set status to 'downloading'
        table_list[index][5] = "Downloading"
        window["-TABLE-"].update(table_list)

        # change an extension to mp3 if mp4 audio downloaded.
        if yt_stream.mime_type == "audio/mp4":
            filename = yt_stream.default_filename.rsplit(".", 1)[0] + ".mp3"
        else:
            filename = yt_stream.default_filename
        try:
            yt_stream.download(output_path=output_path, filename=filename)
            # Set status to 'complete'
            table_list[index][5] = "Complete"
            window["-TABLE-"].update(table_list)
        except (PermissionError, RuntimeError):
            psg.popup("ERROR: Permission Error.")


def count_progress(index, stream, chunk, bytes_remaining, window):
    """Count the progress of downloading file."""
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_completion = round(bytes_downloaded / total_size * 100, 2)
    table_list[index][3] = f"{percentage_completion}%"

    # Calculate and update the download speed
    elapsed_time = (datetime.now() - download_start_time).total_seconds()
    download_speed = bytes_downloaded / (1024 * elapsed_time)  # Convert bytes/sec to kilobytes/sec
    table_list[index][4] = f"{round(download_speed, 2)} KB/s"
    window["-TABLE-"].update(table_list)


def create_window(theme):
    """Application layout for PySimpleGUI."""
    psg.theme(theme)

    layout = [
        [psg.Text("Enter URLs:"),
         psg.Push(),
         psg.Text("Ext:"),
         psg.Combo(values=["Video", "Audio"],
                   default_value="Audio",
                   background_color="light grey",
                   text_color="black",
                   pad=(32, 5),
                   k="-FORMAT-"),
         psg.Button(image_filename=resource_path("./images/icons_black/sun.png"),
                    button_color=colors[0],
                    border_width=0,
                    pad=5,
                    k="-THEME-"),
         psg.Button(image_filename=resource_path("./images/icons_black/setting.png"),
                    button_color=colors[0],
                    border_width=0,
                    pad=5,
                    k="-SETTINGS-")],

        [psg.Input(focus=True,
                   background_color="light grey",
                   text_color="black",
                   expand_x=True,
                   border_width=0,
                   pad=5,
                   right_click_menu=["%Right", ["Paste"]],
                   k="-URL-"),
         psg.Button('Submit', visible=False, bind_return_key=True),
         psg.Button("Add",
                    border_width=0,
                    size=8,
                    pad=5,
                    k="-ADD-")],

        [psg.Image(filename=resource_path("./images/icons_black/folder.png")),
         psg.Input("C:/Users/",
                   background_color="light grey",
                   text_color="black",
                   expand_x=True,
                   border_width=0,
                   k="-DOWNLOAD-FOLDER-"),
         psg.FolderBrowse("Browse",
                          initial_folder="C:/Users/lzeru/Desktop/",
                          size=(8, 1))],

        [psg.Table(values=[],
                   headings=["Title", "Ext", "Size", "Progress", "Speed", "Status"],
                   col_widths=[33, 7, 7, 7, 8, 12],
                   auto_size_columns=False,
                   justification="c",
                   background_color="light grey",
                   alternating_row_color="grey",
                   text_color="black",
                   size=(10, 20),
                   expand_x=True,
                   border_width=0,
                   pad=5,
                   k="-TABLE-")],

        [psg.Button("Clear",
                    border_width=0,
                    size=8,
                    pad=5,
                    k="-CLEAR-"),
         psg.Push(),
         psg.Button("Download",
                    border_width=0,
                    size=8,
                    pad=5,
                    k="-DOWNLOAD-")]
    ]
    return psg.Window(f"YouTube Getter v{version}",
                      layout=layout,
                      size=(800, 490),
                      element_justification="c",
                      resizable=True,
                      icon=resource_path("./images/yt3d.png"),
                      finalize=True)


def main():
    """Main function for the YouTube Getter application."""
    window = create_window(themes[0])
    themes_counter = 1
    while True:
        event, values = window.read()
        if event == psg.WIN_CLOSED:
            break

        elif event == "Paste":
            window["-URL-"].update(psg.clipboard_get())

        elif event == "-THEME-":
            theme = themes[themes_counter % len(themes)]
            color = colors[themes_counter % len(themes)]
            window.close()
            window = create_window(theme)
            window["-SETTINGS-"].update(button_color=color)
            window["-THEME-"].update(button_color=color)
            themes_counter += 1

        elif event == "-SETTINGS-":
            settings_popup()

        elif event == "-ADD-" or event == "Submit":
            if values["-URL-"]:
                try:
                    get_playlist_links(values["-URL-"])
                    if values["-FORMAT-"] == "Video":
                        update_table(22, "mp4", window)
                    else:
                        update_table(140, "mp3", window)

                except pytube.exceptions.VideoUnavailable:
                    psg.popup("ERROR: Video is age restricted.")
                except pytube.exceptions.RegexMatchError:
                    psg.popup("ERROR: Wrong URL.")
                except (urllib.error.URLError, urllib.error.HTTPError):
                    psg.popup("ERROR: Internal error.")
            else:
                psg.Popup("ERROR: No url detected.")

        elif event == "-CLEAR-":
            yt_playlist.clear()
            table_list.clear()
            window["-TABLE-"].update(table_list)

        elif event == "-DOWNLOAD-":
            output_format = values["-FORMAT-"]
            output_path = values["-DOWNLOAD-FOLDER-"]
            if output_format == "mp4":
                threading.Thread(target=download_video, args=(yt_playlist.copy(), output_path, window)).start()
                print(type(window["-TABLE-"]))
            else:
                threading.Thread(target=download_audio, args=(yt_playlist.copy(), output_path, window)).start()

    window.close()


if __name__ == "__main__":
    main()
