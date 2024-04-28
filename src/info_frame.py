from tkinter import X, CENTER, N, W, S, E
from datetime import datetime

from customtkinter import CTk, CTkScrollableFrame, CTkFrame, CTkImage, CTkLabel, CTkButton, CTkFont
from pytubefix import YouTube, Channel
from src.helpers import get_links, center_window
from requests import get
from PIL import Image
from io import BytesIO


class DataFrame(CTkFrame):
    """ Custom frame widget that holds and displays data about the YouTube video. """
    def __init__(self, master, data, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.data = data
        # self.configure(height=50)

        """LEFT SIDE"""

        # thumbnail (60x36)
        self.thumbnail = CTkLabel(self, text='', image=CTkImage(self.display_image(data[0]), size=(64, 36)))

        # title
        self.title = CTkLabel(self, text=self.data[1], height=12)

        # channel name
        self.channel = CTkLabel(self, text=self.data[2], font=CTkFont(size=11), height=8)

        # duration
        self.duration = CTkLabel(self, text=f' {self.convert_time(self.data[3])}', image=CTkImage(Image.open('../images/hourglass_12x12_white.png'), size=(12, 12)), compound='left', font=CTkFont(size=11), height=8)

        # views
        self.views = CTkLabel(self, text=f' {self.data[4]}', image=CTkImage(Image.open('../images/eye_12x12_white.png'), size=(12, 12)), compound='left', font=CTkFont(size=11), height=8)

        # uploaded_date
        self.uploaded_date = CTkLabel(self, text=f' {self.convert_date(self.data[5])}', image=CTkImage(Image.open('../images/calendar_12x12_white.png'), size=(12, 12)), compound='left', font=CTkFont(size=11), height=8)

        # RIGHT SIDE
        self.extension = None
        self.delete_btn = None

        # draw elements
        self.draw_elements()

    def draw_elements(self):
        self.thumbnail.grid(column=0, row=0, rowspan=2, padx=10, pady=10, sticky=W)
        self.title.grid(column=1, row=0, columnspan=800, pady=(0, 1), sticky=(S, W))
        self.channel.grid(column=2, row=1, padx=(0, 5),  pady=(6, 4), sticky=W)
        self.duration.grid(column=3, row=1, padx=5,  pady=(6, 4), sticky=W)
        self.views.grid(column=4, row=1, padx=5,  pady=(6, 4), sticky=W)
        self.uploaded_date.grid(column=5, row=1, padx=5, pady=(6, 4), sticky=W)

    @staticmethod
    def display_image(url):
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


if __name__ == '__main__':
    single_link = 'https://www.youtube.com/watch?v=afB4DlkebO8'
    playlist_link = 'https://www.youtube.com/watch?v=gKDuHIRNJSY&list=PLRNsV20DA24Gmt9C-X4CVFF4eP76KtkLq&pp=gAQBiAQB'

    url_list = []
    table_data_list = []
    get_links(playlist_link, url_list)

    for link in url_list:
        yt = YouTube(link)
        table_data_list.append([
                yt.thumbnail_url,
                yt.title,
                Channel(yt.channel_url).channel_name,
                yt.length,
                yt.views,
                yt.publish_date
            ])

    root = CTk()
    center_window(root, 800, 500)

    scr_frame = CTkScrollableFrame(root, width=800, height=300, fg_color='black')
    scr_frame.pack()

    for data_entry in table_data_list:
        data_frame = DataFrame(scr_frame, data_entry)
        data_frame.pack(padx=5, pady=5, fill=X)

    root.mainloop()
