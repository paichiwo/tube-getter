import os
import time
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

    def __get_video_src(self, quality):

        self.__driver.get(self.__url + self.__quality_urls[quality])
        page = self.__driver.page_source

        if page:
            soup = BeautifulSoup(page, 'html.parser')
            video_tag = soup.find('video', class_='pb-video-player')
            if video_tag:
                src = video_tag.get('src')
                return src
        return None

    def __find_best_quality(self):
        for quality in self.__qualities:
            target = self.__get_video_src(quality)
            print(target)
            if target and len(target.split('/')[-1]) > 4:
                return target
        return None

    @staticmethod
    def __download_video(target, filename='cda_file.mp4', on_progress_callback=None):
        if not os.path.exists(filename):
            print('Downloading...')
            urllib.request.urlretrieve(target, filename, reporthook=on_progress_callback)
        else:
            print('File already downloaded')

    def download(self, filename='cda_file.mp4', on_progress_callback=None):
        target = self.__find_best_quality()
        if target:
            print(f"Found video URL: {target}")
            if not os.path.exists(filename):
                print('Downloading...')
                urllib.request.urlretrieve(target, filename, reporthook=on_progress_callback)
            else:
                print('File already downloaded')
        else:
            print("No valid video URL found.")
        self.__driver.quit()


if __name__ == '__main__':

    start_time = time.time()

    def report_hook(count, block_size, total_size):
        # progress percentage
        progress = min(1.0, float(count * block_size) / total_size)
        print(f'progress: {progress:.2f}')

        # download speed
        elapsed_time = time.time() - start_time
        if elapsed_time > 0:
            speed = (count * block_size) / (1024 * elapsed_time)  # speed in KB/s
            print(f'Download speed: {speed:.2f} KB/s')

    url1 = 'https://www.cda.pl/video/14967539bc'
    url2 = 'https://www.cda.pl/video/192935076e'
    url3 = 'https://www.cda.pl/video/295066274/'

    cda = PyCDA(url1)
    cda.download(on_progress_callback=report_hook)
