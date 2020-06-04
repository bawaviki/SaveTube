import threading
from Savetube.youtubedltojson import YoutubedlTojson
import os
import itertools
import sys
import time
import getopt
import pyfiglet
from pyfiglet import Figlet
from termcolor import colored, cprint
import youtube_dl.postprocessor as ytpp
from Savetube.ffmpeg import GetFFmpeg
from Savetube.version import __version__


def get_download_path():
    """Returns the default downloads path for linux or windows"""
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'Downloads')


class CliApp:

    def __init__(self, url):
        self.done = False
        self.video_converter = ytpp.FFmpegPostProcessor.get_versions()

        def getJson():
            self.loadingStart()
            y2j = YoutubedlTojson(url)
            self.done = True
            self.clearTerminal()
            if not (self.video_converter['ffmpeg'] or self.video_converter['avconv']):
                f = input("ffmpeg is needed to work properly download now (y/n): ")
                if f == "y":
                    GetFFmpeg(None, None)
            self.clearTerminal()
            self.intro()
            cprint("\nTitle: {}\n".format(y2j.getTitle()), 'blue', attrs=['bold'])

            ext = int(self.getAnswer(y2j.getFormatsExt()))
            self.clearTerminal()

            if y2j.getFormatsExt()[(ext - 1)] == "mp3":
                os.system("youtube-dl --rm-cache-dir")
                os.system(
                    "youtube-dl -o \"{}/%(title)s.%(ext)s\" -x --audio-format mp3 {}".format(get_download_path(), url))

            elif y2j.getFormatsExt()[(ext - 1)] == "m4a":
                os.system("youtube-dl --rm-cache-dir")
                os.system("youtube-dl -o \"{}/%(title)s.%(ext)s\" -f \"bestaudio[ext={}]\" {}".format(
                    get_download_path(), "m4a", url))

            else:
                height = int(self.getAnswer(y2j.getFormatsHeight()))
                self.clearTerminal()

                sub = input("Download with Subtitles (if Available) y/n: ")
                out = get_download_path()

                if sub == "y":
                    sub = "--all-subs --write-auto-sub"
                else:
                    sub = ""

                os.system("youtube-dl --rm-cache-dir")
                os.system(
                    "youtube-dl  -o \"{}/%(title)s.%(ext)s\" {} -f \"bestvideo[height<={}][ext={}]+bestaudio/best\" {}".format(
                        out, sub, y2j.getFormatsHeight()[(height - 1)], y2j.getFormatsExt()[(ext - 1)], url))

        threading.Thread(target=getJson).start()

    def animate(self):
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if self.done:
                break
            sys.stdout.write('\rloading ' + c)
            sys.stdout.flush()
            time.sleep(0.1)
        # sys.stdout.write('\rDone!     ')

    def loadingStart(self):
        self.done = False
        t = threading.Thread(target=self.animate)
        t.start()

    def getAnswer(self, option):
        op = 1
        for f in option:
            cprint(" {}.    {}".format(op, f), 'white', 'on_grey')
            op = op + 1
        cprint(" x.    Exit ", 'white', 'on_grey', attrs=['bold'])
        ans = input(colored("\nEnter your choise: ", 'yellow'))
        if ans == 'x':
            sys.exit(0)
        if int(ans) in range(1, op):
            return ans
        else:
            print(colored("\nPlease chose wisely\n", 'red'))
            self.getAnswer(option)

    @staticmethod
    def clearTerminal():
        os.system('cls' if os.name == 'nt' else 'clear')

    def intro(self):

        f = Figlet(font='slant')
        pyfiglet.figlet_format(" SaveTube", font="banner")
        cprint(f.renderText(" SaveTube"), 'white', 'on_red', attrs=['bold'])

        print(colored("ffmpeg_version: {}".format(self.video_converter['ffmpeg']),
                      'green' if self.video_converter['ffmpeg'] else 'red'), end="\t\t")
        print(colored("avconv_version: {}".format(self.video_converter['avconv']),
                      'green' if self.video_converter['avconv'] else 'red'), end="\t\t")
        cprint("by: bawaviki", 'white', 'on_grey', attrs=['blink', 'bold'])

# flake8: noqa: C901
def main(args=None):
    args = sys.argv[1:]
    url = ''
    has_op = False
    try:
        opts, args = getopt.getopt(args, "vhU:", ["url", "version", "help"])
    except getopt.GetoptError:
        print(
            " Incorrect option!\n usage: savetube [-h :help] [-v, --version :version] [-U <url>] [--url <url>] for GUI mode just type savetube and hit enter.")
        sys.exit()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            has_op = True
            print(
                " usage: savetube [-h :help] [-v, --version :version] [-U <url>] [--url <url>] for GUI mode just type savetube and hit enter.")
            sys.exit()
        elif opt in ("-v", "--version"):
            has_op = True
            print("Current version: {}".format(__version__))
            sys.exit()
        elif opt in ("-U", "--url"):
            has_op = True
            url = arg
            os.system('cls' if os.name == 'nt' else 'clear')
            print(colored("Url is {}".format(url), 'cyan'))

    if has_op:

        if url == '':
            print("Please add an url first i.e --url <url> or -h for help")
            sys.exit(0)

        CliApp(url)

    else:
        try:
            import tkinter as tk
        except ImportError:
            os.system("savetube -h")
            sys.exit()

        try:
            from PIL import Image # noqa
            from PIL import ImageTk # noqa
        except ModuleNotFoundError:
            import subprocess
            print("Downloading the require module")
            subprocess.call('pip3 install Pillow', shell=True)
            print("Restarting the app now")
            os.system("savetube")
            sys.exit()

        from Savetube.GUI.__main__ import App

        root = tk.Tk()
        App(root)
        root.mainloop()


if __name__ == "__main__":
    main()
