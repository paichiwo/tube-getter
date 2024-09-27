import os
import urllib.error
import pytubefix.exceptions
from datetime import datetime
from pytubefix import YouTube, Channel
from src.config import INFO_MSG
from src.helpers import (get_links, convert_time, format_date, format_file_size, load_settings,
                         handle_audio_extension, format_dl_speed_string)
from src.media_root import MediaRoot


class YouTuber(MediaRoot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add(self, url):
        try:
            get_links(url, self.url_list)
            self.info_msg(INFO_MSG['gathering_data'])
            data = self.create_yt_media_table()
            self.add_update_with_new_data(data)
        except pytubefix.exceptions.VideoUnavailable as e:
            self.info_msg(e)
        except (pytubefix.exceptions.RegexMatchError, KeyError):
            self.info_msg(INFO_MSG['wrong_url_err'])
        except urllib.error.URLError:
            self.info_msg(INFO_MSG['internal_err'])
        finally:
            self.enable_buttons()

    def create_yt_media_table(self):
        self.table_list.clear()
        for url in self.url_list:
            yt = YouTube(url, client='MWEB')
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
                    format_date(yt.publish_date),
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
                    format_date(yt.publish_date),
                    'mp4',
                    format_file_size(yt.streams.get_highest_resolution().filesize)
                ])
        return self.table_list

    def download(self):
        output_path = load_settings()
        for i, link in enumerate(self.url_list):
            yt = YouTube(link, client='MWEB', on_progress_callback=self.progress_callback)
            if self.dl_format == 'audio':
                yt_stream = yt.streams.get_audio_only()
                filename = handle_audio_extension(yt_stream)
            else:
                yt_stream = yt.streams.get_highest_resolution()
                filename = yt_stream.title + '.mp4'
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

    def progress_callback(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = bytes_downloaded / total_size
        elapsed_time = (datetime.now() - self.download_start_time).total_seconds()
        download_speed = bytes_downloaded / (1024 * elapsed_time)

        self.update_progress_gui(stream, percentage, download_speed)

    def update_progress_gui(self, stream, percentage, download_speed):
        for i, item in enumerate(self.table_list):
            if item[1] == stream.title:
                self.table.frames[i].progress_bar.set(percentage)
                self.table.frames[i].change_delete_btn()
                self.dl_speed.configure(text=format_dl_speed_string(download_speed))
