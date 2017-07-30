"""
dolphindownloader v2
Automatically downloads the latest version of Dolphin Emulator.

"""

import os
import re
import shutil
import subprocess
import sys

import requests
from bs4 import BeautifulSoup


class DolphinDownloader():
    """Automatically downloads the latest version of Dolphin Emulator."""
    def __init__(self):
        self.link = ""
        self.filename = ""
        self.version = ""
        self.versionname = ""

    def getnewestversion(self):
        """Gets download link, filename, and version of the newest version of Dolphin Emulator."""
        page = requests.get('https://dolphin-emu.org/download')
        parsed = BeautifulSoup(page.text, "html.parser")
        link = parsed.find('a', attrs={'class':"btn always-ltr btn-info win"})['href']

        self.link = link
        self.filename = os.path.basename(self.link)
        self.version = re.findall(r"dolphin-master-(.*)-x64.7z", self.link).pop()
        self.versionname = "Dolphin_" + self.version

    def download(self):
        """Downloads the newest build of Dolphin."""
        link = self.link
        filename = self.filename
        with open(filename, "wb") as archive:
            print('Downloading {}...'.format(filename))
            response = requests.get(link, stream=True)
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
        print("Cleaning up...")
        os.remove(self.filename)
        if os.path.isdir(self.versionname):
            shutil.rmtree(self.versionname)
        os.rename("Dolphin-x64", self.versionname)

if __name__ == "__main__":
    dolphindownloader = DolphinDownloader()

    print("Dolphin Downloader v2")
    print("Retrieving most recent Dolphin build version...")

    dolphindownloader.getnewestversion()

    print("Most recent version is {}.".format(dolphindownloader.version))

    versionfile = os.path.join(dolphindownloader.versionname, "version.txt")

    if os.path.isfile(versionfile):
        with open(versionfile, "r") as text:
            if text.readline() >= dolphindownloader.version:
                print("Dolphin is up to date!")
                sys.exit(0)

    dolphindownloader.download()
    dolphindownloader.extract()
    dolphindownloader.cleanup()

    with open(versionfile, "w") as version:
        version.write(dolphindownloader.version)
