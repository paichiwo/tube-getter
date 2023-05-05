#!/usr/bin/env python3

import time
import PySimpleGUI as sg
import requests
from pytube import YouTube
from pytube.cli import on_progress

# https://youtu.be/eEQh4qvj-qo`


def create_window():

    sg.theme('black')

    layout = [
        [sg.Push(), sg.Image("image/logo.png"), sg.Push()],
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
        [sg.Table(values=[], headings=["Title", "Resolution", "Download"],
                  col_widths=[100, 100, 100],
                  justification="left",
                  selected_row_colors="red on white",
                  enable_events=True,
                  expand_x=True,
                  expand_y=True,
                  key="-TABLE-")]
        ]

    return sg.Window('YouTube Downloader', layout,
                     size=(500, 500),
                     resizable=True)


def update_table(window, url):

    table = window["-TABLE-"]
    list_of_streams = []
    yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
    for stream in yt.streams.filter(file_extension="mp4").order_by("resolution").desc():
        list_of_streams.append([yt.title, stream.resolution, sg.Button("Download", key="-STREAM-DOWNLOAD-")])
        print(yt.title, stream.itag, stream.resolution)  # for DEBUGGING
    table.update(list_of_streams)


def youtube_downloader():

    window = create_window()

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        if event == "-DOWNLOAD-":
            url = values["-URL-"]
            update_table(window, url)

    window.close()


if __name__ == "__main__":
    youtube_downloader()
