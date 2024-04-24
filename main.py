#!/usr/bin/python3

import darkdetect
import sv_ttk
import threading
import pytubefix.exceptions
import urllib.error
import customtkinter as ctk
from datetime import datetime
from pytubefix import YouTube
from PIL import Image
from customtkinter import CTkFrame, CTkButton, CTkEntry, CTkLabel, CTkSwitch, CTkImage
from tkinter import ttk, Menu, CENTER
from src.config import VERSION, IMG_PATHS
from src.helpers import *
from src.settings_win import SettingsWindow

if getattr(sys, 'frozen', False):
    import pyi_splash


class TubeGetter(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.iconbitmap(bitmap=IMG_PATHS['icon'])
        self.title(f'Tube Getter v{VERSION}')
        self.resizable(False, False)
        center_window(self, 800, 500)

        self.settings_window = None

        self.yt_playlist = []
        self.treeview_list = []
        self.download_start_time = datetime.now()
        self.dl_format = 'audio'

        # gui elements
        self.main_frame = CTkFrame(self, width=800, height=500, bg_color='transparent')

        self.enter_url_label = CTkLabel(self.main_frame, text='Enter URL:')
        self.switch = CTkSwitch(self.main_frame, text='audio', command=self.switch_action,
                                fg_color='#2b719e', progress_color='#2b719e')

        self.settings_button = CTkButton(self.main_frame, image=CTkImage(Image.open(IMG_PATHS['settings'])),
                                         text='', width=40, command=self.settings_action)

        self.url_entry = CTkEntry(self.main_frame, width=620, border_width=1)
        self.url_entry.bind('<Return>', self.add_action)
        self.url_entry.bind('<Control-z>', self.delete_url_action)

        self.add_button = CTkButton(self.main_frame, text='Add', width=130, command=self.add_action)
        self.clear_button = CTkButton(self.main_frame, text='Clear', width=130, command=self.clear_action)
        self.download_button = CTkButton(self.main_frame, text='Download', width=130, command=self.download_action)

        # treeview
        columns = ('title', 'ext', 'size', 'progress', 'speed', 'status')
        self.tree = ttk.Treeview(self.main_frame, columns=columns, show='headings')

        self.tree.heading('title', text='Title')
        self.tree.heading('ext', text='Ext')
        self.tree.heading('size', text='Size')
        self.tree.heading('progress', text='Progress')
        self.tree.heading('speed', text='Speed')
        self.tree.heading('status', text='Status')

        self.tree.column('title', anchor=CENTER, minwidth=150, width=300, stretch=False)
        self.tree.column('ext', anchor=CENTER, minwidth=50, width=70, stretch=False)
        self.tree.column('size', anchor=CENTER, minwidth=70, width=90, stretch=False)
        self.tree.column('progress', anchor=CENTER, minwidth=60, width=80, stretch=False)
        self.tree.column('speed', anchor=CENTER, minwidth=70, width=90, stretch=False)
        self.tree.column('status', anchor=CENTER, minwidth=75, width=95, stretch=False)

        self.tree.bind('<Configure>', self.on_heading_width_change)

        # Treeview Scrollbars
        self.vsb = ttk.Scrollbar(self.main_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.vsb.set)

        treeview_right_click_menu = Menu(self.main_frame, tearoff=0, foreground='white')
        treeview_right_click_menu.add_command(label='Delete item', command=self.delete_item_treeview_action)
        treeview_right_click_menu.add_command(label='Open downloads folder', command=open_downloads_folder)

        self.tree.bind('<Button-3>', lambda event: treeview_right_click_menu.post(event.x_root, event.y_root))

        # info for user
        self.info_for_user_frame = CTkFrame(self.main_frame, width=810, height=24)
        self.info_for_user_label = CTkLabel(self.info_for_user_frame, text='')

        # draw GUI
        self.draw_gui()
        load_heading_widths(self.tree)

    def draw_gui(self):
        self.main_frame.pack()
        self.enter_url_label.place(x=21, y=12)
        self.switch.place(x=650, y=12)
        self.settings_button.place(x=740, y=10)
        self.url_entry.place(x=20, y=45)
        self.add_button.place(x=650, y=45)

        self.tree.place(x=18, y=83, width=735, height=344)
        self.vsb.place(x=755, y=85, height=340)

        self.clear_button.place(x=20, y=438)
        self.download_button.place(x=650, y=438)

        self.info_for_user_frame.place(x=-5, y=477)
        self.info_for_user_label.place(relx=.015, rely=0)

    def switch_action(self):
        self.clear_treeview()
        self.treeview_list.clear()
        if self.dl_format == 'audio':
            self.dl_format = 'video'
            data = self.get_data_for_treeview(22, 'mp4')
        else:
            self.dl_format = 'audio'
            data = self.get_data_for_treeview(140, 'mp3')
        self.switch.configure(text=self.dl_format)
        self.update_treeview(data)

    def add_action(self, event=None):
        self.treeview_list.clear()
        self.clear_treeview()

        url = self.url_entry.get()
        if url:
            try:
                if self.dl_format == 'audio':
                    get_links(url, self.yt_playlist)
                    data = self.get_data_for_treeview(140, 'mp3')
                else:
                    get_links(url, self.yt_playlist)
                    data = self.get_data_for_treeview(22, 'mp4')
                self.update_treeview(data)
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
        self.yt_playlist.clear()
        self.clear_treeview()

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

    def get_data_for_treeview(self, i_tag, dl_format):
        self.treeview_list.clear()
        for url in self.yt_playlist:
            yt = YouTube(url)
            try:
                self.treeview_list.append([
                    yt.streams.get_by_itag(i_tag).title,
                    dl_format,
                    f"{count_file_size(yt.streams.get_by_itag(i_tag).filesize)} MB",
                    "0 %",
                    "0 KiB/s",
                    "Queued"
                ])
            except (AttributeError, KeyError):
                self.treeview_list.append([
                    yt.streams.get_highest_resolution().title,
                    dl_format,
                    f"{count_file_size(yt.streams.get_highest_resolution().filesize)} MB",
                    "0 %",
                    "0 KiB/s",
                    "Queued"
                ])
        return self.treeview_list

    def update_treeview(self, array):
        for item in array:
            self.tree.insert('', 'end', values=item)

    def update_treeview_row(self, index, data):
        self.tree.item(self.tree.get_children()[index], values=data)

    def clear_treeview(self):
        for entry in self.tree.get_children():
            self.tree.delete(entry)

    def delete_item_treeview_action(self):
        selection = self.tree.selection()
        if selection:
            # Delete item from yt_playlist
            index = self.tree.index(selection[0])
            self.yt_playlist.pop(index)
            # Delete item from treeview
            self.tree.delete(selection[0])
        else:
            self.info_for_user_label.configure(text="No item selected.")

    def download_video(self, playlist, output_path):
        for index, link in enumerate(playlist):
            yt = YouTube(link, on_progress_callback=self.progress_callback)
            yt_stream = yt.streams.get_highest_resolution()
            self.treeview_list[index][5] = "Downloading"
            self.update_treeview_row(index, self.treeview_list[index])
            try:
                yt_stream.download(output_path=output_path, filename=yt_stream.default_filename)
                self.treeview_list[index][5] = "Downloaded"
                self.treeview_list[index][4] = "0 KiB/s"
                self.update_treeview_row(index, self.treeview_list[index])
            except (PermissionError, RuntimeError):
                self.info_for_user_label.configure(text="ERROR: Permission Error.")

    def download_audio(self, playlist, output_path):
        for index, link in enumerate(playlist):
            yt = YouTube(link, on_progress_callback=self.progress_callback)
            yt_stream = yt.streams.get_audio_only()
            self.treeview_list[index][5] = "Downloading"
            self.update_treeview_row(index, self.treeview_list[index])
            # change an extension to mp3 if mp4 audio downloaded.
            if yt_stream.mime_type == "audio/mp4":
                filename = yt_stream.default_filename.rsplit(".", 1)[0] + ".mp3"
            else:
                filename = yt_stream.default_filename
            try:
                yt_stream.download(output_path=output_path, filename=filename)
                self.treeview_list[index][5] = "Downloaded"
                self.treeview_list[index][4] = "0 KiB/s"
                self.update_treeview_row(index, self.treeview_list[index])
            except (PermissionError, RuntimeError):
                self.info_for_user_label.configure(text="ERROR: Permission Error.")

    def progress_callback(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100

        elapsed_time = (datetime.now() - self.download_start_time).total_seconds()
        download_speed = bytes_downloaded / (1024 * elapsed_time)

        for item in self.treeview_list:
            if item[0] == stream.title:
                item[3] = f"{percentage:.2f} %"
                if download_speed < 1000:
                    item[4] = f"{download_speed:.2f} KiB/s"
                else:
                    item[4] = f"{download_speed / 1024:.2f} MiB/s"
                break
        # Update the specific row directly
        index = [i for i, item in enumerate(self.treeview_list) if item[0] == stream.title]
        if index:
            self.update_treeview_row(index[0], self.treeview_list[index[0]])

    def check_theme_change(self):
        if darkdetect.isDark():
            sv_ttk.use_dark_theme()
        else:
            sv_ttk.use_light_theme()
        self.after(5000, self.check_theme_change)

    def on_heading_width_change(self, event):
        save_heading_widths(self.tree)

    if getattr(sys, 'frozen', False):
        pyi_splash.close()


if __name__ == '__main__':
    tube_getter = TubeGetter()
    tube_getter.check_theme_change()
    tube_getter.mainloop()
