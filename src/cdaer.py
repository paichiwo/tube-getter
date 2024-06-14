from src.media_root import MediaRoot


class CDAer(MediaRoot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_cda(self, url):
        self.add_media(url, 'cda')

    def cda_download(self):
        self.download_media('cda')
