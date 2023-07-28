import threading
from datetime import datetime
import pytube.exceptions
import urllib.error
from pytube import YouTube
from tkinter import Tk, ttk, Button, Entry, Label, PhotoImage, CENTER
from src.settings_window import settings_window
from src.config import version, image_paths, colors
from src.helpers import center_window, get_playlist_links, load_settings, count_file_size

yt_playlist = []
treeview_list = []
download_start_time = datetime.now()


def main_window():
    """Create UI elements for the main window and provide functionality"""

    def get_data_for_treeview(i_tag, output_format, yt_list):
        """Return a list with data to display in the treeview"""
        treeview_list.clear()
        for url in yt_list:
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
            try:
                yt_stream.download(output_path=output_path, filename=yt_stream.default_filename)
            except (PermissionError, RuntimeError):
                print("ERROR: Permission Error.")

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
                print("ERROR: Permission Error.")

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
            file_type = combobox.get()
            if file_type == "Audio":
                download_audio(yt_playlist, output_path)
            else:
                download_video(yt_playlist, output_path)
            print("Download complete.")

        download_thread = threading.Thread(target=download_task)
        download_thread.start()

    def clear():
        """Clear all data from the list and the treeview"""
        yt_playlist.clear()
        for entry in tree.get_children():
            tree.delete(entry)

    def add():
        """Add youtube link or youtube playlist to queue"""
        url = url_entry.get()
        file_type = combobox.get()
        treeview_list.clear()
        if url:
            try:
                get_playlist_links(url, yt_playlist)
                if file_type == "Audio":
                    data = get_data_for_treeview(140, 'mp3', yt_playlist)
                    update_treeview(data)
                else:
                    data = get_data_for_treeview(22, 'mp4', yt_playlist)
                    update_treeview(data)
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

    # Enter Urls label:
    enter_urls_label = Label(
        root,
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
        border=0,
        command=download)
    download_button.place(x=670, y=450)

    root.mainloop()


if __name__ == "__main__":
    main_window()
