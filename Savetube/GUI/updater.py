from urllib.request import urlopen
import urllib.request
import json
from subprocess import PIPE, Popen
import subprocess
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
import sys
from Savetube.GUI.loadinganim import Loading
import os


def getnewversion():
    with urllib.request.urlopen("https://api.github.com/repos/bawaviki/youtubedl-lazy/releases/latest") as url:
        data = json.loads(url.read().decode())
        return data['tag_name']


def getcurrentversion():
    result = subprocess.check_output("youtube-dl --version", shell=True, stderr=PIPE, universal_newlines=True)
    return result.rstrip()


def downloadupdate(master):
    if getcurrentversion() != getnewversion():
        if messagebox.askokcancel("Update Available", "Download update now !"):
            dw = downloadwindow(master)
            with open(os.path.dirname(os.path.abspath(__file__)) + "/youtube-dl.exe", "wb") as f:
                response = urlopen("https://youtube-dl.org/downloads/latest/youtube-dl.exe")
                data_read = chunk_read(response, report_hook=dw.chunk_report)
                f.write(data_read)
            # print("Update successfuly")
    else:
        print("Already updated")


class downloadwindow:
    def __init__(self, master):
        self.master = master
        self.progress = ttk.Progressbar()
        self.dwindow = tk.Frame()
        self.showWindow()

    def showWindow(self):
        self.dwindow = tk.Toplevel(self.master)
        self.dwindow.title("Downloading......")

        # Gets both half the screen width/height and window width/height
        positionRight = int(self.master.winfo_screenwidth() / 2 - 150)
        positionDown = int(self.master.winfo_screenheight() / 2)

        self.dwindow.geometry("300x60+{}+{}".format(positionRight, positionDown))
        self.dwindow.grab_set()
        self.dwindow.focus_force()
        self.progress = ttk.Progressbar(self.dwindow, orient=tk.HORIZONTAL, mode='determinate', length=200)
        self.progress.pack(pady=20)

        # def flash(event):
        #     self.dwindow.bell()
        #     self.dwindow.focus_force()
        #     number_of_flashes = 5
        #     flash_time = 80
        #     info = FLASHWINFO(0,
        #                       windll.user32.GetForegroundWindow(),
        #                       win32con.FLASHW_ALL,
        #                       number_of_flashes,
        #                       flash_time)
        #     info.cbSize = sizeof(info)
        #     windll.user32.FlashWindowEx(byref(info))

        # self.dwindow.bind("<FocusOut>", flash)
        self.dwindow.protocol("WM_DELETE_WINDOW", lambda: "pass")

    def updatestatus(self, status):
        self.progress['value'] = int(status)
        self.dwindow.update()

    def chunk_report(self, bytes_so_far, chunk_size, total_size):
        percent = float(bytes_so_far) / total_size
        percent = round(percent * 100, 2)
        self.updatestatus(percent)
        sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" %
                         (bytes_so_far, total_size, percent))

        if bytes_so_far >= total_size:
            sys.stdout.write('\n')
            self.dwindow.protocol("WM_DELETE_WINDOW", lambda: self.dwindow.destroy())


def chunk_read(response, chunk_size=8192, report_hook=None):
    total_size = response.info().get("Content-Length").strip()
    total_size = int(total_size)
    bytes_so_far = 0
    data = b""

    while 1:
        chunk = response.read(chunk_size)
        bytes_so_far += len(chunk)

        if not chunk:
            break

        if report_hook:
            report_hook(bytes_so_far, chunk_size, total_size)

        data += chunk

    return data
