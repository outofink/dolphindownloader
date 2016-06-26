"""
dolphindownloader v1.1.1
Automatically downloads the latest version of [Dolphin Emulator](https://dolphin-emu.org/).

## Requirements
* Python 3.x
* BeautifulSoup
* 7zip (specifically `7za.exe`)

"""

import os
import re
import shutil
import subprocess
import sys
import time

from urllib.error import HTTPError, URLError
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as BS

def getversion():
    try:
        dolphinBS = BS(urlopen(Request('https://dolphin-emu.org/download')).read(), "html.parser")
    except URLError:
        print("\nERROR: Not connected to the internet.")
        sys.exit(1)
    dolphinCurVer = dolphinBS.find('a', attrs={'class':"btn-info"})['href']
    dolphinCurVer = re.findall(r"dolphin-master-(.*)-x64.7z", dolphinCurVer).pop()
    return dolphinCurVer
def genlink(version):

    final = "http://dl.dolphin-emu.org/builds/dolphin-master-{}-x64.7z".format(version)
    try:
        urlopen(final)
    except HTTPError:
        print("ERROR: Cannot resolve download URL.")
        sys.exit(2)
    return final

def download(link):
    file_name = link.split('/')[-1]
    u = urlopen(link)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta["Content-Length"])
    file_sizeMB = file_size/1024.0/1024.0
    print("Downloading: {0} filesize: {1:.2f}MB".format(file_name, file_sizeMB))
    file_size_dl = 0
    block_sz = 1024
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        file_size_dl += len(buffer)
        f.write(buffer)
        p = float(file_size_dl) / file_size
        status = r"{0:.2f}MB/{2:.2f}MB [{1:.2%}]".format(file_size_dl/1024.0/1024.0, p, file_sizeMB)
        status = status + chr(8)*(len(status)+1)
        sys.stdout.write(status)
    print()
    f.close()
    return file_name

def extract(zipped):
    cmd = ['7za', 'x', '-y', zipped]
    try:
    	sp = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    except FileNotFoundError:
        print("ERROR: Cannot find '7za.exe'.")
        exit(3)
    while sp.poll() is None:
        time.sleep(0.1)
    return True

def main():
    os.chdir(".")

    os.system('cls' if os.name == 'nt' else 'clear')
    print("Dolphin Downloader v1.1.1")
    print("Retrieving most recent Dolphin development version...")
    dolphinCurVer = getversion()

    print("\nMost recent version is %s." % dolphinCurVer)

    try:
        versionfile = open("Dolphin/version.txt", "r")
        versiontext = versionfile.readline()
        versionfile.close()
        if versiontext >= dolphinCurVer:
            old = False
        else:
            old = True
    except FileNotFoundError:
        old = True

    if not old:
        print("Dolphin is up to date!")
    else:
        linked = genlink(dolphinCurVer)
        print("Downloading most recent version now... (please wait a bit)\n")
        dolphinzip = download(linked)
        print("\nExtracting Dolphin package...")

        extract(dolphinzip)

        print("\nCleaning up...")
        os.remove(dolphinzip)
        try:
            shutil.rmtree('Dolphin')
        except FileNotFoundError:
            pass
        os.rename("Dolphin-x64", "Dolphin")
        versionfile = open("Dolphin/version.txt", "w")
        versionfile.write(dolphinCurVer)
        versionfile.close()

        print("\nDone!")

if __name__ == "__main__":
    main()
