from src.resource_path import resource_path


VERSION = '2.2.2'

IMG_PATHS = {
    'icon': resource_path('images/yt3d.ico'),
    'icon_png': resource_path('images/yt3d.png'),
    'settings': resource_path('images/setting.png'),
    'github': resource_path('images/github.png'),
    'clock': resource_path('images/clock.png'),
    'eye': resource_path('images/webcam.png'),
    'calendar': resource_path('images/calendar.png'),
    'bin': resource_path('images/bin.png'),
    'folder': resource_path('images/folder.png')
}

INFO_MSG = {
    'wrong_url_err': 'ERROR: Wrong URL',
    'url_detected_err': 'ERROR: No url detected',
    'age_restricted_err': 'ERROR: Video is age restricted or Wrong URL',
    'internal_err': 'ERROR: Internal error',
    'permission_err': 'ERROR: Permission Error',
    'file_exists': 'File already downloaded',
    'dl_complete': 'Download complete',
    'converting': 'Converting video to mp3 file',
    'conversion_done': 'Conversion complete',
    'gathering_data': 'Gathering data, please wait...',
    'downloading': 'Downloading...',
}


# settings window
SETTINGS_HEADER = f'TUBE GETTER v{VERSION}\nby Paichiwo\n2023'

SETTINGS_MSG = """
Welcome to my Python-based Tube Getter. This app makes downloading video 
or audio files from YouTube and BitChute an easy and pleasant task. 
It lets you download individual files or whole playlists to a chosen location on your PC. 
I'm constantly working on the updates, but should you find any bugs 
please visit my github by clicking an icon below and open an 'issue' to let me know.
"""

GITHUB_URL = 'https://github.com/paichiwo/tube-getter'

# new version window
NEW_VERSION_MSG = 'New version available.\n\n Would you like to download it ?\n'
