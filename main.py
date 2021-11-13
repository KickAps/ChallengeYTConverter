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
import getopt


class Converter:
    def __init__(self, p_website, p_hd, p_force):
        self._website = p_website
        self._program_dir = 'Program/'
        self._href_list = []
        self._program = []
        self.hd = p_hd
        self.force = p_force
        self.video_dir = 'Video/'
        self.video_only_dir = 'Video/video_only/'
        self.audio_only_dir = 'Video/audio_only/'
        self.videos = {}

    def convert(self):
        swl = SWinLnk()
        main_dir = os.path.dirname(os.path.realpath(__file__))

        if os.path.exists(self._program_dir):
            shutil.rmtree(self._program_dir)

        os.mkdir(self._program_dir)

        # Parse web page
        response = requests.get(self._website)
        html = BeautifulSoup(response.text, 'html.parser')

        # Scraping
        div_videos = html.find_all('div', class_="videos")

        # Loop on div with videos class
        for div in div_videos:
            day = []
            for child in div.findChildren('a'):

                # Ignore optional video
                if child.findChildren('div', class_="video optional"):
                    continue

                href = child['href']
                day.append(href)

                if href not in self._href_list:
                    self._href_list.append(href)

            self._program.append(day)

        # Loop on all href
        for href in self._href_list:
            d = Downloader(href)
            t = threading.Thread(target=d.animate)
            t.start()

            d.download(self)

            # Wait for thread to complete
            t.join()

        # Loop on program
        for i, day in enumerate(self._program):
            dir_name = 'Program/Day ' + str(i + 1)
            # Rest day
            if len(day) == 0:
                dir_name = 'Program/Day ' + str(i + 1) + ' - rest'
            os.mkdir(dir_name)

            # Loop on days
            for j, href in enumerate(day):
                source = main_dir + '/Video/' + self.videos[href]
                link = main_dir + '/' + dir_name + '/' + str(j + 1) + '. ' + self.videos[href] + '.lnk'
                # Create links
                swl.create_lnk(source, link)


class Downloader:
    def __init__(self, p_href):
        self._running = True
        self._href = p_href
        self._name = ''

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
        print('\rCompleted   ' + self._href + '  ' + self._name, flush=True)

    def download(self, c):
        video = pytube.YouTube(self._href)
        name = video.title.replace('|', '').replace(',', '')
        name = ''.join(e for e in name if e.isascii())
        name = name.strip()
        video.title = name
        if c.hd:
            self._name = name + '.webm'
        else:
            self._name = name + '.mp4'

        c.videos[self._href] = self._name

        if os.path.exists(c.video_dir + '/' + name + '.webm') and c.force:
            os.remove(c.video_dir + '/' + name + '.webm')
        if os.path.exists(c.video_dir + '/' + name + '.mp4') and c.force:
            os.remove(c.video_dir + '/' + name + '.mp4')

        if not os.path.exists(c.video_dir + '/' + self._name):
            if c.hd:
                if not os.path.exists(c.video_only_dir + '/' + self._name):
                    video.streams.filter(progressive=False, file_extension='webm').order_by('resolution').last().download(c.video_only_dir)
                if not os.path.exists(c.audio_only_dir + '/' + self._name):
                    video.streams.filter(only_audio=True).order_by('bitrate').last().download(c.audio_only_dir)
                os.system(
                    'ffmpeg -hide_banner -loglevel error -i "' +
                    c.audio_only_dir + '/' + self._name + '" -i "' +
                    c.video_only_dir + '/' + self._name + '" -async 1 -c copy "' +
                    c.video_dir + '/' + self._name + '"')
            else:
                video.streams.get_highest_resolution().download(c.video_dir)

        self.terminate()


def main(argv):
    # Examples :
    # https://chloeting.com/program/2021/weight-loss-challenge.html
    # https://chloeting.com/program/2021/get-fit-challenge.html
    website = ""
    hd = False
    force = False

    help_msg = 'main.py -w <website_url> --hd -f'

    try:
        opts, args = getopt.getopt(argv, "hw:f", ["hd"])
    except getopt.GetoptError:
        print(help_msg)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(help_msg)
            sys.exit()
        elif opt == "-w":
            website = arg
        elif opt == "--hd":
            hd = True
        elif opt == "-f":
            force = True

    if website == '':
        print(help_msg)
        sys.exit(2)

    print('Website : ', website)
    print('Quality : ', hd)
    print('Force : ', force)
    c = Converter(website, hd, force)
    c.convert()


if __name__ == "__main__":
    # Hide cursor
    print("\x1b[?25l")

    main(sys.argv[1:])

    # Show cursor
    print("\x1b[?25h")
