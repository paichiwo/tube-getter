#!/usr/bin/env python3

import os
import sys
import webbrowser
import PySimpleGUI as psg
import data
from pytube import YouTube
from pytube import Playlist
from pytube.exceptions import VideoUnavailable

# sort font problem

# https://www.youtube.com/playlist?list=PLRNsV20DA24Gmt9C-X4CVFF4eP76KtkLq


def resource_path(relative_path):
    """PyInstaller requirement,
    Get an absolute path to resource, works for dev and for PyInstaller."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


version = "1.1"
themes = ["LightGrey", "DarkGrey4"]
colors = ["#FBFBFB", "#52524E"]
font_path = resource_path("./fonts/Manrope-Regular.ttf")
font = (font_path, 10)
yt_playlist = []
table_list = []


def settings_popup():
    """Creates a new window with app information / settings."""
    layout = [[psg.Image(filename=resource_path("./images/youtube.png"))],
              [psg.Text(f"YOUTUBE GETTER v{version}\nby Paichiwo\n2023\n\n{data.popup_message}",
                        justification='c')],
              [psg.Image(filename=resource_path("./images/github.png")),
               psg.Text("GitHub",
                        font=(font, 10, "underline"),
                        enable_events=True)],
              [psg.Button('OK')]]
    window = psg.Window("Information",
                        layout,
                        element_justification='c',
                        grab_anywhere=True,
                        finalize=True,
                        icon=resource_path("./images/youtube.png"))

    event, values = window.read()
    if event in "GitHub":
        webbrowser.open(data.github_link)
    window.close()


def count_file_size(size_data):
    """Count the stream file sizes."""
    return round(size_data / (1024 * 1024), 1)


def download_video(playlist, output_path):
    """Download video stream - highest resolution."""
    for url in playlist:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        stream.download(output_path=output_path, filename=stream.default_filename)


def download_audio(playlist, output_path):
    """Download audio stream."""
    for url in playlist:
        yt = YouTube(url)
        stream = yt.streams.get_audio_only()
        if stream.mime_type == "audio/mp4":
            filename = stream.default_filename.rsplit(".", 1)[0] + ".mp3"
        else:
            filename = stream.default_filename
        stream.download(output_path=output_path, filename=filename)


def create_window(theme):
    """Application layout for PySimpleGUI."""
    psg.theme(theme)

    layout = [
        [psg.Push(),
         psg.Button(image_filename=resource_path("./images/close.png"),
                    button_color=colors[0],
                    border_width=0,
                    k="-CLOSE-")],

        [psg.Text("Enter URLs:", font=font),
         psg.Push()],

        [psg.Input("",
                   focus=True,
                   background_color="light grey",
                   text_color="black",
                   expand_x=True,
                   border_width=0,
                   pad=5,
                   k="-URL-"),
         psg.Button("OK",
                    k="-OK-"),
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

        [psg.Multiline(autoscroll=True,
                       background_color="light grey",
                       text_color="black",
                       size=(10, 10),
                       expand_x=True,
                       border_width=0,
                       pad=5,
                       k="-LINKS-")],

        [psg.Image(filename=resource_path("./images/icons_black/folder.png")),
         psg.Input(background_color="light grey",
                   text_color="black",
                   k="-DOWNLOAD-FOLDER-"),
         psg.FolderBrowse("•••",
                          button_color=("black", colors[0])),
         psg.Push(),
         psg.Text("Format"),
         psg.Combo(values=["mp4", "mp3"],
                   k="-FORMAT-"),
         psg.Push(),
         psg.Button("Add",
                    k="-ADD-")
         ],

        [psg.Table(values=[],
                   headings=["Title", "Ext", "Size", "Complete", "Speed", "Status"],
                   col_widths=[33, 7, 8, 6, 8, 12],
                   auto_size_columns=False,
                   justification="c",
                   background_color="light grey",
                   text_color="black",
                   size=(10, 10),
                   expand_x=True,
                   border_width=0,
                   pad=5,
                   k="-TABLE-")],

        [psg.Push(),
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

        if event == "-THEME-":
            theme = themes[themes_counter % len(themes)]
            color = colors[themes_counter % len(themes)]
            window.close()
            window = create_window(theme)
            window["-SETTINGS-"].update(button_color=color)
            window["-THEME-"].update(button_color=color)
            window["-CLOSE-"].update(button_color=color)
            themes_counter += 1

        if event == "-SETTINGS-":
            settings_popup()

        if event == "-OK-":
            if "playlist" in values["-URL-"]:
                p = Playlist(values["-URL-"])
                for url in p.video_urls:
                    yt_playlist.append(url)
                window["-LINKS-"].update("\n".join(yt_playlist))
            else:
                yt_playlist.append(values["-URL-"])
                window["-LINKS-"].update("\n".join(yt_playlist))

        if event == "-ADD-":
            if values["-FORMAT-"]:
                for url in yt_playlist:
                    yt = YouTube(url)
                    table_list.append(
                        [yt.streams.get_highest_resolution().title,
                         values["-FORMAT-"],
                         f"{count_file_size(yt.streams.get_highest_resolution().filesize)} MB",
                         "0 %",
                         "13.4 Mb/s",
                         "testing"])
                window["-TABLE-"].update(table_list)
            else:
                print("no format selected.")

        if event == "-DOWNLOAD-":
            output_format = values["-FORMAT-"]
            output_path = values["-DOWNLOAD-FOLDER-"]
            if output_format == "Video mp4":
                download_video(yt_playlist, output_path)
            else:
                download_audio(yt_playlist, output_path)

    window.close()


if __name__ == "__main__":
    main()
