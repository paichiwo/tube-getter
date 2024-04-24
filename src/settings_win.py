import webbrowser
from tkinter import filedialog, CENTER
from PIL import Image
from customtkinter import CTkToplevel, CTkFrame, CTkButton, CTkLabel, CTkImage
from src.config import IMG_PATHS, SETTINGS_HEADER, SETTINGS_MSG, GITHUB_URL
from src.helpers import save_settings, load_settings, center_window


class SettingsWindow(CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.after(250, lambda: self.iconbitmap(bitmap=IMG_PATHS['icon']))
        self.after(100, lambda: self.focus())
        self.title('Settings')
        self.resizable(False, False)
        center_window(self, 500, 450)

        self.top_frame = CTkFrame(self, width=490, height=310)

        # Top frame widgets
        self.logo_image = CTkImage(Image.open(IMG_PATHS['icon_png']), size=(64, 64))
        self.logo_label = CTkLabel(self.top_frame, image=self.logo_image, text='')

        self.header_label = CTkLabel(self.top_frame, text=SETTINGS_HEADER)
        self.message_label = CTkLabel(self.top_frame, text=SETTINGS_MSG, width=490, height=120)

        self.github_image = CTkImage(Image.open(IMG_PATHS['github']), size=(32, 32))
        self.github_label = CTkLabel(self.top_frame, image=self.github_image, text='',
                                     width=32, height=32, cursor='hand2')
        self.github_label.bind('<Button-1>', lambda _: webbrowser.open(GITHUB_URL))
        self.github_link = CTkLabel(self.top_frame, text='GitHub', cursor='hand2')
        self.github_link.bind('<Button-1>', lambda _: webbrowser.open(GITHUB_URL))

        # Bottom widgets
        self.output_text_label = CTkLabel(self, text='Choose output folder:', width=200, height=30)
        self.output_destination_label = CTkLabel(self, text=f'{load_settings()}', width=400, height=30)
        self.output_button = CTkButton(self, text='Browse', command=self.get_output_path)

        self.draw_gui()

    def draw_gui(self):
        self.top_frame.place(relx=.5, rely=.355, anchor=CENTER)

        # top frame
        self.logo_label.place(relx=.5, rely=.12, anchor=CENTER)
        self.header_label.place(relx=.5, rely=.3, anchor=CENTER)
        self.message_label.place(relx=.5, rely=.57, anchor=CENTER)
        self.github_label.place(relx=.5, rely=.8, anchor=CENTER)
        self.github_link.place(relx=.5, rely=.89, anchor=CENTER)

        # bottom
        self.output_text_label.place(relx=.5, rely=.75, anchor=CENTER)
        self.output_destination_label.place(relx=.5, rely=.82, anchor=CENTER)
        self.output_button.place(relx=.5, rely=.9, anchor=CENTER)

    def get_output_path(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_destination_label.configure(text=folder_selected)
            save_settings({'output_folder': folder_selected}, 'settings.json')
            self.focus()
