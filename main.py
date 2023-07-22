import tkinter.font
from tkinter import Tk, ttk, Button, Entry, Label, PhotoImage
from src.config import version, image_paths, colors, font_size
from src.helpers import center_window

root = Tk()
root.iconbitmap(bitmap=image_paths['icon'])
root.title(f"YouTube Getter v{version}")
center_window(root, 800, 500)
root.resizable(False, False)


# UI Elements
custom_font = tkinter.font.Font(size=font_size)

enter_urls_label = Label(
    root,
    font=custom_font,
    text="Enter URLs:")
enter_urls_label.place(x=25, y=8)

theme_button_image = PhotoImage(file=image_paths['theme'])
theme_button = Button(
    root,
    image=theme_button_image,
    border=0)
theme_button.place(x=740, y=8)

settings_button_image = PhotoImage(file=image_paths['settings'])
settings_button = Button(
    root,
    image=settings_button_image,
    border=0)
settings_button.place(x=765, y=8)

entry_image = PhotoImage(file=image_paths['entry'])
entry_label = Label(root, image=entry_image)
entry_label.place(x=12, y=35)
url_entry = Entry(
    root,
    bg=colors[0],
    border=0)
url_entry.place(x=35, y=45, width=600)

add_button_image = PhotoImage(file=image_paths['add'])
add_button = Button(root, image=add_button_image, border=0)
add_button.place(x=670, y=35)

# treeview

clear_button_image = PhotoImage(file=image_paths['clear'])
clear_button = Button(root, image=clear_button_image, border=0)
clear_button.place(x=12, y=450)

download_button_image = PhotoImage(file=image_paths['download'])
download_button = Button(root, image=download_button_image, border=0)
download_button.place(x=670, y=450)

root.mainloop()
