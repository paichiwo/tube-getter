import tkinter.font
import pytube.exceptions
import urllib.error
from tkinter import Tk, ttk, Button, Entry, Label, PhotoImage, CENTER
from src.settings_window import settings_window
from src.config import version, image_paths, colors, font_size
from src.helpers import center_window, get_playlist_links, get_data_for_treeview

yt_playlist = []


def download():
    pass


def clear():
    """Clear all data from the list and the treeview"""
    yt_playlist.clear()
    for item in tree.get_children():
        tree.delete(item)


def add():
    """Add youtube link or youtube playlist to queue"""
    url = url_entry.get()
    file_type = combobox.get()
    if url:
        try:
            get_playlist_links(url, yt_playlist)
            if file_type == "Audio":
                data = get_data_for_treeview(140, 'mp3', yt_playlist)
                for item in data:
                    tree.insert("", "end", values=item)
            else:
                data = get_data_for_treeview(22, 'mp4', yt_playlist)
                for item in data:
                    tree.insert("", "end", values=item)

        except pytube.exceptions.VideoUnavailable:
            print("ERROR: Video is age restricted.")
        except pytube.exceptions.RegexMatchError:
            print("ERROR: Wrong URL.")
        except (urllib.error.URLError, urllib.error.HTTPError):
            print("ERROR: Internal error.")
    else:
        print("ERROR: No url detected.")


root = Tk()
root.iconbitmap(bitmap=image_paths['icon'])
root.title(f"YouTube Getter v{version}")
center_window(root, 800, 500)
root.resizable(False, False)


# UI Elements

custom_font = tkinter.font.Font(size=font_size)

# Enter Urls label:
enter_urls_label = Label(
    root,
    font=custom_font,
    text="Enter URLs:")
enter_urls_label.place(x=25, y=8)

# Combobox

combobox = ttk.Combobox(
    root,
    values=["Audio", "Video"],
    state="readonly",
    width=10)
combobox.set("Audio")  # Default selection
combobox.place(x=570, y=8)

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
    border=0,
    command=settings_window)
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
add_button = Button(
    root,
    image=add_button_image,
    border=0,
    command=add)
add_button.place(x=670, y=35)

# TREEVIEW
style = ttk.Style()
style.configure("mystyle.Treeview", highlightthickness=0, bd=0, background="#CCCCCC")
style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders

# Set the colors for the treeview rows
style.configure("mystyle.Treeview.Heading", background="#CCCCCC", foreground="#000000")  # Heading row
style.map("mystyle.Treeview", background=[('selected', '#0C8AFF')])  # Selected row

columns = ('title', 'ext', 'size', 'progress', 'speed', 'status')
tree = ttk.Treeview(root, columns=columns, show='headings', height=15, style='mystyle.Treeview')

# define headings
tree.heading('title', text='Title')
tree.heading('ext', text='Ext')
tree.heading('size', text='Size')
tree.heading('progress', text='Progress')
tree.heading('speed', text='Speed')
tree.heading('status', text='Status')

# Set the width of columns
tree.column('title', anchor=CENTER, minwidth=100, width=300)
tree.column('ext', anchor=CENTER, minwidth=50, width=50)
tree.column('size', anchor=CENTER, minwidth=50, width=50)
tree.column('progress', anchor=CENTER, minwidth=70, width=70)
tree.column('speed', anchor=CENTER, minwidth=70, width=70)
tree.column('status', anchor=CENTER, minwidth=70, width=70)


tree.place(x=15, y=100, width=750)

# Scrollbars
vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
vsb.place(x=765, y=100, height=300)
tree.configure(yscrollcommand=vsb.set)

hsb = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
hsb.place(x=15, y=410, width=750)
tree.configure(xscrollcommand=hsb.set)

# Bottom row of buttons
clear_button_image = PhotoImage(file=image_paths['clear'])
clear_button = Button(
    root,
    image=clear_button_image,
    border=0,
    command=clear)
clear_button.place(x=12, y=450)

download_button_image = PhotoImage(file=image_paths['download'])
download_button = Button(
    root,
    image=download_button_image,
    border=0)
download_button.place(x=670, y=450)

root.mainloop()
