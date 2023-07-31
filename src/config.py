from src.helpers import resource_path

version = "1.2"

image_paths = {
    'theme': resource_path('../images/icons_black/sun.png'),
    'settings': resource_path('../images/icons_black/setting.png'),
    'entry': resource_path('../images/entry.png'),
    'entry_small': resource_path('../images/entry_small.png'),
    'folder': resource_path('../images/folder.png'),
    'add': resource_path('../images/button_add.png'),
    'clear': resource_path('../images/button_clear.png'),
    'download': resource_path('../images/button_download.png'),
    'close': resource_path('../images/button_close.png'),
    'icon': resource_path('../images/yt3d.ico'),
    'icon_png': resource_path('../images/yt3d.png'),
    'github': resource_path('../images/github.png'),
    'switch_left': resource_path('../images/switch_left.png'),
    'switch_right': resource_path('../images/switch_right.png')
}
font_size = 10

colors = ['#CCCCCC', '#0C8AFF']

settings_header = f"TUBE GETTER v{version}\nby Paichiwo\n2023"

settings_message = """
The Python-based Tube Getter enables users to download video or
audio files from YouTube with ease. The user interface is built using
the PySimpleGUI library, while the PyTube library is used to
implement the video/audio downloading functionality. With a user-friendly
design, it offers a hassle-free method to obtain desired YouTube content.
"""

github_url = "https://github.com/paichiwo"
