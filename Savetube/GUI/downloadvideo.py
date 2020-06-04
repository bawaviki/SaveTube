from subprocess import Popen, PIPE


class DownloadVideo:
    def __init__(self, master, videourl, destination, height, vformat, subs, func):
        print("youtube-dl-tkinter: Initializing download of url {} to destination {} of height {} in format {}".format(
            videourl, destination, height, vformat))
        if subs == "yes":
            subs = "--all-subs --write-auto-sub"
        else:
            subs = ""
        if vformat == "mp3":
            shellcmd = "youtube-dl --newline -o \"{}/%(title)s.%(ext)s\" -x --audio-format mp3 {}".format(destination,
                                                                                                          videourl)
        elif vformat == "m4a":
            shellcmd = "youtube-dl --newline -o \"{}/%(title)s.%(ext)s\" -f \"bestaudio[ext={}]\" {}".format(
                destination, vformat, videourl)
        else:
            if "{}".format(height).isdigit():
                if vformat == "mp4":
                    shellcmd = "youtube-dl --newline -o \"{}/%(title)s.%(ext)s\" {} -f \"bestvideo[height<={}][ext={}]+bestaudio[ext=m4a]/best\" {}".format(
                        destination, subs, height, vformat, videourl)
                else:
                    shellcmd = "youtube-dl --newline -o \"{}/%(title)s.%(ext)s\" {} -f \"bestvideo[height<={}][ext={}]+bestaudio/best\" {}".format(
                        destination, subs, height, vformat, videourl)
            else:
                shellcmd = "youtube-dl --newline -o \"{}/%(title)s.%(ext)s\" {} -f \"bestvideo[ext={}]+bestaudio/best\" {}".format(
                    destination, subs, vformat, videourl)

        self.status = "Downloading start"

        for path in self.run(master, shellcmd):
            func("{}".format(path)[10:None])
            print(path[10:None])

    def run(self, master, command):
        process = Popen(command, stdout=PIPE, shell=True, stderr=PIPE, universal_newlines=True)
        while True:
            line = process.stdout.readline().rstrip()
            if not line:
                break
            yield line

        def temin():
            process.terminate()
            master.destroy()

        master.protocol("WM_DELETE_WINDOW", temin)

    def getCommandResult(self):
        return self.status
