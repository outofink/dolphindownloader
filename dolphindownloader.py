"""
dolphindownloader v3
Automatically downloads the latest build of Dolphin Emulator.

"""

import os
import re
import shutil
import subprocess
import sys

import requests
from bs4 import BeautifulSoup


class DolphinDownloader():
    """Automatically downloads the latest build of Dolphin Emulator."""
    def __init__(self):
        self.link = ""
        self.filename = ""
        self.build = ""
        self.buildname = ""

    def getlatestbuild(self):
        """Gets download link and filename of the lastest build of Dolphin Emulator."""
        print("Checking latest Dolphin build...")

        page = requests.get('https://dolphin-emu.org/download')
        parsed = BeautifulSoup(page.text, "html.parser")
        link = parsed.find('a', attrs={'class':"btn always-ltr btn-info win"})['href']
        
        self.link = link
        self.filename = os.path.basename(self.link)
        self.build = re.findall(r"dolphin-master-(.*)-x64.7z", self.link).pop()
        self.buildname = "Dolphin_" + self.build

        print("Most recent build is {}.".format(self.build))

    def download(self):
        """Downloads the newest build of Dolphin."""
        link = self.link
        filename = self.filename
        #check if the build exists
        response = requests.get(link, stream=True)
        if response.headers['Content-Type'] != 'application/x-7z-compressed':
            print("Bad link. That build probably doesn't exist.")
            sys.exit(1)
        with open(filename, "wb") as archive:
            print('Downloading {}...'.format(filename))
            total = response.headers.get('content-length')

            downloaded = 0
            total = int(total)/1024/1024 # in MB
            for data in response.iter_content(chunk_size=4096):
                downloaded += len(data)/1024/1024 # in MB
                archive.write(data)
                percent = str(int(100 * downloaded / total)).rjust(3)
                percentbar = '[{}]'.format(('=' * int(int(percent)/2)).ljust(50))
                progress = f'\r{percent}% {percentbar} {downloaded:.2f}MB/{total:.2f}MB'
                sys.stdout.write(progress)
                sys.stdout.flush()
        print() # to add a newline

    def extract(self):
        """Extracts the newest build of Dolphin."""
        cmd = ['7za', 'x', '-y', self.filename]
        if not os.path.isfile("7za.exe"):
            raise FileNotFoundError("Cannot find '7za.exe'.")

        print("Extracting {}...".format(self.filename))
        process = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        process.communicate()

    def cleanup(self):
        """Removes unnecessary files."""
        os.remove(self.filename)
        if os.path.isdir(self.buildname):
            shutil.rmtree(self.buildname)
        os.rename("Dolphin-x64", self.buildname)

if __name__ == "__main__":
    dolphindownloader = DolphinDownloader()

    print("Dolphin Downloader v3")

    dolphindownloader.getlatestbuild()

    buildfile = os.path.join(dolphindownloader.buildname, "build.txt")

    if os.path.isfile(buildfile):
        with open(buildfile, "r") as text:
            if text.readline() >= dolphindownloader.build:
                print("Dolphin is up to date!")
                sys.exit(0)

    dolphindownloader.download()
    dolphindownloader.extract()
    dolphindownloader.cleanup()

    with open(buildfile, "w") as build:
        build.write(dolphindownloader.build)
