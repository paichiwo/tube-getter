from datetime import datetime
from customtkinter import CTkScrollableFrame, CTkFrame, CTkImage, CTkLabel, CTkButton, CTkFont, CTkProgressBar
from src.config import IMG_PATHS
from requests import get
from PIL import Image
from io import BytesIO


class Table(CTkScrollableFrame):
    """ Custom scrollable frame that holds DataFrames"""

    def __init__(self, master,
                 yt_links=None,
                 table_data=None,
                 width=300,
                 height=300,
                 entry_padx=5,
                 entry_pady=5,
                 entry_color=('grey90', 'grey20'),
                 *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # arrays with data
        self.yt_links = yt_links
        self.table_data = table_data

        # entry configuration
        self.entry_padx = entry_padx
        self.entry_pady = entry_pady
        self.entry_color = entry_color

        # table configuration
        self.configure(width=width, height=height)

        # list containing data frames
        self.frames = []

        # initial setup
        self.create_list_with_data_frames()
        self.draw_data_frames()
        self.update_frames()

    def create_list_with_data_frames(self):
        for data_entry in self.table_data:
            self.frames.append(DataFrame(self, data_entry, self.delete_one_data_frame, fg_color=self.entry_color))

    def draw_data_frames(self):
        for data_frame in self.frames:
            data_frame.pack(padx=self.entry_padx, pady=self.entry_pady, fill='x')

    def update_frames(self):
        for i, frame in enumerate(self.frames):
            frame.index = i

    def delete_all_data_frames(self):
        for data_frame in self.frames:
            data_frame.destroy()
        self.frames.clear()

    def delete_one_data_frame(self):
        for i, frame in enumerate(self.frames):
            if frame.deleted:
                self.frames.pop(i)
                self.table_data.pop(i)
                self.yt_links.pop(i)
                frame.destroy()

        self.update_frames()


class DataFrame(CTkFrame):
    """ Custom frame widget that holds and displays data about the YouTube video. """

    def __init__(self, master, data, destroy_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.master = master
        self.data = data
        self.index = 0
        self.deleted = False
        self.destroy_callback = destroy_callback

        self.thumbnail = CTkLabel(self,
                                  text='',
                                  image=CTkImage(self.create_thumbnail(data[0]), size=(64, 36)))

        self.title = CTkLabel(self,
                              text=self.data[1],
                              height=12)

        self.channel = CTkLabel(self,
                                text=self.data[2],
                                font=CTkFont(size=11),
                                height=8)

        self.duration = CTkLabel(self,
                                 text=f' {self.convert_time(self.data[3])}',
                                 image=CTkImage(Image.open(IMG_PATHS['clock']), size=(12, 12)),
                                 compound='left',
                                 font=CTkFont(size=11),
                                 height=8)

        self.views = CTkLabel(self,
                              text=f' {self.data[4]}',
                              image=CTkImage(Image.open(IMG_PATHS['eye']), size=(12, 12)),
                              compound='left',
                              font=CTkFont(size=11),
                              height=8)

        self.uploaded_date = CTkLabel(self,
                                      text=f' {self.convert_date(self.data[5])}',
                                      image=CTkImage(Image.open(IMG_PATHS['calendar']), size=(12, 12)),
                                      compound='left',
                                      font=CTkFont(size=11),
                                      height=8)

        self.extension = CTkLabel(self,
                                  text='test',
                                  fg_color=('grey80', 'grey25'),
                                  corner_radius=5)

        self.download_speed = CTkLabel(self,
                                       text='0 KiB/s',
                                       fg_color=('grey80', 'grey25'),
                                       corner_radius=5)

        self.delete_btn = CTkButton(self,
                                    text='',
                                    width=24,
                                    image=CTkImage(Image.open(IMG_PATHS['bin']), size=(24, 24)),
                                    fg_color='transparent',
                                    hover_color=('grey80', 'grey25'),
                                    command=self.delete_action)

        self.progress_bar_frame = CTkFrame(self)
        self.progress_bar = CTkProgressBar(self.progress_bar_frame, height=2)
        self.progress_bar.set(0)

        # draw elements
        self.draw_elements()

    def delete_action(self):
        self.deleted = True
        self.destroy_callback()

    def draw_elements(self):
        self.progress_bar_frame.pack(anchor='n', side='bottom', fill='x', padx=7)
        self.progress_bar.pack(anchor='n', side='bottom', fill='x')

        self.thumbnail.place(x=7, y=7)
        self.update()
        self.title.pack(anchor='w', padx=(self.thumbnail.winfo_width() + 15, 0), pady=(10, 5))
        self.update()
        self.channel.pack(anchor='w', side='left', padx=(self.thumbnail.winfo_width() + 15, 10), pady=(0, 7))
        self.duration.pack(anchor='w', side='left', padx=(0, 10), pady=(0, 7))
        self.views.pack(anchor='w', side='left', padx=(0, 10), pady=(0, 7))
        self.uploaded_date.pack(anchor='w', side='left', padx=(0, 10), pady=(0, 7))

        self.extension.place(relx=.84, rely=.5, anchor='center')
        self.download_speed.place(relx=.9, rely=.5, anchor='center')
        self.delete_btn.place(relx=.96, rely=.5, anchor='center')

    @staticmethod
    def create_thumbnail(url):
        response = get(url)
        image_data = response.content
        image = Image.open(BytesIO(image_data)).resize((64, 36))
        return image

    @staticmethod
    def convert_time(time_in_sec):
        hours = time_in_sec // 3600
        time_in_sec %= 3600
        minutes = time_in_sec // 60
        time_in_sec %= 60
        return f'{hours:02d}:{minutes:02d}:{time_in_sec:02d}'

    @staticmethod
    def convert_date(date):
        return datetime.strptime(str(date).split(' ')[0], '%Y-%m-%d').strftime('%d-%m-%Y')
