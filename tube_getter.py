import customtkinter as ctk
import tkinter as tk
from PIL import ImageTk, Image

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.geometry("500x350")


def theme_toggle():
    current_theme = ctk.get_appearance_mode()
    print(current_theme)
    if current_theme == "Dark":
        ctk.set_appearance_mode("Light")
        theme_button.config(background="#FFFFFF")
    else:
        ctk.set_appearance_mode("Dark")
        theme_button.config(background="#262626")



label = ctk.CTkLabel(master=root, text="YouTube Getter")
label.pack(pady=12, padx=10)

theme_image = tk.PhotoImage(file="./images/dark.png")
theme_button = tk.Button(master=root,
                         image=theme_image,
                         borderwidth=0,
                         command=theme_toggle)
theme_button.pack(pady=12, padx=10)

root.mainloop()
