from urllib.request import urlopen
import urllib.request
import os
import sys


class GetFFmpeg:

    def __init__(self, status, completed):
        self.status = status
        self.completed = completed
        if os.name == 'nt':
            self.download_ffmpeg_windows()
        else:
            self.download_ffmpeg_debian()

    @staticmethod
    def download_ffmpeg_debian():
        os.system("apt-get install ffmpeg -y")

    def download_ffmpeg_windows(self):
        with open(os.path.dirname(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..",".."))) + "/ffmpeg.exe", "wb") as f:
            response = urlopen("https://github.com/bawaviki/static-files/raw/master/ffmpeg.exe")
            data_read = self.chunk_read(response, report_hook=self.chunk_report)
            f.write(data_read)

    def chunk_read(self, response, chunk_size=8192, report_hook=None):
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

    def chunk_report(self, bytes_so_far, chunk_size, total_size):
        percent = float(bytes_so_far) / total_size
        percent = round(percent * 100, 2)
        if self.status != None:
            self.status(percent)
        os.system('cls')
        sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" %
                         (bytes_so_far, total_size, percent))

        if bytes_so_far >= total_size:
            sys.stdout.write('\n')
            if self.completed != None:
                self.completed()
            # self.dwindow.protocol("WM_DELETE_WINDOW", lambda: self.dwindow.destroy())
