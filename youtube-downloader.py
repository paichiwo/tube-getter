#!/usr/bin/env python3

# 1. Make skeleton with download feature that works
#    - update table with list of stream and resolutions
#    - when clicked create popup window asking if user wants to download (yes/no)
#      - get itags for each entry on the table and use download by itag
#
# 2. Implement mp4 to mp3 conversion if user wants to download only audio


import time
import PySimpleGUI as sg
import requests
from pytube import YouTube
from pytube.cli import on_progress

# https://youtu.be/eEQh4qvj-qo

sg.theme('black')

layout = [
    [sg.Stretch(), sg.Image("image/logo.png"), sg.Stretch()],
    [sg.Text('Enter YouTube Video URL:', size=20), sg.InputText(key='-URL-')],
    [sg.Button('Download', size=11, key="-DOWNLOAD-"),
     sg.Push(),
     sg.ProgressBar(
        max_value=100,
        orientation='h',
        border_width=1,
        size=(25, 10),
        bar_color=('#199FD0', '#FFFFFF'),
        key='-PROGRESS-BAR-')],
    [sg.Table(values=[], headings=["Title", "Resolution", "ITag"],
              auto_size_columns=True,
              justification="center",
              selected_row_colors="red on white",
              enable_events=True,
              expand_x=True,
              expand_y=True,
              key="-TABLE-")]
]

window = sg.Window('YouTube Downloader', layout,
                   size=(500, 500),
                   resizable=True)

list_of_streams = []

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == "-DOWNLOAD-":
        table = window["-TABLE-"]
        url = values["-URL-"]
        list_of_streams.clear()
        yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
        for stream in yt.streams.filter(file_extension="mp4").order_by("resolution").desc():
            list_of_streams.append([yt.title, stream.resolution, stream.itag])
            print(yt.title, stream.itag, stream.resolution, stream.itag)  # for DEBUGGING
        table.update(list_of_streams)

    if event == "-TABLE-":
        selected_row_index = values["-TABLE-"][0]
        if selected_row_index != sg.TABLE_SELECT_MODE_NONE:
            selected_row = list_of_streams[selected_row_index]
            i_tag = selected_row[2]
            choice = sg.popup_yes_no("Download?")
            if choice == "Yes":
                url = values["-URL-"]
                yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
                yt.streams.get_by_itag(i_tag).download()

window.close()
