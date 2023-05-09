#!/usr/bin/env python3

"""
This is a Python script that allows users to download videos or audios from YouTube by entering the URL of the video.
The user interface is built using PySimpleGUI library, and the video downloading functionality is implemented
using PyTube library. The script also uses requests, io, PIL, and os libraries for various purposes.

When the user enters a YouTube video URL and clicks on the "Video" or "Audio" button, the script retrieves
the available video or audio streams and displays them in a table. The user can then select a stream from the table
and click on the "Yes" in popup window to download the selected file to the "Downloads" folder.

The script also converts the thumbnail image from .jpg to .png format and resizes it to fit in the GUI.
In addition, the script changes the file extension of the downloaded audio files from .mp4 to .mp3,
as PyTube saves audio files as .mp4 files for some reason.

Overall, the script provides a simple and user-friendly way to download YouTube videos or audios.
"""

import PySimpleGUI as sg
import requests
import io
import os
from pytube import YouTube
from PIL import Image


def jpg_to_png(link):
    """ Convert .jpg to .png to properly display thumbnail in PySimpleGUI """
    response = requests.get(link)
    image = Image.open(io.BytesIO(response.content))
    image.thumbnail((250, 140))
    file_path = os.path.join("Downloads", "thumb.png")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    image.save(file_path, "PNG")
    return file_path


def change_extension():
    """ Changes .mp4 to .mp3 extension for downloaded audio files (PyTube for some reason saves audio as .mp4) """
    for f_name in os.listdir("Downloads"):
        if f_name.endswith(".mp4"):
            os.rename(os.path.join("Downloads", f_name), os.path.join("Downloads", f"{f_name.rsplit('.', 1)[0]}.mp3"))


def count_size():
    """ Count the streams file size """
    return round(stream.filesize / (1024 * 1024), 1)


def download():
    """ Download chosen file form the table"""
    choice = sg.popup_yes_no("Download?", font=font_used)
    if choice == "Yes":
        url = values["-URL-"]
        yt = YouTube(url, use_oauth=True, allow_oauth_cache=True,
                     on_progress_callback=progress_check, on_complete_callback=on_complete)
        if not os.path.exists("Downloads"):
            os.mkdir("Downloads")
        yt.streams.get_by_itag(i_tag).download("Downloads/")


def progress_check(stream, chunk, bytes_remaining):
    """ Display progress status in the [-PROGRESS-BAR-] """
    progress_amount = 100 - round(bytes_remaining / stream.filesize * 100)
    window["-PROGRESS-BAR-"].update(progress_amount, bar_color=("red", "white"))


def on_complete(stream, file_path):
    """ Clear the progress bar and display message when download completed """
    window["-PROGRESS-BAR-"].update(0, bar_color=("white", "white"))
    sg.popup("Done!")


# Application layout
font_used = ("Tahoma", 9)

sg.theme("black")

layout = [
    [sg.Stretch(), sg.Image("image/logo.png"), sg.Stretch()],
    [sg.VPush()],
    [sg.Stretch(), sg.Image("image/dummy_thumb.png", key="-THUMBNAIL-"), sg.Stretch()],
    [sg.VPush()],
    [sg.Text("Video URL:", font=font_used)],
    [sg.Input(size=60, enable_events=True, key="-URL-")],
    [sg.Button("Video", font=font_used, size=10, key="-VIDEO-"),
     sg.Button("Audio", font=font_used, size=10, key="-AUDIO-")],
    [sg.Table(values=[], headings=["Title", "Resolution", "Size", "Tag"],
              col_widths=[33, 7, 8, 4], auto_size_columns=False, justification="center", enable_events=True,
              font=font_used, selected_row_colors="red on white", expand_x=True, expand_y=True, key="-TABLE-")],
    [sg.ProgressBar(max_value=100, orientation='h', border_width=1, size=(25, 7),
                    bar_color=("red", "white"), expand_x=True, key='-PROGRESS-BAR-')],
]

window = sg.Window("YouTube Downloader by paichiwo", layout,
                   element_justification="center", size=(520, 520), resizable=True)

list_of_streams = []

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

    if event == "-VIDEO-":
        # Update the table with Video streams
        url = values["-URL-"]
        if url:
            list_of_streams.clear()
            yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
            for stream in yt.streams.filter(file_extension="mp4").order_by("resolution").desc():
                list_of_streams.append([yt.title, stream.resolution, f"{count_size()} MB", stream.itag])
            window["-TABLE-"].update(list_of_streams)
            # Get thumbnail
            thumbnail_string = jpg_to_png(yt.thumbnail_url)
            window["-THUMBNAIL-"].update(thumbnail_string)
        else:
            sg.Popup("ERROR: No url detected.", font=font_used)

    if event == "-AUDIO-":
        # Update the table with Audio streams
        url = values["-URL-"]
        if url:
            list_of_streams.clear()
            yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
            for stream in yt.streams.filter(only_audio=True).order_by("abr").desc():
                list_of_streams.append([yt.title, stream.abr, f"{count_size()} MB", stream.itag])
            window["-TABLE-"].update(list_of_streams)
            # Get thumbnail
            thumbnail_string = jpg_to_png(yt.thumbnail_url)
            window["-THUMBNAIL-"].update(thumbnail_string)
        else:
            sg.Popup("ERROR: No url detected.", font=font_used)

    if event == "-TABLE-":
        try:
            selected_row_index = values["-TABLE-"][0]
        except IndexError:
            continue
        selected_row = list_of_streams[selected_row_index]
        audio_tags = [139, 140, 249, 250, 251]
        i_tag = selected_row[3]
        # Download Video
        if i_tag not in audio_tags:
            download()
            os.remove("Downloads/thumb.png")
        # Download Audio
        if i_tag in audio_tags:
            download()
            change_extension()
            os.remove("Downloads/thumb.png")
window.close()
