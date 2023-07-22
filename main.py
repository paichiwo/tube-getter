from tkinter import Tk, ttk, Button, Entry, Label, PhotoImage, Frame, LEFT, BOTTOM, TOP, W
from src.config import version, image_paths
from src.helpers import center_window

root = Tk()
root.title(f"YouTube Getter v{version}")
center_window(root, 800, 500)
root.resizable(False, False)


# UI Elements
enter_url_label = Label(
    root,
    text="Enter URLs:",
    padx=10,
    pady=10)
enter_url_label.place(x=0, y=0)

theme_button_image = PhotoImage(file=image_paths['theme'])
theme_button_button = Button(
    image=theme_button_image,
    border=0,
    padx=10,
    pady=10)
theme_button_button.place(x=720, y=8)

settings_button_image = PhotoImage(file=image_paths[])

root.mainloop()
