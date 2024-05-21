import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib.request

url1 = 'https://www.cda.pl/video/213378f7'
url2 = 'https://www.cda.pl/video/5044781ea'

USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:48.0) Gecko/20100101 Firefox/48.0'

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument(f'user-agent={USER_AGENT}')
driver = webdriver.Chrome(options=options)

qualities = ['1080', '720', '480', '360']
quality_urls = {q: f'/vfilm?wersja={q}p' for q in qualities}


def get_video_src(quality):
    driver.get(url2 + quality_urls[quality])
    page = driver.page_source
    if page:
        soup = BeautifulSoup(page, 'html.parser')
        video_tag = soup.find('video', class_='pb-video-player')
        if video_tag:
            src = video_tag.get('src')
            return src
    return None


target = None

for quality in qualities:
    target = get_video_src(quality)
    print(target)
    if target and len(target.split('/')[-1]) > 4:
        break

if target:
    print(f"Found video URL: {target}")
    # Uncomment the following line to download the video
    # urllib.request.urlretrieve(target, 'aaa.mp4')
else:
    print("No valid video URL found.")

driver.quit()
