#!/usr/bin/env python3

import time
import PySimpleGUI as sg
import requests
from pytube import YouTube
from pytube.cli import on_progress

sg.theme('LightGrey3')

layout = [
    [sg.Text('Enter YouTube Video URL:', size=20), sg.InputText(key='url')],
    [sg.Button('Download mp4', size=11, key="MP4"),
     sg.Button("Download mp3", size=11, key="MP3"),
     sg.Push(),
     sg.ProgressBar(
        max_value=100,
        orientation='h',
        border_width=1,
        size=(25, 25),
        bar_color=('#199FD0', '#FFFFFF'),
        key='PRG')],
    [sg.Text('Download Speed: ', key='speed')],
    ]
window = sg.Window('YouTube Downloader', layout)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == 'MP3':
        video_url = values['url']
        try:
            yt = YouTube(video_url, use_oauth=True,
                         allow_oauth_cache=True,
                         on_progress_callback=on_progress)
            stream = yt.streams.filter(only_audio=True, abr="128kbps")
            if stream:
                req = requests.get(stream.url, stream=True)
                content_size = int(req.headers.get('Content-Length'))
                chunk_size = 1024
                bytes_read = 0
                start_time = time.time()
                file_name = f"{yt.title}.mp3"
                with open(file_name, 'wb') as f:
                    for chunk in req.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
                        bytes_read += len(chunk)
                        percent_complete = int(bytes_read / content_size * 100)
                        window['PRG'].update(percent_complete)
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 0:
                            download_speed = round(bytes_read / (1024 * elapsed_time), 2)
                            window['speed'].update(f"Download Speed: {download_speed} KB/s")
                sg.Popup('Download Complete', 'Audio downloaded successfully!')
        except Exception as e:
            sg.PopupError(f'An error occurred while downloading the video: {str(e)}')
            print(e)

    if event == "MP4":
        video_url = values['url']
        try:
            yt = YouTube(video_url, use_oauth=True,
                         allow_oauth_cache=True,
                         on_progress_callback=on_progress)
            stream = yt.streams.filter(progressive=True,
                                       file_extension='mp4'
                                       ).order_by('resolution').desc().first()
            if stream:
                req = requests.get(stream.url, stream=True)
                content_size = int(req.headers.get('Content-Length'))
                chunk_size = 1024
                bytes_read = 0
                start_time = time.time()
                file_name = f"{yt.title}.mp4"
                with open(file_name, 'wb') as f:
                    for chunk in req.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
                        bytes_read += len(chunk)
                        percent_complete = int(bytes_read / content_size * 100)
                        window['PRG'].update(percent_complete)
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 0:
                            download_speed = round(bytes_read / (1024 * elapsed_time), 2)
                            window['speed'].update(f"Download Speed: {download_speed} KB/s")
                sg.Popup('Download Complete', 'Video downloaded successfully!')
        except Exception as e:
            sg.PopupError(f'An error occurred while downloading the video: {str(e)}')
            print(e)

window.close()
