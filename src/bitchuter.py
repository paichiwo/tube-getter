
from src.media_root import MediaRoot


class Bitchuter(MediaRoot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add(self, url):
        self.add_media(url, 'bitchute')

    def download(self):
        self.download_media('bitchute')
