from datetime import datetime, timedelta


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

