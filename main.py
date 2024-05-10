#!/usr/bin/python3
import os
import sys
import threading
import pytubefix.exceptions
import urllib.error
import customtkinter as ctk
from datetime import datetime
from pytubefix import YouTube, Channel
from pychute import PyChute
from customtkinter import CTkFrame, CTkButton, CTkEntry, CTkLabel, CTkSwitch
from src.config import VERSION, IMG_PATHS
from src.helpers import (center_window, imager, get_links, format_file_size, load_settings, handle_audio_extension,
                         open_downloads_folder, format_dl_speed_string, convert_time, convert_date, convert_to_mp3,
                         format_filename)
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
        self.provider = 'youtube'

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
        self.switch.configure(text=self.dl_format)

        if self.provider == 'youtube':
            data = self.get_yt_data_for_table()
            self.update_table(data)
        elif self.provider == 'bitchute':
            data = self.get_bc_data_for_table()
            self.update_table(data)

    def add_action(self, event=None):
        self.info_for_user_label.configure(text='')
        self.table_list.clear()
        self.add_button.configure(state='disabled')

        def add_threaded():
            url = self.url_entry.get()
            if url:
                if 'youtube' in url:
                    self.provider = 'youtube'
                    try:
                        get_links(url, self.yt_list)
                        self.info_for_user_label.configure(text='Please wait, gathering data...')
                        data = self.get_yt_data_for_table()
                        if data:
                            self.table.delete_all_data_frames()
                            self.update_table(data)
                            self.add_button.configure(state='normal')
                            self.info_for_user_label.configure(text='Ready.')

                    except pytubefix.exceptions.VideoUnavailable:
                        self.info_for_user_label.configure(text='ERROR: Video is age restricted.')
                        self.add_button.configure(state='normal')
                    except (pytubefix.exceptions.RegexMatchError, KeyError):
                        self.info_for_user_label.configure(text='ERROR: Wrong URL.')
                        self.add_button.configure(state='normal')
                    except urllib.error.URLError:
                        self.info_for_user_label.configure(text='ERROR: Internal error.')
                        self.add_button.configure(state='normal')

                elif 'bitchute' in url:
                    self.provider = 'bitchute'

                    try:
                        self.yt_list.clear()
                        get_links(url, self.yt_list)
                        self.info_for_user_label.configure(text='Please wait, gathering data...')
                        data = self.get_bc_data_for_table()
                        if data:
                            self.table.delete_all_data_frames()
                            self.update_table(data)
                            self.add_button.configure(state='normal')
                            self.info_for_user_label.configure(text='Ready.')
                    except KeyError:
                        self.info_for_user_label.configure(text='ERROR: Wrong URL.')
                        self.add_button.configure(state='normal')
                    except urllib.error.URLError:
                        self.info_for_user_label.configure(text='ERROR: Internal error.')
                        self.add_button.configure(state='normal')
                else:
                    self.info_for_user_label.configure(text='ERROR: Wrong URL.')
                    self.add_button.configure(state='normal')
            else:
                self.info_for_user_label.configure(text='ERROR: No url detected.')
                self.add_button.configure(state='normal')

        add_thread = threading.Thread(target=add_threaded)
        add_thread.start()

    def delete_url_action(self, event=None):
        self.url_entry.delete(0, 'end')

    def clear_action(self):
        self.yt_list.clear()
        self.table_list.clear()
        self.table.delete_all_data_frames()
        self.info_for_user_label.configure(text='')

    def download_action(self):
        def download_task():

            for data_frame in self.table.frames:
                data_frame.delete_btn.configure(state='disabled')

            if self.provider == 'youtube':
                self.download_yt()
            elif self.provider == 'bitchute':
                self.download_bc()

        download_thread = threading.Thread(target=download_task)
        download_thread.start()

    def settings_action(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self)
        else:
            self.settings_window.focus()

    def get_yt_data_for_table(self):
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
                    convert_time(yt.length),
                    yt.views,
                    convert_date(yt.publish_date),
                    file_format,
                    format_file_size(stream.filesize)
                ])
            except (AttributeError, KeyError):
                self.table_list.append([
                    yt.thumbnail_url,
                    yt.title,
                    Channel(yt.channel_url).channel_name,
                    convert_time(yt.length),
                    yt.views,
                    convert_date(yt.publish_date),
                    'mp4',
                    format_file_size(yt.streams.get_highest_resolution().filesize)
                ])
        return self.table_list

    def get_bc_data_for_table(self):

        pc = PyChute(self.yt_list[0])
        self.table_list.append([
            pc.thumbnail(),
            pc.title(),
            pc.channel(),
            str(pc.duration()),
            pc.views(),
            pc.publish_date().split(' ')[0],
            'mp4',
            format_file_size(pc.filesize())
        ])
        return self.table_list

    def update_table(self, array):
        self.table.table_data = array
        self.table.create_list_with_data_frames()
        self.table.draw_data_frames()

    def download_yt(self):
        filename = ''
        output_path = load_settings()

        for index, link in enumerate(self.yt_list):
            yt = YouTube(link, on_progress_callback=self.yt_progress_callback)
            if self.dl_format == 'audio':
                yt_stream = yt.streams.get_audio_only()
                filename = handle_audio_extension(yt_stream)
            else:
                yt_stream = yt.streams.get_highest_resolution()

            self.info_for_user_label.configure(text='Downloading...')

            try:
                if os.path.exists(os.path.join(load_settings(), filename)):
                    self.table.frames[index].delete_btn.configure(image=imager(IMG_PATHS['folder'], 24, 24),
                                                                  command=open_downloads_folder, state='normal')
                    self.info_for_user_label.configure(text='File already downloaded.')
                else:
                    yt_stream.download(output_path=output_path, filename=filename)
                    self.dl_speed.configure(text='0 KiB/s')
                    self.info_for_user_label.configure(text='Download complete.')

            except (PermissionError, RuntimeError):
                self.info_for_user_label.configure(text='ERROR: Permission Error.')

    def download_bc(self):
        output_path = load_settings()

        for i, link in enumerate(self.yt_list):
            pc = PyChute(url=link)
            filename = os.path.join(output_path, format_filename(pc.title()))

            # check if file exists before downloading
            if os.path.exists(filename + '.mp4'):
                self.table.frames[i].delete_btn.configure(image=imager(IMG_PATHS['folder'], 24, 24),
                                                          command=open_downloads_folder, state='normal')
                self.info_for_user_label.configure(text='File already downloaded.')
            else:

                if self.dl_format == 'audio':
                    # download
                    self.info_for_user_label.configure(text='Downloading...')
                    pc.download(filename=filename, on_progress_callback=self.bc_progress_callback)
                    self.table.frames[i].delete_btn.configure(state='disabled')

                    # convert
                    self.info_for_user_label.configure(text='Converting bitchute video to mp3 file.')
                    convert_to_mp3(f'{filename}.mp4', f'{filename}.mp3')
                    os.remove(f'{filename}.mp4')
                    self.table.frames[i].extension.configure(text='mp3')
                    self.table.frames[i].size.configure(text=f'{format_file_size(os.path.getsize(f'{filename}.mp3'))}')
                    self.table.frames[i].delete_btn.configure(image=imager(IMG_PATHS['folder'], 24, 24), width=25, height=25,
                                                              command=open_downloads_folder, state='normal')
                    # check converted file exists
                    if os.path.exists(filename + '.mp3'):
                        self.table.frames[i].delete_btn.configure(image=imager(IMG_PATHS['folder'], 24, 24),
                                                                  command=open_downloads_folder, state='normal')
                        self.dl_speed.configure(text='0 KiB/s')
                        self.info_for_user_label.configure(text='Conversion complete.')

                else:
                    self.info_for_user_label.configure(text='Downloading...')
                    pc.download(filename=filename, on_progress_callback=self.bc_progress_callback)
                    self.dl_speed.configure(text='0 KiB/s')
                    self.info_for_user_label.configure(text='Download complete.')

    def yt_progress_callback(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = bytes_downloaded / total_size

        elapsed_time = (datetime.now() - self.download_start_time).total_seconds()
        download_speed = bytes_downloaded / (1024 * elapsed_time)
        for i, item in enumerate(self.table_list):
            if item[1] == stream.title:
                self.table.frames[i].progress_bar.set(percentage)
                self.table.frames[i].change_delete_btn()
                self.dl_speed.configure(text=format_dl_speed_string(download_speed))

    def bc_progress_callback(self, count, block_size, total_size):
        percentage = min(1.0, float(count * block_size) / total_size)

        elapsed_time = (datetime.now() - self.download_start_time).total_seconds()
        download_speed = (count * block_size) / (1024 * elapsed_time)

        for i, item in enumerate(self.table_list):
            self.table.frames[i].progress_bar.set(percentage)
            self.dl_speed.configure(text=format_dl_speed_string(download_speed))

    if getattr(sys, 'frozen', False):
        pyi_splash.close()


if __name__ == '__main__':
    tg = TubeGetter()
    tg.mainloop()
