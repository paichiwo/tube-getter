import os
import urllib.error
from datetime import datetime, timedelta
from cda_download import CdaDownload
from pychute import PyChute
from src.config import INFO_MSG
from src.helpers import (get_links, format_file_size, load_settings, format_filename, convert_to_mp3,
                         format_dl_speed_string)


class MediaRoot:
    def __init__(self, dl_format, url_list, table_list, add_update_with_new_data, enable_buttons, info_msg,
                 dl_speed, table):

        self.url_list = url_list
        self.table_list = table_list
        self.info_msg = info_msg
        self.add_update_with_new_data = add_update_with_new_data
        self.enable_buttons = enable_buttons
        self.dl_format = dl_format
        self.dl_speed = dl_speed
        self.table = table

        self.initial_speed = '0 KiB/s'
        self.download_start_time = datetime.now()
        self.last_update_time = datetime.now()

    def add_media(self, url, media_type):
        try:
            self.url_list.clear()
            get_links(url, self.url_list)
            self.info_msg(INFO_MSG['gathering_data'])
            data = self.get_media_data(media_type)
            self.add_update_with_new_data(data)
        except (KeyError, TypeError):
            self.info_msg(INFO_MSG['wrong_url_err'])
        except urllib.error.URLError:
            self.info_msg(INFO_MSG['internal_err'])
        self.enable_buttons()

    def get_media_data(self, media_type):
        if media_type == 'cda':
            return self.create_media_table(CdaDownload)
        elif media_type == 'bitchute':
            return self.create_media_table(PyChute)

    def create_media_table(self, media_class):
        media = media_class(self.url_list[0])
        data = [
            media.thumbnail(),
            media.title(),
            media.channel(),
            str(media.duration()),
            'N/A' if media_class == CdaDownload else media.views(),
            media.publish_date().split(' ')[0] if media_class == PyChute else media.publish_date(),
            'mp4',
            format_file_size(media.filesize())
        ]
        self.table_list.append(data)
        return self.table_list

    def download_media(self, media_type):
        output_path = load_settings()

        for i, link in enumerate(self.url_list):
            media = CdaDownload(link) if media_type == 'cda' else PyChute(link)
            filename = os.path.join(output_path, format_filename(media.title()))
            file_exists = os.path.exists(f'{filename}.mp4') or (
                    self.dl_format == 'audio' and os.path.exists(f'{filename}.mp3'))

            if file_exists:
                self.table.frames[i].change_delete_btn()
                self.info_msg(INFO_MSG['file_exists'])
                continue

            self.info_msg(INFO_MSG['downloading'])
            media.download(filename=filename, on_progress_callback=self.progress_callback)

            if self.dl_format == 'audio':
                self.table.frames[i].delete_btn.configure(state='disabled')
                self.convert_media(filename, i)
            else:
                self.dl_speed.configure(self.initial_speed)
                self.info_msg(INFO_MSG['dl_complete'])

    def convert_media(self, filename, i):
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

    def progress_callback(self, count, block_size, total_size):
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
