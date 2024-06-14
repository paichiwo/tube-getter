from src.media_root import MediaRoot


class CDAer(MediaRoot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add(self, url):
        self.add_media(url, 'cda')

    def download(self):
        self.download_media('cda')
