"""
dolphindownloader v3
A tool which downloads a specified (or the lastest) build of Dolphin Emulator.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys

import requests
from bs4 import BeautifulSoup


class DolphinDownloader():
    """A tool which downloads a specified (or the lastest) build of Dolphin Emulator."""
    def __init__(self):
        self.link = ""
        self.filename = ""
        self.build = ""
        self.buildname = ""

    def getlatestbuild(self):
        """Gets download link and filename of the lastest build of Dolphin."""
        print("Checking latest Dolphin build...")
        try:
            page = requests.get('https://dolphin-emu.org/download')
            page.raise_for_status()
        except requests.exceptions.RequestException as error:
            print("Failed to connect. Check your internet connection.")
            sys.exit(1)

        parsed = BeautifulSoup(page.text, "html.parser")
        link = parsed.find('a', attrs={'class':"btn always-ltr btn-info win"})['href']
        
        self.link = link
        self.filename = os.path.basename(self.link)
        self.build = re.findall(r"dolphin-master-(.*)-x64.7z", self.link).pop()
        self.buildname = "Dolphin_" + self.build

        print("Most recent build is {}.".format(self.build))

    def getbuild(self, build):
        """Gets download link and filename of a specified build of Dolphin Emulator."""
        self.link = "https://dl.dolphin-emu.org/builds/dolphin-master-{}-x64.7z".format(build)
        self.filename = os.path.basename(self.link)
        self.build = build
        self.buildname = "Dolphin_" + self.build

        print("Attempting to download build {}...".format(self.build))

    def download(self):
        """Downloads a build of Dolphin."""
        link = self.link
        filename = self.filename
        #check if the build exists
        try:
            response = requests.get(link, stream=True)
            response.raise_for_status()
        except requests.exceptions.HTTPError as error:
            print(error)
            print("That build probably doesn't exist.")
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
        """Extracts Dolphin .7z archive."""
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

    def run(self):
        subprocess.Popen(os.path.join(self.buildname, "Dolphin.exe"))

def validbuild(build, regex=re.compile('^\d\.(0|5)-\d{1,4}$')):
    if not regex.match(build):
        raise argparse.ArgumentTypeError("Invalid build format. Try something like 5.0-4839.")
    return build

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Downloads a specified (or the lastest) build of Dolphin Emulator.')
    parser.add_argument("-q", "--quiet", action="store_true", help="disables commandline output")
    parser.add_argument("-r", "--run", action="store_true", help="run Dolphin Emulator after downloading")
    parser.add_argument("-b", "--build", type=validbuild, help="specify build version to download")

    args = parser.parse_args()
    if args.quiet:
        sys.stdout = open(os.devnull, 'w')

    dolphindownloader = DolphinDownloader()
    print("Dolphin Downloader v3")

    if args.build:
        dolphindownloader.getbuild(args.build)
    else:
        dolphindownloader.getlatestbuild()

    buildfile = os.path.join(dolphindownloader.buildname, ".build")

    if os.path.isfile(buildfile):
        with open(buildfile, "r") as text:
            if text.readline() >= dolphindownloader.build:
                print("Dolphin is up to date!")
                if args.run: dolphindownloader.run()
                sys.exit(0)

    dolphindownloader.download()
    dolphindownloader.extract()
    dolphindownloader.cleanup()

    with open(buildfile, "w") as build:
        build.write(dolphindownloader.build)

    if args.run: dolphindownloader.run()
