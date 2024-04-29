from datetime import datetime
from customtkinter import CTk, CTkScrollableFrame, CTkFrame, CTkImage, CTkLabel, CTkButton, CTkFont, CTkProgressBar
from pytubefix import YouTube, Channel
from src.helpers import get_links, center_window
from requests import get
from PIL import Image
from io import BytesIO


class Table(CTkScrollableFrame):
    """ Custom scrollable frame that holds DataFrames"""

    def __init__(self, master, table_data, width=300, height=300, entry_padx=5, entry_pady=5, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.table_data = table_data
        self.configure(width=width, height=height)

        for data_entry in self.table_data:
            data_frame = DataFrame(self, data_entry)
            data_frame.pack(padx=entry_padx, pady=entry_pady, fill='x')


class DataFrame(CTkFrame):
    """ Custom frame widget that holds and displays data about the YouTube video. """

    def __init__(self, master, data, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.data = data
        self.configure(height=50)

        self.thumbnail = CTkLabel(self,
                                  text='',
                                  image=CTkImage(self.display_image(data[0]), size=(64, 36)))

        self.title = CTkLabel(self,
                              text=self.data[1],
                              height=12)

        self.channel = CTkLabel(self,
                                text=self.data[2],
                                font=CTkFont(size=11),
                                height=8)

        self.duration = CTkLabel(self,
                                 text=f' {self.convert_time(self.data[3])}',
                                 image=CTkImage(Image.open('../images/test/clock.png'), size=(12, 12)),
                                 compound='left',
                                 font=CTkFont(size=11),
                                 height=8)

        self.views = CTkLabel(self,
                              text=f' {self.data[4]}',
                              image=CTkImage(Image.open('../images/test/webcam.png'), size=(12, 12)),
                              compound='left',
                              font=CTkFont(size=11),
                              height=8)

        self.uploaded_date = CTkLabel(self,
                                      text=f' {self.convert_date(self.data[5])}',
                                      image=CTkImage(Image.open('../images/test/calendar.png'), size=(12, 12)),
                                      compound='left',
                                      font=CTkFont(size=11),
                                      height=8)

        self.extension = CTkLabel(self,
                                  text='test',
                                  width=20,
                                  fg_color='grey25',
                                  corner_radius=5)

        self.delete_btn = CTkButton(self,
                                    text='',
                                    width=24,
                                    image=CTkImage(Image.open('../images/test/bin.png'), size=(24, 24)),
                                    fg_color='transparent',
                                    hover_color='grey20')

        self.progress_bar = CTkProgressBar(self, width=954, height=2)

        # draw elements
        self.draw_elements()

    def draw_elements(self):
        self.thumbnail.place(x=7, y=7)
        self.update()
        self.title.place(x=self.thumbnail.winfo_x() + self.thumbnail.winfo_width() + 10, y=7)
        self.channel.place(x=self.thumbnail.winfo_x() + self.thumbnail.winfo_width() + 10, y=29)
        self.update()
        self.duration.place(x=self.channel.winfo_x() + self.channel.winfo_width() + 10, y=29)
        self.update()
        self.views.place(x=self.duration.winfo_x() + self.duration.winfo_width() + 10, y=29)
        self.update()
        self.uploaded_date.place(x=self.views.winfo_x() + self.views.winfo_width() + 10, y=29)

        self.extension.place(relx=.9, rely=.5, anchor='center')
        self.delete_btn.place(relx=.96, rely=.5, anchor='center')

        self.progress_bar.place(x=7, y=48)

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
    center_window(root, 1000, 600)
    root.resizable(False, False)

    table = Table(root, table_data_list, height=400, fg_color='black')
    table.pack(fill='x')

    root.mainloop()
