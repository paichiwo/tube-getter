#!/usr/bin/env python3

"""
YouTube Downloader allows users to download videos or audios from YouTube.
The user interface is built using PySimpleGUI library, and the video downloading
functionality is implemented using PyTube library.
Overall, the script provides a simple and user-friendly way to download YouTube videos or audios.
"""

import PySimpleGUI as sg
import requests
import io
import os
from pytube import YouTube
from PIL import Image

font_used = ("Tahoma", 9)


def jpg_to_png(url):
    """ Convert .jpg to .png to properly display thumbnail in PySimpleGUI """
    response = requests.get(url)
    image = Image.open(io.BytesIO(response.content))
    image.thumbnail((300, 168))
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
    """ Count the stream file sizes """
    return round(stream_data.filesize / (1024 * 1024), 1)


def download():
    """ Download chosen file from the table"""
    choice = sg.popup_yes_no("Download?", font=font_used)
    if choice == "Yes":
        url = values["-URL-"]
        yt = YouTube(url, on_progress_callback=progress_check, on_complete_callback=on_complete)
        if not os.path.exists("Downloads"):
            os.mkdir("Downloads")
        stream = yt.streams.get_by_itag(i_tag)
        if stream.mime_type == "audio/mp4":
            # Set a suffix for audio files
            filename = stream.default_filename.rsplit(".", 1)[0] + ".mp3"
        else:
            filename = stream.default_filename
        stream.download(output_path="Downloads", filename=filename)


def progress_check(stream, chunk, bytes_remaining):
    """ Display progress status in the [-PROGRESS-BAR-] """
    progress_amount = 100 - round(bytes_remaining / stream.filesize * 100)
    window["-PROGRESS-BAR-"].update(progress_amount, bar_color=("red", "white"))


def on_complete(stream, file_path):
    """ Clear the progress bar and display message when download completed """
    window["-PROGRESS-BAR-"].update(0, bar_color=("white", "white"))
    sg.popup("Done!")


def create_window():
    """Application layout."""
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
        [sg.ProgressBar(max_value=100, orientation='h', border_width=0, size=(25, 2),
                        bar_color=("red", "white"), expand_x=True, key='-PROGRESS-BAR-')],
    ]

    return sg.Window("YouTube Downloader by paichiwo", layout,
                     element_justification="center", size=(520, 520), resizable=True)


list_of_streams = []
window = create_window()

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

    if event == "-VIDEO-":
        link = values["-URL-"]
        if link:
            list_of_streams.clear()
            yt_data = YouTube(link, use_oauth=False)  # use_oauth=True, allow_oauth_cache=True
            for stream_data in yt_data.streams.filter(file_extension="mp4").order_by("resolution").desc():
                list_of_streams.append([yt_data.title, stream_data.resolution, f"{count_size()} MB", stream_data.itag])
            window["-TABLE-"].update(list_of_streams)

            thumbnail_string = jpg_to_png(yt_data.thumbnail_url)
            window["-THUMBNAIL-"].update(thumbnail_string)
        else:
            sg.Popup("ERROR: No url detected.", font=font_used)

    if event == "-AUDIO-":
        link = values["-URL-"]
        if link:
            list_of_streams.clear()
            yt_data = YouTube(link)  # use_oauth=True, allow_oauth_cache=True
            for stream_data in yt_data.streams.filter(only_audio=True).order_by("abr").desc():
                list_of_streams.append([yt_data.title, stream_data.abr, f"{count_size()} MB", stream_data.itag])
            window["-TABLE-"].update(list_of_streams)

            thumbnail_string = jpg_to_png(yt_data.thumbnail_url)
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
            try:
                os.remove("Downloads/thumb.png")
            except FileNotFoundError:
                continue
        # Download Audio
        if i_tag in audio_tags:
            download()
            try:
                os.remove("Downloads/thumb.png")
            except FileNotFoundError:
                continue
window.close()
