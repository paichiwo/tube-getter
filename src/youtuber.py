import os
import urllib.error
import pytubefix.exceptions
from datetime import datetime
from pytubefix import YouTube, Channel

from src.config import IMG_PATHS, INFO_MSG
from src.helpers import (get_links, convert_time, convert_date, format_file_size, load_settings, open_downloads_folder,
                         handle_audio_extension, imager, format_dl_speed_string)


class YouTuber:
    def __init__(self, dl_format, yt_list, table_list, add_update_with_new_data, enable_buttons, info_msg,
                 dl_speed, table):

        self.yt_list = yt_list
        self.table_list = table_list
        self.info_msg = info_msg
        self.add_update_with_new_data = add_update_with_new_data
        self.enable_buttons = enable_buttons
        self.dl_format = dl_format
        self.dl_speed = dl_speed
        self.table = table

        self.initial_speed = '0 KiB/s'
        self.download_start_time = datetime.now()

    def add_youtube(self, url):
        try:
            get_links(url, self.yt_list)
            self.info_msg(INFO_MSG['gathering_data'])
            data = self.get_yt_data_for_table()
            self.add_update_with_new_data(data)
        except pytubefix.exceptions.VideoUnavailable:
            self.info_msg(INFO_MSG['age_restricted_err'])
        except (pytubefix.exceptions.RegexMatchError, KeyError):
            self.info_msg(INFO_MSG['gathering_data'])
        except urllib.error.URLError:
            self.info_msg(INFO_MSG['internal_err'])
        self.enable_buttons()

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

    def yt_download(self):
        filename = ''
        output_path = load_settings()
        for i, link in enumerate(self.yt_list):
            yt = YouTube(link, on_progress_callback=self.yt_progress_callback)
            if self.dl_format == 'audio':
                yt_stream = yt.streams.get_audio_only()
                filename = handle_audio_extension(yt_stream)
            else:
                yt_stream = yt.streams.get_highest_resolution()
            self.info_msg(INFO_MSG['downloading'])
            try:
                if os.path.exists(os.path.join(load_settings(), filename)):
                    self.table.frames[i].change_delete_btn()
                    self.info_msg(INFO_MSG['file_exists'])
                else:
                    yt_stream.download(output_path=output_path, filename=filename)
                    self.dl_speed.configure(text=self.initial_speed)
                    self.info_msg(INFO_MSG['dl_complete'])
            except (PermissionError, RuntimeError):
                self.info_msg(INFO_MSG['permission_err'])

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
