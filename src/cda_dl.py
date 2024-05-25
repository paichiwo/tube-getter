import os
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver


class PyCDA:
    def __init__(self, url):
        self.__url = url
        self.__user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:48.0) Gecko/20100101 Firefox/48.0'
        self.__qualities = ['1080', '720', '480', '360']
        self.__quality_urls = {q: f'/vfilm?wersja={q}p' for q in self.__qualities}

        self.__options = webdriver.ChromeOptions()
        self.__options.add_argument('headless')
        self.__options.add_argument(f'user-agent={self.__user_agent}')
        self.__driver = webdriver.Chrome(options=self.__options)

    def get_video_src(self, quality):
        self.__driver.get(self.__url + self.__quality_urls[quality])
        page = self.__driver.page_source
        if page:
            soup = BeautifulSoup(page, 'html.parser')
            video_tag = soup.find('video', class_='pb-video-player')
            if video_tag:
                src = video_tag.get('src')
                return src
        return None

    def find_best_quality(self):
        for quality in self.__qualities:
            target = self.get_video_src(quality)
            if target and len(target.split('/')[-1]) > 4:
                return target
        return None

    def download_video(self, target, filename='cda_file.mp4', on_progress_callback=None):
        if not os.path.exists(filename):
            print('Downloading...')
            urllib.request.urlretrieve(target, filename, reporthook=on_progress_callback)
        else:
            print('File already downloaded')

    def run(self, filename='cda_file.mp4', on_progress_callback=None):
        target = self.find_best_quality()
        if target:
            print(f"Found video URL: {target}")
            self.download_video(target, filename, on_progress_callback)
        else:
            print("No valid video URL found.")
        self.__driver.quit()


if __name__ == '__main__':
    url = 'https://www.cda.pl/video/14967539bc'
    cda = CdaDL(url)
    cda.run()
