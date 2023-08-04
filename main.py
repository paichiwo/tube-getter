#!/usr/bin/python3

import sys
import threading
import pytube.exceptions
import urllib.error
from datetime import datetime
from pytube import YouTube
from tkinter import Tk, ttk, Button, Entry, Label, PhotoImage, Menu, CENTER
from src.settings_window import settings_window
from src.config import version, image_paths, colors
from src.helpers import center_window, get_playlist_links, load_settings, count_file_size

# add an option to delete single item, (button, right click menu in the treeview)
# implement changing themes

yt_playlist = []
treeview_list = []
download_start_time = datetime.now()
is_on = True
file_type = 'audio'

if getattr(sys, 'frozen', False):
    import pyi_splash


def main_window():
    """Create UI elements for the main window and provide functionality"""

    def get_data_for_treeview(i_tag, output_format):
        """Return a list with data to display in the treeview"""
        treeview_list.clear()
        for url in yt_playlist:
            yt = YouTube(url)
            try:
                treeview_list.append([
                    yt.streams.get_by_itag(i_tag).title,
                    output_format,
                    f"{count_file_size(yt.streams.get_by_itag(i_tag).filesize)} MB",
                    "0 %",
                    "0 KiB/s",
                    "Queued"
                ])
            except AttributeError:
                treeview_list.append([
                    yt.streams.get_highest_resolution().title,
                    output_format,
                    f"{count_file_size(yt.streams.get_highest_resolution().filesize)} MB",
                    "0 %",
                    "0 KiB/s",
                    "Queued"
                ])
        return treeview_list

    def update_treeview(array):
        for item in array:
            tree.insert("", "end", values=item)

    def update_treeview_row(index, data):
        """Update an individual row in the treeview with new data."""
        tree.item(tree.get_children()[index], values=data)

    def download_video(playlist, output_path):
        """Download video stream - highest resolution"""
        for index, link in enumerate(playlist):
            yt = YouTube(link, on_progress_callback=progress_callback)
            yt_stream = yt.streams.get_highest_resolution()
            treeview_list[index][5] = "Downloading"
            update_treeview_row(index, treeview_list[index])
            try:
                yt_stream.download(output_path=output_path, filename=yt_stream.default_filename)
                treeview_list[index][5] = "Downloaded"
                treeview_list[index][4] = "0 KiB/s"
                update_treeview_row(index, treeview_list[index])
            except (PermissionError, RuntimeError):
                message_label.configure(text="ERROR: Permission Error.")

    def download_audio(playlist, output_path):
        """Download audio stream"""
        for index, link in enumerate(playlist):
            yt = YouTube(link, on_progress_callback=progress_callback)
            yt_stream = yt.streams.get_audio_only()
            treeview_list[index][5] = "Downloading"
            update_treeview_row(index, treeview_list[index])
            # change an extension to mp3 if mp4 audio downloaded.
            if yt_stream.mime_type == "audio/mp4":
                filename = yt_stream.default_filename.rsplit(".", 1)[0] + ".mp3"
            else:
                filename = yt_stream.default_filename
            try:
                yt_stream.download(output_path=output_path, filename=filename)
                treeview_list[index][5] = "Downloaded"
                treeview_list[index][4] = "0 KiB/s"
                update_treeview_row(index, treeview_list[index])
            except (PermissionError, RuntimeError):
                message_label.configure(text="ERROR: Permission Error.")

    def progress_callback(stream, chunk, bytes_remaining):
        """Update the progress and speed values in the treeview list"""
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100

        elapsed_time = (datetime.now() - download_start_time).total_seconds()
        download_speed = bytes_downloaded / (1024 * elapsed_time)

        for item in treeview_list:
            if item[0] == stream.title:
                item[3] = f"{percentage:.2f} %"
                if download_speed < 1000:
                    item[4] = f"{download_speed:.2f} KiB/s"
                else:
                    item[4] = f"{download_speed / 1024:.2f} MiB/s"
                break
        # Update the specific row directly
        index = [i for i, item in enumerate(treeview_list) if item[0] == stream.title]
        if index:
            update_treeview_row(index[0], treeview_list[index[0]])

    def download():
        """Download video or audio action when the download button is pressed"""

        def download_task():
            output_path = load_settings()
            if file_type == 'audio':
                download_audio(yt_playlist, output_path)
            else:
                download_video(yt_playlist, output_path)  # Always download video if switch is off
            message_label.configure(text="Download complete.")

        download_thread = threading.Thread(target=download_task)
        download_thread.start()

    def clear_treeview():
        """Clear all rows in the treeview"""
        for entry in tree.get_children():
            tree.delete(entry)

    def clear():
        """Clear all data from the list and the treeview"""
        yt_playlist.clear()
        clear_treeview()

    def switch():
        """Switches the file type between 'audio' and 'video' and updates the treeview accordingly"""
        global is_on
        global file_type
        clear_treeview()
        treeview_list.clear()
        if is_on:
            on_button.config(image=switch_right)
            is_on = False
            file_type = 'video'
            data = get_data_for_treeview(22, 'mp4')
        else:
            on_button.config(image=switch_left)
            is_on = True
            file_type = 'audio'
            data = get_data_for_treeview(140, 'mp3')
        update_treeview(data)

    def add():
        """Add youtube link or youtube playlist to queue"""
        url = url_entry.get()
        treeview_list.clear()
        clear_treeview()
        if url:
            try:
                if is_on:
                    get_playlist_links(url, yt_playlist)
                    data = get_data_for_treeview(140, 'mp3')
                else:
                    get_playlist_links(url, yt_playlist)
                    data = get_data_for_treeview(22, 'mp4')
                update_treeview(data)
            except pytube.exceptions.VideoUnavailable:
                message_label.configure(text="ERROR: Video is age restricted.")
            except pytube.exceptions.RegexMatchError:
                message_label.configure(text="ERROR: Wrong URL.")
            except (urllib.error.URLError, urllib.error.HTTPError):
                message_label.configure(text="ERROR: Internal error.")
        else:
            message_label.configure(text="No url detected.")

    # Menu functions
    def on_url_entry_right_click(event):
        try:
            url_entry_right_click_menu.post(event.x_root, event.y_root)
        finally:
            url_entry_right_click_menu.grab_release()

    def paste_url():
        """Handle the 'Paste' option for the url_entry"""
        clipboard_text = root.clipboard_get()
        url_entry.insert('end', clipboard_text)

    def delete_url():
        """Handle the 'Delete' option for the url_entry"""
        url_entry.delete(0, "end")

    root = Tk()
    root.iconbitmap(bitmap=image_paths['icon'])
    root.title(f"Tube Getter v{version}")
    center_window(root, 800, 500)
    root.resizable(False, False)

    # UI Elements

    # Enter Urls label:
    enter_urls_label = Label(
        root,
        text="Enter URLs:")
    enter_urls_label.place(x=25, y=12)

    # SWITCH for 'audio' / 'video'
    switch_left = PhotoImage(file=image_paths['switch_left'])
    switch_right = PhotoImage(file=image_paths['switch_right'])
    on_button = Button(
        root,
        image=switch_left,
        bd=0,
        command=switch)
    on_button.place(x=670, y=8)

    # THEME button
    theme_button_image = PhotoImage(file=image_paths['theme'])
    theme_button = Button(
        root,
        image=theme_button_image,
        bd=0)
    theme_button.place(x=740, y=8)

    # SETTINGS button
    settings_button_image = PhotoImage(file=image_paths['settings'])
    settings_button = Button(
        root,
        image=settings_button_image,
        bd=0,
        command=settings_window)
    settings_button.place(x=765, y=8)

    # URL entry
    entry_image = PhotoImage(file=image_paths['entry'])
    entry_label = Label(root, image=entry_image)
    entry_label.place(x=12, y=35)
    url_entry = Entry(
        root,
        bg=colors[0],
        bd=0)
    url_entry.place(x=25, y=45, width=615)
    # Right click menu
    url_entry_right_click_menu = Menu(root, tearoff=0)
    url_entry_right_click_menu.add_command(label="Paste", command=paste_url)
    url_entry_right_click_menu.add_command(label="Clear", command=delete_url)
    # Bind right mouse button
    url_entry.bind('<Button-3>', on_url_entry_right_click)
    # Bind the Enter key
    url_entry.bind('<Return>', lambda event: add())
    # Bind CTRL+Z
    url_entry.bind('<Control-z>', lambda event: delete_url())

    # ADD button
    add_button_image = PhotoImage(file=image_paths['add'])
    add_button = Button(
        root,
        image=add_button_image,
        bd=0,
        command=add)
    add_button.place(x=670, y=35)

    # TREEVIEW
    style = ttk.Style()
    style.configure("mystyle.Treeview", highlightthickness=0, bd=0, background="#CCCCCC")
    style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])  # Remove the borders

    style.configure("mystyle.Treeview.Heading", background="#CCCCCC", foreground="#000000")  # Heading row
    style.map("mystyle.Treeview", background=[('selected', '#0C8AFF')])  # Selected row

    columns = ('title', 'ext', 'size', 'progress', 'speed', 'status')
    tree = ttk.Treeview(root, columns=columns, show='headings', height=16, style='mystyle.Treeview')

    # define headings
    tree.heading('title', text='Title')
    tree.heading('ext', text='Ext')
    tree.heading('size', text='Size')
    tree.heading('progress', text='Progress')
    tree.heading('speed', text='Speed')
    tree.heading('status', text='Status')

    # Set the width of columns
    tree.column('title', anchor=CENTER, minwidth=150, width=300)
    tree.column('ext', anchor=CENTER, minwidth=30, width=30)
    tree.column('size', anchor=CENTER, minwidth=30, width=30)
    tree.column('progress', anchor=CENTER, minwidth=30, width=30)
    tree.column('speed', anchor=CENTER, minwidth=30, width=30)
    tree.column('status', anchor=CENTER, minwidth=50, width=50)

    tree.place(x=15, y=85, width=750)

    # Treeview Scrollbars
    vsb = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    vsb.place(x=765, y=100, height=325)
    tree.configure(yscrollcommand=vsb.set)

    # CLEAR button
    clear_button_image = PhotoImage(file=image_paths['clear'])
    clear_button = Button(
        root,
        image=clear_button_image,
        bd=0,
        command=clear)
    clear_button.place(x=12, y=440)

    # DOWNLOAD button
    download_button_image = PhotoImage(file=image_paths['download'])
    download_button = Button(
        root,
        image=download_button_image,
        bd=0,
        command=download)
    download_button.place(x=670, y=440)

    # MESSAGE label
    message_label = Label(text="")
    message_label.place(x=12, y=478)

    if getattr(sys, 'frozen', False):
        pyi_splash.close()

    root.mainloop()


if __name__ == "__main__":
    main_window()
