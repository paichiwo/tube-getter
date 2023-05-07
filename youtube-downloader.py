#!/usr/bin/env python3

import PySimpleGUI as sg
import requests
import io
from pytube import YouTube
from PIL import Image
from moviepy.editor import *

# https://youtu.be/eEQh4qvj-qo


def jpg_to_png(link):
    response = requests.get(link)
    image = Image.open(io.BytesIO(response.content))
    image.thumbnail((250, 140))
    if not os.path.exists("Downloads"):
        os.mkdir("Downloads")
    file_path = os.path.join("Downloads/", "thumb.png")
    image.save(file_path, "PNG")
    return file_path


def change_extension():
    for filename in os.listdir("Downloads/"):
        if filename.endswith(".mp4"):
            filename_parts = filename.split(".")
            new_filename = f"{filename_parts[0]}.mp3"
            os.rename(os.path.join("Downloads/", filename), os.path.join("Downloads/", new_filename))


def count_size():
    return round(stream.filesize / 1048576, 1)


def download():
    choice = sg.popup_yes_no("Download?", font=font_used)
    if choice == "Yes":
        url = values["-URL-"]
        yt = YouTube(url, use_oauth=True, allow_oauth_cache=True,
                     on_progress_callback=progress_check, on_complete_callback=on_complete)
        if not os.path.exists("Downloads"):
            os.mkdir("Downloads")
        yt.streams.get_by_itag(i_tag).download("Downloads/")


def progress_check(stream, chunk, bytes_remaining):
    progress_amount = 100 - round(bytes_remaining / stream.filesize * 100)
    window['-PROGRESS-BAR-'].update(progress_amount, bar_color=('red', 'white'))


def on_complete(stream, file_path):
    window['-PROGRESS-BAR-'].update(0, bar_color=('white', 'white'))
    sg.popup("Done!")


# Application layout
font_used = ("Tahoma", 9)

sg.theme('black')

layout = [
    [sg.Stretch(), sg.Image("image/logo.png"), sg.Stretch()],
    [sg.Stretch(), sg.Image("image/dummy_thumb.png", key="-THUMBNAIL-"), sg.Stretch()],
    [sg.VPush()],
    [sg.Text("Video URL:", font=font_used)],
    [sg.Input(size=60, enable_events=True, key="-URL-")],
    [sg.Button("Video", font=font_used, size=10, key="-VIDEO-"),
     sg.Button("Audio", font=font_used, size=10, key="-AUDIO-")],
    [sg.Table(values=[], headings=["Title", "Resolution", "Size", "ITag"],
              col_widths=[33, 7, 8, 4], auto_size_columns=False, justification="center", enable_events=True,
              font=font_used, selected_row_colors="red on white", expand_x=True, expand_y=True, key="-TABLE-")],
    [sg.ProgressBar(max_value=100, orientation='h', border_width=1, size=(25, 7),
                    bar_color=('#199FD0', '#FFFFFF'), expand_x=True, key='-PROGRESS-BAR-')],
    # [sg.VPush()]
]

window = sg.Window("YouTube Downloader by paichiwo", layout,
                   element_justification="center", size=(520, 520), resizable=True)

list_of_streams = []

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == "-VIDEO-":
        # update the table
        url = values["-URL-"]
        if url:
            list_of_streams.clear()
            yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
            for stream in yt.streams.filter(file_extension="mp4").order_by("resolution").desc():
                list_of_streams.append([yt.title, stream.resolution, f"{count_size()} MB", stream.itag])
            window["-TABLE-"].update(list_of_streams)
            # get thumbnail
            thumbnail_string = jpg_to_png(yt.thumbnail_url)
            window["-THUMBNAIL-"].update(thumbnail_string)
        else:
            sg.Popup("ERROR: No url detected.", font=font_used)

    if event == "-AUDIO-":
        # update the table
        url = values["-URL-"]
        if url:
            list_of_streams.clear()
            yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
            for stream in yt.streams.filter(only_audio=True).order_by("abr").desc():
                list_of_streams.append([yt.title, stream.abr, f"{count_size()} MB", stream.itag])
            window["-TABLE-"].update(list_of_streams)
            # get thumbnail
            thumbnail_string = jpg_to_png(yt.thumbnail_url)
            window["-THUMBNAIL-"].update(thumbnail_string)
        else:
            sg.Popup("ERROR: No url detected.", font=font_used)

    if event == "-TABLE-":
        selected_row_index = values["-TABLE-"][0]

        if selected_row_index != sg.TABLE_SELECT_MODE_NONE:
            selected_row = list_of_streams[selected_row_index]
            audio_tags = [139, 140, 249, 250, 251]
            i_tag = selected_row[3]

            if i_tag not in audio_tags:
                download()
                os.remove("Downloads/thumb.png")

            if i_tag in audio_tags:
                download()
                change_extension()
                os.remove("Downloads/thumb.png")
window.close()
