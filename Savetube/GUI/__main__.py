import tkinter as tk
from tkinter import ttk
import re
import subprocess
import threading
from tkinter.filedialog import askdirectory

try:
    from PIL import Image # noqa
    from PIL import ImageTk # noqa
except ImportError:
    subprocess.call('pip3 install Pillow', shell=True)
import io
from urllib.request import urlopen
from tkinter import messagebox
import youtube_dl.postprocessor as ytpp
from Savetube.ffmpeg import GetFFmpeg
from Savetube.GUI.loadinganim import Loading
from Savetube.GUI.scrollableframe import ScrollableFrame
from Savetube.youtubedltojson import YoutubedlTojson
from Savetube.GUI.downloadvideo import DownloadVideo
from Savetube.GUI.updater import downloadupdate
import os
import webbrowser
import sys


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


class DownloadDetails:

    def __init__(self, url, title, vformat, ext, op, subs, ):
        self.url = url
        self.title = title
        self.vformat = vformat
        self.ext = ext
        self.op = op
        self.subs = subs
        self.progress = ttk.Progressbar()
        self.master = tk.Frame()
        self.size = tk.Label()
        self.rate = tk.Label()
        self.eta = tk.Label()
        self.window = None

    def gettitle(self):
        return self.title

    def Downloadfile(self):
        # def startd():
        DownloadVideo(self.window, self.url, self.op, self.vformat, self.ext, self.subs, self.updateStatus)

        # threading.Thread(target=startd).start()

    def downloadView(self, master, window):
        self.master = master
        self.window = window
        df = tk.Frame(master, bd=5, height=40, width=900)
        df.pack()
        titlet = tk.Label(df, text=self.title, anchor="w")
        # self.downloadprocess = tk.Label(df, text="00% of size at 0Kib/s ETA ")
        self.size = tk.Label(df, text="unknown")
        self.rate = tk.Label(df, text="0.0KiB/s")
        self.eta = tk.Label(df, text="99:99")
        self.progress = ttk.Progressbar(df, orient=tk.HORIZONTAL, mode='determinate')
        titlet.place(relwidth=0.40)
        self.progress.place(relx=0.42, relwidth=0.15)
        self.size.place(relx=0.65)
        self.rate.place(relx=0.75)
        self.eta.place(relx=0.85)
        # self.downloadprocess.place(relx=0.7, relwidth=0.3)
        # df.pack()
        # self.Downloadfile()

    def updateStatus(self, status):
        # self.downloadprocess['text'] = status
        # self.master.update()
        print("{}".format(status).strip())
        if "{}".format(status).strip()[0:2].isdigit():
            # self.downloadprocess['text'] = status
            # self.master.update()
            per = "{}".format(status)[2:6]
            rate = re.findall("at ([^ ]*)", "{}".format(status))
            size = re.findall("of ([^ ]*)", "{}".format(status))
            eta = re.findall("ETA ([^\']*)", "{}".format(status))
            if per != "00% ":
                self.progress['value'] = int(float(per))
            else:
                self.progress['value'] = 100
            try:
                self.size['text'] = size[0]
                self.rate['text'] = rate[0]
                self.eta['text'] = eta[0]
            except IndexError:
                self.rate['text'] = "0.0KiB/s"
            self.master.update()


class App:

    def __init__(self, master):
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        # self.master.mainloop()
        self.loading = None
        self.iswindowGenerated = 0

        # Icon and title
        self.icon = tk.PhotoImage(file=os.path.dirname(os.path.abspath(__file__)) + "/icon.png")
        self.master.iconphoto(False, self.icon)
        self.master.title("SaveTube")

        # Gets the requested values of the height and widht.
        self.windowWidth = self.master.winfo_reqwidth()
        self.windowHeight = self.master.winfo_reqheight()

        # Gets both half the screen width/height and window width/height
        self.positionRight = int(self.master.winfo_screenwidth() / 2 - self.windowWidth / 2)
        self.positionDown = int(self.master.winfo_screenheight() / 2 - self.windowHeight / 2)

        # Positions the window in the center of the page.
        self.master.geometry("+{}+{}".format(self.positionRight, self.positionDown))

        # root.geometry("320x80")
        # self.master.overrideredirect(True)

        # self.progress = Progressbar(master, orient=HORIZONTAL,
        #                             length=400, mode='indeterminate')
        self.url = tk.Entry(self.master, width=50, bd=5)
        # self.url.insert(0, "{}".format(self.getClipboardText()))
        self.url.grid(row=2, column=0, pady=2)

        self.btn = tk.Button(self.master, text="Go", bg="red", fg="white", pady=2, command=self.bar, width=10,
                             activebackground="green",
                             activeforeground="white")
        self.btn.grid(row=2, column=1, pady=2)

        self.dtext = tk.StringVar()
        self.dtext.set("Click to download")
        self.downloadprocess = tk.Label(self.master, text="Click to download......", relief=tk.SUNKEN, anchor=tk.W)

        self.vtitle = tk.StringVar()

        # frames of master
        self.topframe = tk.Frame(self.master, pady=5, padx=2, bd=5, height=300)
        self.bottomframe = tk.Frame(self.master, pady=5, padx=2, bd=5, height=300)

        # Dictionary
        self.videos = {}

        # Queue
        self.scrollF = tk.Frame(self.bottomframe)
        self.scrollb = tk.Scrollbar(self.scrollF)
        self.scrollb.pack(side=tk.RIGHT, fill=tk.Y)
        self.queue = tk.Listbox(self.scrollF, selectmode='multiple')

        # Radiobox
        self.subs = tk.IntVar()

        # resolution
        # Create a Tkinter variable
        self.defaultheight = tk.StringVar(self.master)

        # Dictionary with options
        # self.defaultheight.set('720')  # set the default option
        self.heights = ttk.Combobox(self.topframe, textvariable=self.defaultheight)
        self.heights.config(width=30)

        # formats
        # Create a Tkinter variable
        self.defaultformat = tk.StringVar(self.master)

        # Dictionary with options
        self.formats = ttk.Combobox(self.topframe, textvariable=self.defaultformat)
        self.formats.config(width=30)

        # folder chooser
        self.chosenfolder = tk.StringVar(self.master)
        self.chosenfolder.set("{}".format(get_download_path()))
        self.folder_choser_frame = tk.Frame(self.bottomframe)
        self.folder = tk.Entry(self.folder_choser_frame, textvariable=self.chosenfolder, width=30)
        self.folderchoser = tk.Button(self.folder_choser_frame, text="...", command=self.pickfolder)

        # style
        self.styleb = ttk.Style()
        self.styleb.configure('W.TButton', font=('calibri', 10, 'bold', 'underline'), foreground='red')
        self.styleb.map('W.TButton', foreground=[('active', '!disabled', 'green')], background=[('active', 'black')])

        # add Button
        self.addbutton = ttk.Button(self.topframe, text="Add To List", style="W.TButton", command=self.addtask)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.master.destroy()
            sys.exit(0)

    def bar(self, vurl=None):
        # self.master.overrideredirect(False)
        if vurl is None:
            vurl = self.url.get();
        self.master.geometry("900x600+280+80")
        self.master.resizable(0, 0)
        self.btn.grid_forget()
        self.url.grid_forget()

        # self.loading = Loading(self.master)
        # self.loading.show()
        # root.geometry("320x480")
        # self.progress.pack()
        # self.progress.start()

        def linkTojson():
            self.loading = Loading(self.master)
            self.loading.show()
            jsonp = YoutubedlTojson(vurl)
            imgurl = jsonp.getImgurl()
            title = jsonp.getTitle()
            self.vtitle = title
            site = jsonp.getExtractor()
            description = jsonp.getDescription()
            uploader = jsonp.getUploader()
            formatsh = jsonp.getFormatsHeight()
            formatse = jsonp.getFormatsExt()
            if isinstance(formatsh, tuple):
                self.defaultheight.set(formatsh[1])
            else:
                self.defaultheight.set(formatsh)
            self.defaultformat.set(formatse[1])
            self.formats['values'] = jsonp.getFormatsExt()
            self.heights['values'] = jsonp.getFormatsHeight()
            # self.progress.stop()
            # self.progress.pack_forget()
            self.mainWindow(imgurl, title, uploader, description, site)
            # self.setTopframe(imgurl, title)
            # self.setBottom()

        threading.Thread(target=linkTojson).start()

    def pickfolder(self):
        print("youtube-dl-tkinter: Choosing File Destination")
        tk.Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
        filename = askdirectory()  # show an "Open" dialog box and return the path to the selected file
        print(filename)
        self.chosenfolder.set(filename)

    def addtask(self):
        video_converter = ytpp.FFmpegPostProcessor.get_versions()
        if not (video_converter['ffmpeg'] or video_converter['avconv']):
            if messagebox.askokcancel("FFmpeg", "FFmpeg needed download now?"):
                self.getFFmpeg()

        print("youtube-dl-tkinter: Youtube Url Added to queue!")
        listitem = "{}.      {}".format(self.queue.size() + 1, self.vtitle)
        ddetails = DownloadDetails(self.url.get(), self.vtitle, self.heights.get(), self.formats.get(),
                                   self.chosenfolder.get(), self.subs.get())
        self.videos[listitem] = ddetails
        self.queue.insert(tk.END, listitem)
        self.master.update()

    def mainWindow(self, imgurl, title, uploader, description, site):
        # ***** Main Menu *****

        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        subMenu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label="File", menu=subMenu)
        subMenu.add_command(label="Add task", command=self.addNewUrl)
        subMenu.add_command(label="New...", command=self.doNothing)
        subMenu.add_separator()
        subMenu.add_command(label="Exit", command=lambda: sys.exit(0))

        editMenu = tk.Menu(menu, tearoff=False)
        menu.add_cascade(label="Edit", menu=editMenu)
        editMenu.add_command(label="Help", command=self.help)

        # ***** The Toolbar *****

        # toolbar = Frame(root)
        #
        # insertButt = Button(toolbar, text="Insert Image", command=doNothing)
        # insertButt.pack(side=LEFT, padx=2, pady=2)
        # printButt = Button(toolbar, text="Print", command=doNothing)
        # printButt.pack(side=LEFT, padx=2, pady=2)
        #
        # toolbar.pack(side=TOP, fill=X)

        # ***** Status Bar *****

        # status = Label(root, text="Preparing to do nothing...", relief=SUNKEN, anchor=W)
        self.downloadprocess.pack(side=tk.BOTTOM, fill=tk.X)
        self.master.geometry("900x600+280+80")
        self.master.resizable(0, 0)
        self.topframe.pack(fill=tk.X)
        self.bottomframe.pack(fill=tk.X)
        self.setTopframe(imgurl, title, uploader, description, site)
        if not self.iswindowGenerated:
            self.setBottom()
        self.iswindowGenerated = 1
        self.loading.stop()
        self.updater()

    def setTopframe(self, imgurl, title, uploader, description, site):
        fin = urlopen(imgurl)
        # read into a memory stream
        s = io.BytesIO(fin.read())
        pil_image = Image.open(s)
        newsize = (360, 240)
        pil_image = pil_image.resize(newsize)
        # convert PIL image to something Tkinter can handle
        tk_image = ImageTk.PhotoImage(pil_image)
        label = tk.Label(self.topframe, image=tk_image, width=pil_image.width, height=pil_image.height)
        label.image = tk_image
        titlelabel = tk.Message(self.topframe, text=title, relief=tk.RIDGE, width=500, bg="red", fg="white")
        uploaderlabel = tk.Label(self.topframe, text="Uploaded by: {}".format(uploader))
        sitelabel = tk.Label(self.topframe, text="Site: {}".format(site))
        subtitle = tk.Label(self.topframe, text="With Subtitles (if available)")
        subyes = tk.Radiobutton(self.topframe, text="Yes", value=1, variable=self.subs)
        subno = tk.Radiobutton(self.topframe, text="No", value=0, variable=self.subs)
        # descriptionlabel = tk.Label(self.topframe, text=description)
        # label.pack()
        # titlelabel.pack()
        label.place(x=0, y=0)
        titlelabel.place(x=380, y=0)
        uploaderlabel.place(x=380, y=40)
        sitelabel.place(x=380, y=80)
        subtitle.place(x=380, y=120)
        subyes.place(x=380, y=140)
        subno.place(x=380, y=160)
        self.heights.place(x=30, y=260)
        self.formats.place(x=300, y=260)
        self.addbutton.place(x=580, y=260)
        # descriptionlabel.place(x=280, y=80)

        # self.topframe.pack(side=TOP, fill=X)

    def setBottom(self):
        toplabel = tk.Label(self.bottomframe, text="No.         Title", anchor="w")
        dbtn = tk.Button(self.bottomframe, text="Download", fg="green", command=self.download)
        dbtn.place(x=750, y=225)
        img = ImageTk.PhotoImage(Image.open(os.path.dirname(os.path.abspath(__file__)) + "/folder.png"))
        folderimg = tk.Label(self.bottomframe, image=img)
        folderimg.image = img
        toplabel.place(x=0, y=0, relwidth=1)
        self.scrollF.place(x=0, y=20, relwidth=1, relheight=0.7)
        self.queue.place(relwidth=0.98, relheight=1)
        # attach listbox to scrollbar
        self.queue.config(yscrollcommand=self.scrollb.set)
        self.scrollb.config(command=self.queue.yview)
        # self.queue.insert(END, "No.         Title")
        folderimg.place(x=20, y=220)
        self.folder.pack(side=tk.LEFT)
        self.folderchoser.pack(side=tk.LEFT)
        self.folder_choser_frame.place(x=60, y=228)
        # self.folderchoser.place(x=(s+30), y=225)

        # self.bottomframe.pack(side=BOTTOM, fill=X)

    def download(self):
        # vv = self.videos[self.queue.get(self.queue.curselection())]
        if len(self.queue.curselection()) == 0:
            messagebox.showwarning("Warning", "Please add at least one video to list.")
        else:
            dwindow = tk.Toplevel(self.master)
            dwindow.geometry("900x600+280+80")
            dwindow.iconphoto(False, self.icon)
            dwindow.grab_set()
            dwindow.focus_force()
            lframe = tk.Frame(dwindow, height=20)
            lframe.pack(fill=tk.X)
            titleText = tk.Label(lframe, text="TITLE")
            processText = tk.Label(lframe, text="PROCESS")
            sizeText = tk.Label(lframe, text="SIZE")
            rateText = tk.Label(lframe, text="RATE")
            timeText = tk.Label(lframe, text="TIME REMAINING")
            titleText.place(relx=0.02)
            processText.place(relx=0.42)
            sizeText.place(relx=0.65)
            rateText.place(relx=0.75)
            timeText.place(relx=0.85)
            scrollframe = ScrollableFrame(dwindow)
            scrollframe.pack(fill=tk.BOTH)

            def flash(event):
                dwindow.bell()
                dwindow.focus_force()
                dwindow.lift()
                # number_of_flashes = 5
                # flash_time = 80
                # info = FLASHWINFO(0,
                #                   windll.user32.GetForegroundWindow(),
                #                   win32con.FLASHW_ALL,
                #                   number_of_flashes,
                #                   flash_time)
                # info.cbSize = sizeof(info)
                # windll.user32.FlashWindowEx(byref(info))

            dwindow.bind("<FocusOut>", flash)
            for i in self.queue.curselection():
                self.videos[self.queue.get(i)].downloadView(scrollframe.scrollable_frame, dwindow)

            def startD():
                for v in self.queue.curselection():
                    self.videos[self.queue.get(v)].Downloadfile()

            threading.Thread(target=startD).start()

    def updateStatus(self, status):
        self.downloadprocess['text'] = status
        self.master.update()
        if "{}".format(status)[2:4].isdigit():
            print("{}".format(status)[2:6])
            print(re.findall("at ([^ ]*)", "{}".format(status)))
            print(re.findall("ETA ([^\']*)", "{}".format(status)))
            # print("{}".format(status)[25:35])
            # print("{}".format(status)[36:45])

    def doNothing(self):
        Loading(self.master)

    # def getClipboardText(self):
    #     win32clipboard.OpenClipboard()
    #     data = win32clipboard.GetClipboardData()
    #     win32clipboard.CloseClipboard()
    #     return data

    def getFFmpeg(self):

        def flash(event):
            dwindow.bell()
            dwindow.focus_force()

        if os.name == 'nt':
            dwindow = tk.Toplevel(self.master)
            dwindow.title("Downloading FFmpeg......")
            dwindow.iconphoto(False, self.icon)
            dwindow.bind("<FocusOut>", flash)
            # Gets both half the screen width/height and window width/height
            positionRight = int(self.master.winfo_screenwidth() / 2 - 150)
            positionDown = int(self.master.winfo_screenheight() / 2)
            dwindow.protocol("WM_DELETE_WINDOW", lambda: "pass")
            dwindow.geometry("300x60+{}+{}".format(positionRight, positionDown))
            dwindow.grab_set()
            dwindow.focus_force()
            progress = ttk.Progressbar(dwindow, orient=tk.HORIZONTAL, mode='determinate', length=200)
            progress.pack(pady=20)

        def updatestatus(status):
            progress['value'] = int(status)
            dwindow.update()

        def onComplete():
            dwindow.protocol("WM_DELETE_WINDOW", lambda: dwindow.destroy())
            dwindow.destroy()

        def start_downloading():
            GetFFmpeg(updatestatus, onComplete)

        threading.Thread(target=start_downloading).start()

    def addNewUrl(self):
        dwindow = tk.Toplevel(self.master)
        dwindow.iconphoto(False, self.icon)
        dwindow.geometry("+{}+{}".format((self.master.winfo_x() + dwindow.winfo_reqwidth()),
                                         (self.master.winfo_y() + int(self.master.winfo_reqheight() / 2))))
        dwindow.focus_force()
        dwindow.grab_set()
        addurl = tk.Entry(dwindow, width=50, bd=5)
        # addurl.insert(0, "{}".format(self.getClipboardText()))
        self.url.insert(0, "{}".format(addurl.get()))
        addurl.grid(row=2, column=0, pady=10, padx=5)

        def remove():
            self.bar(addurl.get())
            dwindow.destroy()

        addbtn = tk.Button(dwindow, text="Go", bg="red", fg="white", pady=10, padx=5, command=remove, width=10,
                           activebackground="green",
                           activeforeground="white")
        addbtn.grid(row=2, column=1, pady=2)

        def flash(event):
            dwindow.bell()
            dwindow.focus_force()
            dwindow.lift()
            # number_of_flashes = 5
            # flash_time = 80
            # info = FLASHWINFO(0,
            #                   windll.user32.GetForegroundWindow(),
            #                   win32con.FLASHW_ALL,
            #                   number_of_flashes,
            #                   flash_time)
            # info.cbSize = sizeof(info)
            # windll.user32.FlashWindowEx(byref(info))

        dwindow.bind("<FocusOut>", flash)

    @staticmethod
    def help():
        webbrowser.open('https://github.com/bawaviki/savetube', new=2)

    def updater(self):
        threading.Thread(target=downloadupdate(self.master)).start()
