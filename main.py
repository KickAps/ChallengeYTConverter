import os
import pytube
import requests
from bs4 import BeautifulSoup
from swinlnk.swinlnk import SWinLnk
import shutil
import re

swl = SWinLnk()
main_dir = os.path.dirname(os.path.realpath(__file__))

dir_name = 'Program'
if os.path.exists(dir_name):
    shutil.rmtree(dir_name)

os.mkdir(dir_name)

website = 'https://chloeting.com/program/2021/weight-loss-challenge.html'

response = requests.get(website)
html = BeautifulSoup(response.text, 'html.parser')
href_list = []
program = []
videos = {}

div_videos = html.find_all('div', class_="videos")
for div in div_videos:
    day = []
    for child in div.findChildren('a'):
        if child.findChildren('div', class_="video optional"):
            continue

        href = child['href']
        day.append(href)

        if href not in href_list:
            href_list.append(href)

    program.append(day)

for href in href_list:
    print(href)
    youtube = pytube.YouTube(href)
    name = youtube.title.replace('|', '').replace(',', '') + '.mp4'
    path = 'Video'
    videos[href] = name

    if not os.path.exists(path + '/' + name):
        video = youtube.streams.get_highest_resolution()
        path = video.download(path)
        #videos[href] = re.search(r'[^\\\\]*\.mp4$', path).group(0)

for i, day in enumerate(program):
    dir_name = 'Program/Day ' + str(i+1)
    if len(day) == 0:
        dir_name = 'Program/Day ' + str(i + 1) + ' - rest'
    os.mkdir(dir_name)

    for j, href in enumerate(day):
        source = main_dir + '/Video/' + videos[href]
        dest = main_dir + '/' + dir_name + '/' + str(j+1) + '. ' + videos[href] + '.lnk'
        swl.create_lnk(source, dest)
