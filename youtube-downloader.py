import PySimpleGUI as sg
from pytube import YouTube
from pytube.cli import on_progress
import requests

sg.theme('LightGrey3')

layout = [
    [sg.Text('Enter YouTube Video URL:', size=20), sg.InputText(key='url')],
    [sg.Button('Download', size=10), sg.Push(), sg.ProgressBar(
        max_value=100,
        orientation='h',
        border_width=1,
        size=(25, 25),
        bar_color=('#199FD0', '#FFFFFF'),
        key='PRG')]
    ]
window = sg.Window('YouTube Downloader', layout)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == 'Download':
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
                with open('video', 'wb') as f:
                    for chunk in req.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
                        bytes_read += len(chunk)
                        percent_complete = int(bytes_read / content_size * 100)
                        window['PRG'].update(percent_complete)
                sg.Popup('Download Complete', 'Video downloaded successfully!')
        except Exception as e:
            sg.PopupError(f'An error occurred while downloading the video: {str(e)}')
            print(e)

window.close()
