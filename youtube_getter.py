#!/usr/bin/env python3

import os
import sys
import pytube.exceptions
import data
import webbrowser
import PySimpleGUI as psg
from datetime import datetime
from pytube import YouTube
from pytube import Playlist
from pytube.exceptions import VideoUnavailable


# https://www.youtube.com/playlist?list=PLRNsV20DA24Gmt9C-X4CVFF4eP76KtkLq


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
    layout = [[psg.Image(filename=resource_path("./images/youtube.png"))],
              [psg.Text(f"YOUTUBE GETTER v{version}\nby Paichiwo\n2023\n\n{data.popup_message}",
                        justification='c')],
              [psg.Image(filename=resource_path("./images/github.png")),
               psg.Text("GitHub",
                        font=("Arial", 10, "underline"),
                        enable_events=True)],
              [psg.Button('OK')]]
    window = psg.Window("Information",
                        layout,
                        element_justification='c',
                        grab_anywhere=True,
                        finalize=True,
                        icon=resource_path("./images/youtube.png"))
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


def count_progress(stream, chunk, bytes_remaining, window):
    """Count the progress of downloading file."""
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_completion = round(bytes_downloaded / total_size * 100, 2)
    for item in table_list:
        item[3] = f"{percentage_completion}%"
    window["-TABLE-"].update(table_list)


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
    for url in yt_playlist:
        yt = YouTube(url)
        table_list.append(
            [yt.streams.get_by_itag(i_tag).title,
             output_format,
             f"{count_file_size(yt.streams.get_by_itag(i_tag).filesize)} MB",
             "0%",
             "0 Mb/s",
             "testing"])
    window["-TABLE-"].update(table_list)


def download_video(playlist, output_path, window):
    """Download video stream - highest resolution."""
    for url in playlist:
        yt = YouTube(url, on_progress_callback=lambda stream, chunk, bytes_remaining: count_progress(stream,
                                                                                                     chunk,
                                                                                                     bytes_remaining,
                                                                                                     window))
        yt_stream = yt.streams.get_highest_resolution()
        yt_stream.download(output_path=output_path, filename=yt_stream.default_filename)


def download_audio(playlist, output_path, window):
    """Download audio stream."""
    for url in playlist:
        yt = YouTube(url, on_progress_callback=lambda stream, chunk, bytes_remaining: count_progress(stream,
                                                                                                     chunk,
                                                                                                     bytes_remaining,
                                                                                                     window))
        yt_stream = yt.streams.get_audio_only()
        if yt_stream.mime_type == "audio/mp4":
            filename = yt_stream.default_filename.rsplit(".", 1)[0] + ".mp3"
        else:
            filename = yt_stream.default_filename
        yt_stream.download(output_path=output_path, filename=filename)


def create_window(theme):
    """Application layout for PySimpleGUI."""
    psg.theme(theme)

    layout = [
        [psg.Push(),
         psg.Button(image_filename=resource_path("./images/close.png"),
                    button_color=colors[0],
                    border_width=0,
                    k="-CLOSE-")],

        [psg.Text("Enter URLs:"),
         psg.Push()],

        [psg.Input("",
                   focus=True,
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
                    k="-ADD-"),
         psg.Push(),
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

        [psg.Image(filename=resource_path("./images/icons_black/folder.png")),
         psg.Input("C:/Users/",
                   background_color="light grey",
                   text_color="black",
                   border_width=0,
                   k="-DOWNLOAD-FOLDER-"),
         psg.FolderBrowse("•••",
                          button_color=("black", colors[0]),
                          initial_folder="C:/Users/",
                          k="-DOTS-"),
         psg.Push(),
         psg.Text("Format"),
         psg.Combo(values=["mp4", "mp3"],
                   default_value="mp3",
                   k="-FORMAT-"),
         ],

        [psg.Table(values=[],
                   headings=["Title", "Ext", "Size", "Progress", "Speed", "Status"],
                   col_widths=[33, 7, 8, 6, 8, 12],
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
                    k="-CLEAR-"),
         psg.Push(),
         psg.Button("Download",
                    border_width=0,
                    k="-DOWNLOAD-")]
    ]
    return psg.Window(f"YouTube Getter v{version}",
                      layout=layout,
                      size=(800, 550),
                      element_justification="c",
                      no_titlebar=False,
                      grab_anywhere=True,
                      finalize=True)


def main():
    """Main function for the YouTube Getter application."""
    window = create_window(themes[0])
    themes_counter = 1
    while True:
        event, values = window.read()
        if event == psg.WIN_CLOSED or event == "-CLOSE-":
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
            window["-CLOSE-"].update(button_color=color)
            window["-DOTS-"].update(button_color=color)
            themes_counter += 1

        elif event == "-SETTINGS-":
            settings_popup()

        elif event == "-ADD-" or event == "Submit":
            if values["-URL-"]:
                try:
                    get_playlist_links(values["-URL-"])
                    if values["-FORMAT-"] == "mp4":
                        update_table(22, "mp4", window)
                    else:
                        update_table(140, "mp3", window)

                except VideoUnavailable:
                    psg.popup("ERROR: Video is age restricted")
                except pytube.exceptions.RegexMatchError:
                    psg.popup("ERROR: Wrong URL",)
            else:
                psg.Popup("ERROR: No url detected.")

        elif event == "-CLEAR-":
            yt_playlist.clear()
            table_list.clear()
            window["-TABLE-"].update(table_list)

        elif event == "-DOWNLOAD-":
            output_format = values["-FORMAT-"]
            output_path = values["-DOWNLOAD-FOLDER-"]
            if output_format == "Video mp4":
                download_video(yt_playlist, output_path, window)
            else:
                download_audio(yt_playlist, output_path, window)

    window.close()


if __name__ == "__main__":
    main()
