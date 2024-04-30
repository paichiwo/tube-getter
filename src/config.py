from src.helpers import resource_path


VERSION = '1.2.9'

IMG_PATHS = {
    'settings': resource_path('images/setting.png'),
    'icon': resource_path('images/yt3d.ico'),
    'icon_png': resource_path('images/yt3d.png'),
    'github': resource_path('images/github.png'),
    'switch_left': resource_path('images/switch_left.png'),
    'switch_right': resource_path('images/switch_right.png'),

    'clock': resource_path('images/test/clock.png'),
    'eye': resource_path('images/test/webcam.png'),
    'calendar': resource_path('images/test/calendar.png'),
    'bin': resource_path('images/test/bin.png'),
}


# settings window
SETTINGS_HEADER = f'TUBE GETTER v{VERSION}\nby Paichiwo\n2023'

SETTINGS_MSG = """
Welcome to my Python-based Tube Getter. This app makes downloading video 
or audio files from YouTube an easy and pleasant task. It lets you download 
individual files or whole playlists to a chosen location on your PC. 
I'm constantly working on updates, but should you find any bugs 
please visit my github by clicking an icon below and open an 'issue' to let me know.
"""

GITHUB_URL = "https://github.com/paichiwo/tube-getter"
