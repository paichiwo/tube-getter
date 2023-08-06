import webbrowser
from tkinter import Tk, Label, PhotoImage, Button, Frame, filedialog
from src.config import image_paths, settings_header, settings_message, colors, github_url
from src.helpers import save_settings, load_settings


def settings_window():
    """Display the settings window"""
    def get_output_path():
        """Get an output folder path to display it in the output_folder_label"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            output_folder_value.configure(text=folder_selected)

    def close_window():
        """Save settings to .json file and close the settings window"""
        output_path = output_folder_value.cget('text')
        save_settings(output_path)
        sett.destroy()

    sett = Tk()
    sett.iconbitmap(bitmap=image_paths['icon'])
    sett.title("Settings")
    sett.geometry('500x450+400+200')
    sett.resizable(False, False)

    # Create top frame and bottom frame
    top_frame = Frame(sett)
    top_frame.pack()
    bot_frame = Frame(sett)
    bot_frame.pack()

    # TOP FRAME
    logo_image = PhotoImage(master=sett, file=image_paths['icon_png'])
    logo_label = Label(top_frame, image=logo_image)
    logo_label.pack()

    header_label = Label(top_frame, text=settings_header)
    header_label.pack()

    message_label = Label(top_frame, text=settings_message)
    message_label.pack()

    github_image = PhotoImage(master=sett, file=image_paths['github'])
    github_label = Label(
        top_frame,
        image=github_image,
        cursor='hand2')
    github_label.pack()
    github_label.bind("<Button-1>", lambda _: webbrowser.open(github_url))
    github_link = Label(
        top_frame,
        text="GitHub link\n",
        cursor='hand2')
    github_link.pack()
    github_label.bind("<Button-1>", lambda _: webbrowser.open(github_url))

    # BOTTOM FRAME
    output_folder_label = Label(bot_frame, text="Choose output folder:")
    output_folder_label.pack()
    entry_small_image = PhotoImage(master=sett, file=image_paths['entry_small'])
    entry_small_label = Label(bot_frame, image=entry_small_image)
    entry_small_label.pack()
    output_folder_value = Label(
        bot_frame,
        text=f"{load_settings()}",
        anchor='w',
        bg=colors[0],
        width=48)
    output_folder_value.place(x=15, y=29)
    browse_button_image = PhotoImage(master=sett, file=image_paths['folder'])
    browse_button_button = Button(
        bot_frame,
        image=browse_button_image,
        bg=colors[0],
        activebackground=colors[0],
        border=0,
        command=get_output_path)
    browse_button_button.place(x=370, y=30)

    close_button_image = PhotoImage(master=sett, file=image_paths['close'])
    close_button_button = Button(
        bot_frame,
        image=close_button_image,
        border=0,
        command=close_window)
    close_button_button.pack(padx=10, pady=10)

    sett.mainloop()
