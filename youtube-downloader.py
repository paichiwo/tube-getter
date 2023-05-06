#!/usr/bin/env python3

# 2. Implement mp4 to mp3 conversion if user wants to download only audio

import time
import PySimpleGUI as sg
import requests
import io
import os
from pytube import YouTube
from PIL import Image

# https://youtu.be/eEQh4qvj-qo


def jpg_to_png(url, title):
    response = requests.get(url)
    image = Image.open(io.BytesIO(response.content))
    max_size = (200, 112)
    image.thumbnail(max_size)
    if not os.path.exists("Download/thumbnails"):
        os.mkdir("Download")
        os.mkdir("Download/thumbnails")
    file_path = os.path.join("Download/thumbnails/", "thumb.png")
    image.save(file_path, "PNG")
    return file_path


def progress_check(stream, chunk, bytes_remaining):
    progress_amount = 100 - round(bytes_remaining / stream.filesize * 100)
    window['-PROGRESS-BAR-'].update(progress_amount,
                                    bar_color=('red', 'white'))


def on_complete(stream, file_path):
    window['-PROGRESS-BAR-'].update(0,  bar_color=('white', 'white'))
    sg.popup("Done!")


sg.theme('black')

layout = [
    [sg.Stretch(), sg.Image("image/logo.png"), sg.Stretch()],
    [sg.Stretch(), sg.Image("image/dummy_thumb.png", key="-THUMBNAIL-"), sg.Stretch()],
    [sg.Text('Enter YouTube Video URL:', size=20), sg.InputText(enable_events=True, key='-URL-')],
    [sg.Button('Download', size=11, key="-DOWNLOAD-"),
     sg.Push(),
     sg.ProgressBar(max_value=100,
                    orientation='h',
                    border_width=1,
                    size=(25, 10),
                    bar_color=('#199FD0', '#FFFFFF'),
                    key='-PROGRESS-BAR-')],
    [sg.Table(values=[], headings=["Title", "Resolution", "Size", "ITag"],
              col_widths=[36, 6, 8, 4],
              auto_size_columns=False,
              justification="center",
              selected_row_colors="red on white",
              enable_events=True,
              expand_x=True,
              expand_y=True,
              key="-TABLE-")]
]

window = sg.Window('YouTube Downloader', layout,
                   size=(600, 500),
                   resizable=True)

list_of_streams = []

while True:
    event, values = window.read(timeout=0.0005)

    if event == sg.WIN_CLOSED:
        break

    if event == "-DOWNLOAD-":
        # update the table
        table = window["-TABLE-"]
        url = values["-URL-"]
        if url:
            list_of_streams.clear()
            yt = YouTube(url, use_oauth=True,
                         allow_oauth_cache=True)
            for stream in yt.streams.filter(file_extension="mp4").order_by("resolution").desc():
                list_of_streams.append([yt.title,
                                        stream.resolution,
                                        f"{round(stream.filesize / 1048576, 1)} MB",
                                        stream.itag])
                print(yt.title, stream.resolution, stream.itag)  # for DEBUGGING
            table.update(list_of_streams)
            # get thumbnail
            thumbnail_string = jpg_to_png(yt.thumbnail_url, yt.title)
            window["-THUMBNAIL-"].update(thumbnail_string)
        else:
            sg.Popup("ERROR: No url detected.")

    if event == "-TABLE-":
        selected_row_index = values["-TABLE-"][0]
        if selected_row_index != sg.TABLE_SELECT_MODE_NONE:
            selected_row = list_of_streams[selected_row_index]
            i_tag = selected_row[3]
            choice = sg.popup_yes_no("Download?")
            if choice == "Yes":
                url = values["-URL-"]
                yt = YouTube(url, use_oauth=True,
                             allow_oauth_cache=True,
                             on_progress_callback=progress_check,
                             on_complete_callback=on_complete)
                if not os.path.exists("Downloads"):
                    os.mkdir("Downloads")
                yt.streams.get_by_itag(i_tag).download("Downloads/")

window.close()
