#!/usr/bin/python3
import datetime
import threading
import pytubefix.exceptions
import urllib.error
import customtkinter as ctk
from datetime import datetime
from pytubefix import YouTube, Channel
from PIL import Image
from customtkinter import CTkFrame, CTkButton, CTkEntry, CTkLabel, CTkSwitch, CTkImage
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

        # self.get_test_data()

        """GUI Elements"""

        # FRAMES
        self.top_frame_1 = CTkFrame(self, fg_color='transparent')
        self.top_frame_2 = CTkFrame(self, fg_color='transparent')
        self.middle_frame = CTkFrame(self, fg_color='transparent')
        self.bottom_frame_1 = CTkFrame(self, fg_color='transparent')
        self.bottom_frame_2 = CTkFrame(self, fg_color='transparent')

        # TOP 1
        self.enter_url_label = CTkLabel(self.top_frame_1, text='Enter URL:')
        self.switch = CTkSwitch(self.top_frame_1, width=88, text='audio', command=self.switch_action,
                                fg_color='#2b719e', progress_color='#2b719e')
        self.settings_button = CTkButton(self.top_frame_1, image=CTkImage(Image.open(IMG_PATHS['settings'])),
                                         text='', width=40, command=self.settings_action)

        # TOP 2
        self.url_entry = CTkEntry(self.top_frame_2, border_width=1)
        self.url_entry.bind('<Return>', self.add_action)
        self.url_entry.bind('<Control-z>', self.delete_url_action)

        self.add_button = CTkButton(self.top_frame_2, text='Add', width=130, command=self.add_action) # change to add action

        # # MIDDLE
        self.table = Table(self.middle_frame, yt_links=self.yt_list, table_data=self.table_list, fg_color=('grey80', 'grey10'))

        # BOTTOM
        self.clear_button = CTkButton(self.bottom_frame_1, text='Clear', width=130, command=self.clear_action)
        self.download_button = CTkButton(self.bottom_frame_1, text='Download', width=130, command=self.download_action)

        # info for user
        self.info_for_user_frame = CTkFrame(self.bottom_frame_2, height=24, corner_radius=0)
        self.info_for_user_label = CTkLabel(self.info_for_user_frame, text='test message')
        self.dl_speed = CTkLabel(self.info_for_user_frame, text='100 kib/s')

        # draw GUI
        self.draw_gui()

        self.a = 0

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

    def simulate_progress(self):
        self.a += 0.01
        print(self.a)
        self.table.frames[0].progress_bar.set(self.a)

    def switch_action(self):
        self.table.delete_all_data_frames()
        self.table_list.clear()
        if self.dl_format == 'audio':
            self.dl_format = 'video'
            data = self.get_data_for_table(22, 'mp4')
        else:
            self.dl_format = 'audio'
            data = self.get_data_for_table(140, 'mp3')
        self.switch.configure(text=self.dl_format)
        self.update_table(data)

    def add_action(self, event=None):
        self.table_list.clear()
        self.table.delete_all_data_frames()

        url = self.url_entry.get()
        if url:
            try:
                if self.dl_format == 'audio':
                    get_links(url, self.yt_list)
                    data = self.get_data_for_table(140, 'mp3')
                else:
                    get_links(url, self.yt_list)
                    data = self.get_data_for_table(22, 'mp4')
                self.update_table(data)
            except pytubefix.exceptions.VideoUnavailable:
                self.info_for_user_label.configure(text="ERROR: Video is age restricted.")
            except pytubefix.exceptions.RegexMatchError:
                self.info_for_user_label.configure(text="ERROR: Wrong URL.")
            except (urllib.error.URLError, urllib.error.HTTPError):
                self.info_for_user_label.configure(text="ERROR: Internal error.")
        else:
            self.info_for_user_label.configure(text="No url detected.")

    def delete_url_action(self, event=None):
        self.url_entry.delete(0, 'end')

    def clear_action(self):
        self.yt_list.clear()
        self.table_list.clear()
        self.table.delete_all_data_frames()

    def download_action(self):
        def download_task():
            output_path = load_settings()
            if self.dl_format == 'audio':
                self.download_audio(self.yt_playlist, output_path)
            else:
                self.download_video(self.yt_playlist, output_path)  # Always download video if switch is off
            self.info_for_user_label.configure(text="Download complete.")

        download_thread = threading.Thread(target=download_task)
        download_thread.start()

    def settings_action(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self)
        else:
            self.settings_window.focus()

    def get_data_for_table(self, i_tag, dl_format):
        self.table_list.clear()

        for url in self.yt_list:
            yt = YouTube(url)
            try:
                stream = yt.streams.get_by_itag(i_tag)
            except (AttributeError, KeyError):
                stream = yt.streams.get_highest_resolution()

            self.table_list.append([
                yt.thumbnail_url,
                yt.title,
                Channel(yt.channel_url).channel_name,
                yt.length,
                yt.views,
                yt.publish_date,
                dl_format,
                f'{count_file_size(stream.filesize)} MB'
            ])
        return self.table_list

    def update_table(self, array):
        self.table.table_data = array
        self.table.create_list_with_data_frames()
        self.table.draw_data_frames()
        print(array)
        print(len(self.table.frames))

    # https://www.youtube.com/watch?v=afB4DlkebO8
    # https://www.youtube.com/watch?v=gKDuHIRNJSY&list=PLRNsV20DA24Gmt9C-X4CVFF4eP76KtkLq&pp=gAQBiAQB

    if getattr(sys, 'frozen', False):
        pyi_splash.close()


if __name__ == '__main__':
    tg = TubeGetter()
    tg.mainloop()
