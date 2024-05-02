#!/usr/bin/python3
import threading
import pytubefix.exceptions
import urllib.error
import customtkinter as ctk
from datetime import datetime
from pytubefix import YouTube, Channel
from customtkinter import CTkFrame, CTkButton, CTkEntry, CTkLabel, CTkSwitch
from src.config import VERSION, IMG_PATHS
from src.helpers import *
from src.settings_win import SettingsWindow
from src.info_frame import Table

if getattr(sys, 'frozen', False):
    import pyi_splash


class TubeGetter(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.iconbitmap(bitmap=IMG_PATHS['icon'])
        self.title(f'Tube Getter v{VERSION}')
        center_window(self, 1000, 600)
        self.minsize(500, 400)  # adjust later

        self.settings_window = None

        self.yt_list = []
        self.table_list = []
        self.download_start_time = datetime.now()
        self.dl_format = 'audio'

        # ------------------ GUI WIDGETS -------------------

        # FRAMES
        self.top_frame_1 = CTkFrame(self, fg_color='transparent')
        self.top_frame_2 = CTkFrame(self, fg_color='transparent')
        self.middle_frame = CTkFrame(self, fg_color='transparent')
        self.bottom_frame_1 = CTkFrame(self, fg_color='transparent')
        self.bottom_frame_2 = CTkFrame(self, fg_color='transparent')

        # TOP FRAME 1
        self.enter_url_label = CTkLabel(self.top_frame_1, text='Enter URL:')
        self.switch = CTkSwitch(self.top_frame_1, width=88, text='audio', command=self.switch_action,
                                fg_color='#2b719e', progress_color='#2b719e')
        self.settings_button = CTkButton(self.top_frame_1, image=imager(IMG_PATHS['settings'], 20, 20),
                                         text='', width=40, command=self.settings_action)

        # TOP FRAME 2
        self.url_entry = CTkEntry(self.top_frame_2, border_width=1)
        self.url_entry.bind('<Return>', self.add_action)
        self.url_entry.bind('<Control-z>', self.delete_url_action)

        self.add_button = CTkButton(self.top_frame_2, text='Add', width=130, command=self.add_action)

        # MIDDLE FRAME
        self.table = Table(self.middle_frame, yt_links=self.yt_list, table_data=self.table_list,
                           fg_color=('grey80', 'grey10'))

        # BOTTOM UPPER FRAME
        self.clear_button = CTkButton(self.bottom_frame_1, text='Clear', width=130, command=self.clear_action)
        self.download_button = CTkButton(self.bottom_frame_1, text='Download', width=130, command=self.download_action)

        # BOTTOM LOWER FRAME
        self.info_for_user_frame = CTkFrame(self.bottom_frame_2, height=24, corner_radius=0)
        self.info_for_user_label = CTkLabel(self.info_for_user_frame, text='')
        self.dl_speed = CTkLabel(self.info_for_user_frame, text='0 KiB/s')

        # draw GUI
        self.draw_gui()

    def draw_gui(self):
        self.top_frame_1.pack(fill='x')
        self.top_frame_1.columnconfigure(0, weight=10)
        self.enter_url_label.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        self.switch.grid(row=0, column=1, sticky='e')
        self.settings_button.grid(row=0, column=2, sticky='e', padx=(0, 10))

        self.top_frame_2.pack(fill='x')
        self.top_frame_2.columnconfigure(0, weight=10)
        self.url_entry.grid(row=0, column=0, columnspan=2, sticky='ew', padx=10, pady=(0, 10))
        self.add_button.grid(row=0, column=2, sticky='ew', padx=(0, 10), pady=(0, 10))

        self.middle_frame.pack(fill='both', expand=True)
        self.middle_frame.columnconfigure(0, weight=1)
        self.table.pack(fill='both', expand=True, padx=10)

        self.bottom_frame_1.pack(fill='x', padx=10, pady=10)
        self.clear_button.pack(anchor='w', side='left')
        self.download_button.pack(anchor='w', side='right')

        self.bottom_frame_2.pack(fill='x', side='bottom')
        self.info_for_user_frame.pack(fill='x')
        self.info_for_user_label.pack(side='left', fill='x', padx=10)
        self.dl_speed.pack(side='right', fill='x', padx=10)

    def switch_action(self):
        self.table.delete_all_data_frames()
        self.table_list.clear()
        if self.dl_format == 'audio':
            self.dl_format = 'video'
        else:
            self.dl_format = 'audio'
        data = self.get_data_for_table()
        self.switch.configure(text=self.dl_format)
        self.update_table(data)

    def add_action(self):
        self.table_list.clear()
        self.table.delete_all_data_frames()

        url = self.url_entry.get()
        if url:
            try:
                get_links(url, self.yt_list)
                data = self.get_data_for_table()
                self.update_table(data)
            except pytubefix.exceptions.VideoUnavailable:
                self.info_for_user_label.configure(text='ERROR: Video is age restricted.')
            except (pytubefix.exceptions.RegexMatchError, KeyError):
                self.info_for_user_label.configure(text='ERROR: Wrong URL.')
            except (urllib.error.URLError, urllib.error.HTTPError):
                self.info_for_user_label.configure(text='ERROR: Internal error.')
        else:
            self.info_for_user_label.configure(text='No url detected.')

    def delete_url_action(self):
        self.url_entry.delete(0, 'end')

    def clear_action(self):
        self.yt_list.clear()
        self.table_list.clear()
        self.table.delete_all_data_frames()

    def download_action(self):
        def download_task():
            for data_frame in self.table.frames:
                data_frame.delete_btn.configure(state='disabled')

            output_path = load_settings()
            if self.dl_format == 'audio':
                self.download_audio(self.yt_list, output_path)
            else:
                self.download_video(self.yt_list, output_path)
            self.info_for_user_label.configure(text='Download complete.')

        download_thread = threading.Thread(target=download_task)
        download_thread.start()

    def settings_action(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self)
        else:
            self.settings_window.focus()

    def get_data_for_table(self):
        self.table_list.clear()

        for url in self.yt_list:
            yt = YouTube(url)
            try:
                stream = yt.streams.get_by_itag(
                    140) if self.dl_format == 'audio' else yt.streams.get_highest_resolution()
                file_format = 'mp3' if self.dl_format == 'audio' else 'mp4'
                self.table_list.append([
                    yt.thumbnail_url,
                    yt.title,
                    Channel(yt.channel_url).channel_name,
                    yt.length,
                    yt.views,
                    yt.publish_date,
                    file_format,
                    count_file_size(stream.filesize)
                ])
            except (AttributeError, KeyError):
                self.table_list.append([
                    yt.thumbnail_url,
                    yt.title,
                    Channel(yt.channel_url).channel_name,
                    yt.length,
                    yt.views,
                    yt.publish_date,
                    'mp4',
                    count_file_size(yt.streams.get_highest_resolution().filesize)
                ])
        return self.table_list

    def update_table(self, array):
        self.table.table_data = array
        self.table.create_list_with_data_frames()
        self.table.draw_data_frames()

    def download_video(self, yt_list, output_path):
        for index, link in enumerate(yt_list):
            yt = YouTube(link, on_progress_callback=self.progress_callback)
            yt_stream = yt.streams.get_highest_resolution()
            try:
                yt_stream.download(output_path=output_path, filename=yt_stream.default_filename)
                self.dl_speed.configure(text='0 KiB/s')

                if os.path.exists(os.path.join(load_settings(), yt_stream.default_filename)):
                    self.table.frames[index].delete_btn.configure(image=imager(IMG_PATHS['folder'], 24, 24),
                                                                  command=open_downloads_folder, state='normal')
                    self.info_for_user_label.configure(text='File already downloaded.')

            except (PermissionError, RuntimeError):
                self.info_for_user_label.configure(text='ERROR: Permission Error.')

    def download_audio(self, yt_list, output_path):
        pass

    def progress_callback(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = bytes_downloaded / total_size

        elapsed_time = (datetime.now() - self.download_start_time).total_seconds()
        download_speed = bytes_downloaded / (1024 * elapsed_time)
        for i, item in enumerate(self.table_list):
            if item[1] == stream.title:
                self.table.frames[i].progress_bar.set(percentage)
                self.table.frames[i].change_delete_btn()
                self.dl_speed.configure(text=format_download_speed_string(download_speed))

    # long video - https://www.youtube.com/watch?v=AsTagX5tG4E
    # https://www.youtube.com/watch?v=afB4DlkebO8
    # https://www.youtube.com/watch?v=gKDuHIRNJSY&list=PLRNsV20DA24Gmt9C-X4CVFF4eP76KtkLq&pp=gAQBiAQB

    if getattr(sys, 'frozen', False):
        pyi_splash.close()


if __name__ == '__main__':
    tg = TubeGetter()
    tg.mainloop()
