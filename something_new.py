#!/usr/bin/env python3

import os
import io
import sys
import base64
import requests
import PySimpleGUI as psg
import messages
from PIL import Image
from pytube import YouTube
from pytube.exceptions import VideoUnavailable


def resource_path(relative_path):
    """PyInstaller requirement,
    Get an absolute path to resource, works for dev and for PyInstaller."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


version = "1.1"
themes = ["LightGrey", "DarkGrey4"]
colors = ["white", "#52524E"]
font = resource_path("./fonts/Poppins-Regular.ttf")


def justified_popup():
    layout = [[psg.Image(filename=resource_path("./images/youtube.png"))],
              [psg.Text(f"YOUTUBE GETTER v{version}\nby Paichiwo\n2023\n\n{messages.popup_message}", justification='c')],
              [psg.Button('OK')]]
    window = psg.Window("Information",
                        layout,
                        element_justification='c',
                        icon=resource_path("./images/youtube.png"))
    event, values = window.read()
    window.close()


def create_window(theme):
    """Application layout for PySimpleGUI."""
    psg.theme(theme)
    layout = [
        [psg.Push(),
         psg.Button(image_filename=resource_path("./images/close.png"),
                    button_color="white",
                    border_width=0,
                    k="-CLOSE-")],
        [psg.Text("YouTube Getter", font=(font, 10)),
         psg.Push(),
         psg.Button(image_filename=resource_path("./images/dark.png"),
                    button_color="white",
                    border_width=0,
                    k="-THEME-"),
         psg.Button(image_filename=resource_path("./images/settings.png"),
                    button_color="white",
                    border_width=0,
                    k="-SETTINGS-")],
    ]
    return psg.Window(f"YouTube Getter v{version}",
                      layout=layout,
                      size=(800, 500),
                      element_justification="center",
                      no_titlebar=True,
                      grab_anywhere=True,
                      finalize=True)


def main():
    """Main function for the YouTube Getter application."""
    window = create_window(themes[0])
    themes_counter = 1
    while True:
        event, values = window.read()
        if event == psg.WIN_CLOSED or event == "-CLOSE-":
            break

        if event == "-THEME-":
            theme = themes[themes_counter % len(themes)]
            color = colors[themes_counter % len(themes)]
            window.close()
            window = create_window(theme)
            window["-SETTINGS-"].update(button_color=color)
            window["-THEME-"].update(button_color=color)
            window["-CLOSE-"].update(button_color=color)
            themes_counter += 1

        if event == "-SETTINGS-":

            justified_popup()


    window.close()


if __name__ == "__main__":
    main()
