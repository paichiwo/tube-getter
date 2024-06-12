import os
import urllib.error
from datetime import datetime, timedelta
from src.media_root import MediaRoot
from pychute import PyChute
from src.config import INFO_MSG
from src.helpers import (get_links, format_file_size, load_settings, format_filename, convert_to_mp3,
                         format_dl_speed_string)


class Bitchuter(MediaRoot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.last_update_time = datetime.now()

    def add_bitchute(self, url):
        try:
            self.url_list.clear()
            get_links(url, self.url_list)
            self.info_msg(INFO_MSG['gathering_data'])
            data = self.get_bc_data_for_table()
            self.add_update_with_new_data(data)
        except (KeyError, TypeError):
            self.info_msg(INFO_MSG['wrong_url_err'])
        except urllib.error.URLError:
            self.info_msg(INFO_MSG['internal_err'])
        self.enable_buttons()

    def get_bc_data_for_table(self):
        pc = PyChute(self.url_list[0])
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

    def bc_download(self):
        output_path = load_settings()

        for i, link in enumerate(self.url_list):
            pc = PyChute(url=link)
            filename = os.path.join(output_path, format_filename(pc.title()))
            file_exists = os.path.exists(f"{filename}.mp4") or (
                        self.dl_format == 'audio' and os.path.exists(f"{filename}.mp3"))

            if file_exists:
                self.table.frames[i].change_delete_btn()
                self.info_msg(INFO_MSG['file_exists'])
                continue

            self.info_msg(INFO_MSG['downloading'])
            pc.download(filename=filename, on_progress_callback=self.bc_progress_callback)

            if self.dl_format == 'audio':
                self.table.frames[i].delete_btn.configure(state='disabled')
                self.bc_convert(filename, i)
            else:
                self.dl_speed.configure(self.initial_speed)
                self.info_msg(INFO_MSG['dl_complete'])

    def bc_convert(self, filename, i):
        self.info_msg(INFO_MSG['converting'])
        convert_to_mp3(f'{filename}.mp4', f'{filename}.mp3')
        os.remove(f'{filename}.mp4')
        self.table.frames[i].extension.configure(text='mp3')
        self.table.frames[i].size.configure(text=f'{format_file_size(os.path.getsize(f'{filename}.mp3'))}')
        self.table.frames[i].change_delete_btn()

        if os.path.exists(filename + '.mp3'):
            self.table.frames[i].change_delete_btn()
            self.dl_speed.configure(text=self.initial_speed)
            self.info_msg(INFO_MSG['conversion_done'])

    def bc_progress_callback(self, count, block_size, total_size):
        percentage = min(1.0, float(count * block_size) / total_size)
        elapsed_time = (datetime.now() - self.download_start_time).total_seconds()
        download_speed = (count * block_size) / (1024 * elapsed_time)

        current_time = datetime.now()
        if (current_time - self.last_update_time) >= timedelta(seconds=.5):
            self.update_progress_bars(percentage, download_speed)
            self.last_update_time = current_time

        if percentage == 1.0:
            self.update_progress_bars(1.0, download_speed)
            self.dl_speed.configure(text=self.initial_speed)

    def update_progress_bars(self, percentage, download_speed):
        for i, item in enumerate(self.table_list):
            self.table.frames[i].progress_bar.set(percentage)
        self.dl_speed.configure(text=format_dl_speed_string(download_speed))
