import os
import urllib.error
from pycda import PyCDA
from src.media_root import MediaRoot
from src.config import INFO_MSG
from src.helpers import (get_links, format_file_size, load_settings, format_filename, convert_to_mp3,
                         format_dl_speed_string)


class CDAer(MediaRoot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_cda(self, url):
        try:
            self.url_list.clear()
            get_links(url, self.url_list)
            self.info_msg(INFO_MSG['gathering_data'])
            data = self.get_cda_data_for_table()
            self.add_update_with_new_data(data)
        except (KeyError, TypeError):
            self.info_msg(INFO_MSG['wrong_url_err'])
        except urllib.error.URLError:
            self.info_msg(INFO_MSG['internal_err'])
        self.enable_buttons()

    def get_cda_data_for_table(self):
        cda = PyCDA(self.url_list[0])
        self.table_list.append([
            cda.thumbnail(),
            cda.title(),
            cda.channel(),
            str(cda.duration()),
            'N/A',
            cda.publish_date(),
            'mp4',
            format_file_size(cda.filesize())
        ])
        return self.table_list

    def cda_download(self):
        output_path = load_settings()

        for i, link in enumerate(self.url_list):
            cda = PyCDA(url=link)
            filename = str(os.path.join(output_path, format_filename(cda.title())))
            file_exists = os.path.exists(f'{filename}.mp4') or (
                    self.dl_format == 'audio' and os.path.exists(f'{filename}.mp3'))

            if file_exists:
                self.table.frames[i].change_delete_btn()
                self.info_msg(INFO_MSG['file_exists'])
                continue

            self.info_msg(INFO_MSG['downloading'])
            cda.download(filename=filename, on_progress_callback=self.cda_progress_callback)

            if self.dl_format == 'audio':
                self.table.frames[i].delete_btn.configure(state='disabled')
                self.cda_convert(filename, i)
            else:
                self.dl_speed.configure(self.initial_speed)
                self.info_msg(INFO_MSG['dl_complete'])

    def cda_convert(self, filename, i):
        pass

    def cda_progress_callback(self, count, block_size, total_size):
        pass

    def update_progress_bars(self):
        pass

