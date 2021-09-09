import os
import pytube
import requests
from bs4 import BeautifulSoup
from swinlnk.swinlnk import SWinLnk
import shutil
import itertools
import threading
import time
import sys


class Downloader:
    def __init__(self, p_href):
        self._running = True
        self._href = p_href

    def terminate(self):
        self._running = False

    def animate(self):
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if not self._running:
                break
            sys.stdout.write('\rDownloading ' + self._href + ' ' + c)
            sys.stdout.flush()
            time.sleep(0.1)

        sys.stdout.flush()
        print('\rCompleted   ' + self._href + '  ', flush=True)

    def download(self):
        video = pytube.YouTube(self._href)
        name = video.title.replace('|', '').replace(',', '') + '.mp4'
        videos[href] = name

        if not os.path.exists(video_dir + '/' + name):
            video.streams.get_highest_resolution().download(video_dir)

        self.terminate()


website = 'https://chloeting.com/program/2021/weight-loss-challenge.html'

# Hide cursor
print("\x1b[?25l")

swl = SWinLnk()
main_dir = os.path.dirname(os.path.realpath(__file__))

program_dir = 'Program/'
video_dir = 'Video/'
if os.path.exists(program_dir):
    shutil.rmtree(program_dir)

os.mkdir(program_dir)

# Parse web page
response = requests.get(website)
html = BeautifulSoup(response.text, 'html.parser')

# Scraping
div_videos = html.find_all('div', class_="videos")

href_list = []
program = []
videos = {}

# Loop on div with videos class
for div in div_videos:
    day = []
    for child in div.findChildren('a'):

        # Ignore optional video
        if child.findChildren('div', class_="video optional"):
            continue

        href = child['href']
        day.append(href)

        if href not in href_list:
            href_list.append(href)

    program.append(day)

# Loop on all href
for href in href_list:
    d = Downloader(href)
    t = threading.Thread(target=d.animate)
    t.start()

    d.download()

    # Wait for thread to complete
    t.join()

# Loop on program
for i, day in enumerate(program):
    dir_name = 'Program/Day ' + str(i+1)
    # Rest day
    if len(day) == 0:
        dir_name = 'Program/Day ' + str(i + 1) + ' - rest'
    os.mkdir(dir_name)

    # Loop on days
    for j, href in enumerate(day):
        source = main_dir + '/Video/' + videos[href]
        link = main_dir + '/' + dir_name + '/' + str(j+1) + '. ' + videos[href] + '.lnk'
        # Create links
        swl.create_lnk(source, link)
