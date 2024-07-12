#!/usr/bin/python3
import sys
import threading
from tkinterdnd2 import TkinterDnD, DND_ALL
from pychute import PyChute
from cda_download import CdaDownload
from datetime import datetime
from customtkinter import CTk, CTkFrame, CTkButton, CTkEntry, CTkLabel, CTkSwitch
from src.youtuber import YouTuber
from src.bitchuter import Bitchuter
from src.cdaer import CDAer
from src.config import VERSION, IMG_PATHS, INFO_MSG
from src.helpers import center_window, imager, check_for_new_version, unzip_ffmpeg
from src.other_windows import SettingsWindow, NewVersionWindow
from src.info_frame import Table
from src.popup_menu import CTkPopupMenu


if getattr(sys, 'frozen', False):
    import pyi_splash


class TubeGetter(CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

        self.iconbitmap(bitmap=IMG_PATHS['icon'])
        self.title(f'Tube Getter v{VERSION}')
        center_window(self, 1000, 600)
        self.minsize(500, 400)  # adjust later

        self.settings_window = None

        self.url_list = []
        self.table_list = []
        self.download_start_time = datetime.now()
        self.dl_format = 'audio'
        self.provider = 'youtube'
        self.initial_speed = '0 KiB/s'

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
        self.settings_button = CTkButton(self.top_frame_1, image=imager(IMG_PATHS['settings'], 19, 19),
                                         text='', width=40, command=self.settings_action)

        # TOP FRAME 2
        self.url_entry = CTkEntry(self.top_frame_2, border_width=1)
        self.url_entry.bind('<Return>', self.add_action)
        self.url_entry.bind('<Control-z>', self.delete_url_action)

        self.add_button = CTkButton(self.top_frame_2, text='Add', width=130, command=self.add_action)

        # MIDDLE FRAME
        self.table = Table(self.middle_frame, yt_links=self.url_list, table_data=self.table_list,
                           fg_color=('grey80', 'grey10'))

        # BOTTOM UPPER FRAME
        self.clear_button = CTkButton(self.bottom_frame_1, text='Clear', width=130, command=self.clear_action)
        self.download_button = CTkButton(self.bottom_frame_1, text='Download', width=130, command=self.download_action)

        # BOTTOM LOWER FRAME
        self.info_for_user_frame = CTkFrame(self.bottom_frame_2, height=24, corner_radius=0)
        self.info_for_user_label = CTkLabel(self.info_for_user_frame, text='')
        self.dl_speed = CTkLabel(self.info_for_user_frame, text=self.initial_speed)

        # RIGHT CLICK MENU FOR URL ENTRY
        self.url_entry_menu = CTkPopupMenu(master=self, width=80, height=50, corner_radius=8, border_width=1)
        # self.url_entry_menu.attributes('-alpha', .85)
        self.url_entry.bind('<Button-3>', lambda event: self.url_entry_menu.popup(event), add='+')
        self.paste_button = CTkButton(self.url_entry_menu.frame, text='Paste', command=self.paste_action,
                                      text_color=('black', 'white'), hover_color=("gray90", "gray25"),
                                      compound='left', anchor='w', fg_color='transparent', corner_radius=5)
        self.paste_button.pack(expand=True, fill="x", padx=10, pady=0)

        # create youtuber object
        self.youtuber = YouTuber(self.dl_format, self.url_list, self.table_list, self.add_update_with_new_data,
                                 self.enable_buttons, self.info_msg, self.dl_speed, self.table)
        # create bitchuter object
        self.bitchuter = Bitchuter(self.dl_format, self.url_list, self.table_list, self.add_update_with_new_data,
                                   self.enable_buttons, self.info_msg, self.dl_speed, self.table)
        # create cda object
        self.cdaer = CDAer(self.dl_format, self.url_list, self.table_list, self.add_update_with_new_data,
                           self.enable_buttons, self.info_msg, self.dl_speed, self.table)

        # draw GUI
        self.draw_gui()
        self.enable_drag_and_drop()

        # check for the newest release
        self.check_for_new_version()

        # unzip ffmpeg
        unzip_ffmpeg()

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

    def enable_drag_and_drop(self):
        widgets = [self.url_entry, self.middle_frame]
        for widget in widgets:
            widget.drop_target_register(DND_ALL)
            widget.dnd_bind('<<Drop>>', self.drop_action)

    def info_msg(self, text):
        self.info_for_user_label.configure(text=text)

    def disable_buttons(self):
        self.add_button.configure(state='disabled')
        self.switch.configure(state='disabled')
        self.clear_button.configure(state='disabled')
        self.download_button.configure(state='disabled')

    def enable_buttons(self):
        self.add_button.configure(state='normal')
        self.switch.configure(state='normal')
        self.clear_button.configure(state='normal')
        self.download_button.configure(state='normal')

    def paste_action(self):
        self.url_entry.insert('end', self.clipboard_get())

    def switch_action(self):
        if self.dl_format == 'audio':
            self.dl_format = 'video'
            self.youtuber.dl_format = 'video'
            self.cdaer.dl_format = 'video'
            self.bitchuter.dl_format = 'video'
        else:
            self.dl_format = 'audio'
            self.youtuber.dl_format = 'audio'
            self.cdaer.dl_format = 'audio'
            self.bitchuter.dl_format = 'audio'

        self.switch.configure(text=self.dl_format)
        self.update_table()

    def update_table(self):
        self.table.delete_all_data_frames()
        self.table_list.clear()

        if self.provider == 'youtube':
            data = self.youtuber.create_yt_media_table()
            self.draw_table(data)
        if self.provider == 'bitchute':
            data = self.bitchuter.create_media_table(PyChute)
            self.draw_table(data)
        if self.provider == 'cda':
            data = self.cdaer.create_media_table(CdaDownload)
            self.draw_table(data)

    def check_urls(self, url):
        if 'youtube' in url or 'youtu.be' in url:
            new_provider = 'youtube'
            processor = self.youtuber
        elif 'bitchute' in url:
            new_provider = 'bitchute'
            processor = self.bitchuter
        elif 'cda' in url:
            new_provider = 'cda'
            processor = self.cdaer
        else:
            self.info_msg(INFO_MSG['wrong_url_err'])
            return

        if self.provider != new_provider:
            self.provider = new_provider
            self.url_list.clear()

        processor.add(url)

    def process_url(self, url):
        if not url:
            self.info_msg(INFO_MSG['url_detected_err'])
            return

        self.info_msg('')
        self.table_list.clear()
        self.disable_buttons()

        def add_threaded():
            self.check_urls(url)
            self.enable_buttons()

        add_thread = threading.Thread(target=add_threaded)
        add_thread.start()

    def add_action(self):
        """Handle URL entered manually."""
        url = self.url_entry.get()
        self.process_url(url)

    def drop_action(self, event):
        """Handle URL dropped."""
        dropped_data = event.data
        if dropped_data:
            self.url_entry.delete(0, 'end')
            self.url_entry.insert(0, dropped_data)
            self.process_url(dropped_data)
        else:
            self.info_msg(INFO_MSG['url_detected_err'])

    def add_update_with_new_data(self, data):
        if data:
            if len(self.table.frames) != 0:
                self.table.delete_all_data_frames()
            self.draw_table(data)
            self.info_msg('Ready')
            self.enable_buttons()

    def delete_url_action(self, event=None):
        if event:
            self.url_entry.delete(0, 'end')

    def clear_action(self):
        self.url_list.clear()
        self.table_list.clear()
        self.table.delete_all_data_frames()
        self.info_msg('')

    def download_action(self):
        def download_task():

            for data_frame in self.table.frames:
                data_frame.delete_btn.configure(state='disabled')

            if self.provider == 'youtube':
                self.youtuber.download()
            elif self.provider == 'bitchute':
                self.bitchuter.download()
            elif self.provider == 'cda':
                self.cdaer.download()

        download_thread = threading.Thread(target=download_task)
        download_thread.start()

    def settings_action(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self)
        else:
            self.settings_window.focus()

    def draw_table(self, array):
        self.table.table_data = array
        self.table.create_list_with_data_frames()
        self.table.draw_data_frames()

    @staticmethod
    def check_for_new_version():
        release = check_for_new_version()
        if release != VERSION:
            NewVersionWindow(release)

    if getattr(sys, 'frozen', False):
        pyi_splash.close()


if __name__ == '__main__':
    tg = TubeGetter()
    tg.mainloop()
