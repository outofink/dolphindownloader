from bs4 import BeautifulSoup as BS
import sys, getopt, zipfile, re, shutil
import subprocess, time
from os import system, name, path, remove, rename

import urllib.request, urllib.error
urlopen   = urllib.request.urlopen
Request   = urllib.request.Request
HTTPError =	urllib.error.HTTPError
URLError  = urllib.error.URLError

class DolphinDownloader():
	def __init__(self, argv):
		self.main(argv)

	def main(self, argv):
		system('cls' if name == 'nt' else 'clear')
		print("Dolphin Downloader v1.0")
		print("Retrieving most recent Dolphin development version...")
		dolphinCurVer = self.getversion()
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
			linked = self.genlink(dolphinCurVer)
			print("Downloading most recent version now... (please wait a bit)\n")
			dolphinzip=self.download(linked)
			print("\nExtracting Dolphin package...")
			#other stuff
			self.extract(dolphinzip)

			print("\nCleaning up...")
			remove(dolphinzip)
			try:
				shutil.rmtree('Dolphin')
			except:
				pass
			rename("Dolphin-x64", "Dolphin")
			versionfile = open("Dolphin/version.txt", "w")
			versionfile.write(dolphinCurVer)
			versionfile.close()

			print("\nDone!")

	def getversion(self):
		try:
			dolphin_html = BS(urlopen(Request('https://dolphin-emu.org/')).read(), "html.parser")
		except URLError:
			print("\nERROR: Not connected to the internet.")
			sys.exit(1)
		dolphinCurVer = dolphin_html.find('a', attrs={'class':"btn btn-primary btn-lg"}).text
		dolphinCurVer = re.findall(r' Download Dolphin (.*) for Windows, Mac and Linux', dolphinCurVer).pop()
		return dolphinCurVer
	def genlink(self, version):

		final="http://dl.dolphin-emu.org/builds/dolphin-master-{}-x64.7z".format(version)
		try:
			u = urlopen(final)
		except HTTPError:
			print("ERROR: Dolphin version does not exist.\nNote: Dolphin Downloader only supports Dolphin 2.57+")
			return False
		return final	
	def download(self, link):
		file_name = link.split('/')[-1]
		u = urlopen(link)
		f = open(file_name, 'wb')
		meta = u.info()
		file_size = int(meta["Content-Length"])
		file_sizeMB=file_size/1024.0/1024.0
		print("Downloading: {0} filesize: {1:.4}MB".format(file_name, file_sizeMB))
		file_size_dl = 0
		block_sz = 1024
		while True:
		    buffer = u.read(block_sz)
		    if not buffer:
		        break
		    file_size_dl += len(buffer)
		    f.write(buffer)
		    p = float(file_size_dl) / file_size
		    status = r"{0:.2f}MB/{2:.2f}MB [{1:.2%}]       ".format(file_size_dl/1024.0/1024.0, p, file_sizeMB)
		    status = status + chr(8)*(len(status)+1)
		    sys.stdout.write(status)
		print()
		f.close()
		return file_name
	def extract(self, zipped):
		cmd = ['7za', 'x', '-y', zipped]
		sp = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)

		while sp.poll() is None:
			time.sleep(0.1)

		return True
		

if __name__ == "__main__":
	DolphinDownloader(sys.argv[1:])
